"""Hybrid KTAS Clinical Knowledge Retriever (Dense + BM25 + RRF + CRAG + Self-RAG).

Replaces full 8,500-token KTAS prompt stuffing with selective top-K clinical retrieval:
1. Clinical Korean tokenization with domain stopword removal & canonical symptom mapping.
2. Sparse Okapi BM25 over pediatric symptom names, categories, and secondary considerations.
3. Dense semantic vector similarity using L2-normalized clinical embeddings.
4. Reciprocal Rank Fusion (RRF, k=60) + clinical symptom-name & vitals reranking.
5. CRAG corrective query expansion when initial fused confidence is low.
6. Self-RAG deterministic grounding verifier validating NACRS codes cleanly.
"""

from __future__ import annotations

import json
import math
import re
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Optional

from app.config import settings
from app.services.llm_gateway import compute_local_embedding, cosine_similarity
from app.services.telemetry import telemetry

# Clinical Korean stopwords & non-diagnostic boilerplate words filtered before retrieval
CLINICAL_STOPWORDS: set[str] = {
    "이내", "이상", "이하", "미만", "시간", "개월", "오늘", "어제", "그제", "아까", "지금",
    "갑자기", "조금", "계속", "자꾸", "너무", "많이", "아이", "아기", "애기", "우리",
    "어디", "가야", "하나요", "어떻게", "해야", "할까요", "있어요", "나요", "해요",
    "정도", "주변", "근처", "병원", "소아과", "약국", "응급실", "있고", "나고", "보여",
    "인데", "때문", "같은", "해서", "상태", "증상", "소아", "정상",
}

# Clinical Korean synonym expansion table for Hybrid Query Expansion & CRAG
CLINICAL_SYNONYMS: dict[str, list[str]] = {
    "열": ["열", "발열", "고열", "감염"],
    "열이": ["열", "발열"],
    "열나": ["열", "발열"],
    "고열": ["열", "발열", "패혈증"],
    "미열": ["열", "발열"],
    "불덩이": ["열", "고열", "발열"],
    "기침": ["기침", "코막힘", "호흡기"],
    "콜록": ["기침", "후두염"],
    "컹컹": ["협착음", "기침", "후두염", "호흡곤란"],
    "콧물": ["코막힘", "기침", "코"],
    "코막": ["코막힘", "기침"],
    "구토": ["구토", "오심", "장폐색"],
    "토": ["구토", "오심"],
    "토했": ["구토", "오심"],
    "분수토": ["구토", "담즙", "뇌압"],
    "설사": ["설사", "탈수", "혈변"],
    "피똥": ["혈변", "직장출혈", "장중첩증"],
    "혈변": ["혈변", "직장출혈"],
    "쌕쌕": ["천명", "호흡곤란", "숨참"],
    "숨": ["호흡곤란", "숨참", "천명", "청색증"],
    "숨차": ["호흡곤란", "숨참", "빈호흡"],
    "청색증": ["청색증", "숨참", "호흡곤란"],
    "경련": ["발작", "열성경련", "떨림", "의식"],
    "경기": ["발작", "열성경련", "떨림"],
    "처짐": ["기면", "의식수준", "무반응"],
    "늘어": ["기면", "의식수준", "무반응"],
    "귀": ["귀통증", "이통", "중이염"],
    "배": ["복통", "배아픔"],
    "복통": ["복통", "장중첩증"],
    "발진": ["발진", "두드러기", "수포", "피부"],
    "화상": ["화상", "열손상", "수포"],
    "머리": ["두부손상", "두부", "뇌진탕"],
    "다쳤": ["외상", "열상", "출혈"],
    "소변": ["배뇨", "탈수", "무뇨"],
    "실신": ["실신", "전실신", "의식"],
}


def _extract_clinical_concepts(text: str) -> list[str]:
    """Extracts normalized clinical trigger terms from noisy guardian input."""
    low = (text or "").lower()
    concepts: list[str] = []
    # Prevent false '열' match inside '해열제'
    sanitized = re.sub(r"해열제", "약물", low)
    # Match multi-char keys first, then careful single-char triggers ('열', '토', '숨', '배', '귀')
    for trig, syns in CLINICAL_SYNONYMS.items():
        if len(trig) == 1:
            pattern = rf"(?<![가-힣a-zA-Z]){re.escape(trig)}|(?<!해)열(?![목가-힣]*제)" if trig == "열" else rf"(?<![가-힣]){re.escape(trig)}"
            if re.search(pattern, sanitized):
                concepts.extend(syns)
        elif trig in sanitized:
            concepts.extend(syns)
    return list(dict.fromkeys(concepts))


def _tokenize_korean_clinical(text: str) -> list[str]:
    """Tokenizes Korean clinical text, dropping addresses/digits/stopwords and adding short stems."""
    clean = re.sub(r"[^a-zA-Z가-힣\s]", " ", (text or "").lower())
    raw_tokens = [t for t in clean.split() if len(t) >= 1]
    tokens: list[str] = []
    for tok in raw_tokens:
        if tok in CLINICAL_STOPWORDS or tok.endswith(("구", "동", "시", "군")) and len(tok) >= 3:
            continue
        tokens.append(tok)
        if len(tok) >= 3:
            for i in range(len(tok) - 1):
                sub = tok[i : i + 2]
                if sub not in CLINICAL_STOPWORDS:
                    tokens.append(sub)
    return tokens


@dataclass
class KtasDocument:
    """Indexed KTAS clinical symptom guideline record."""

    nacrs_code: str
    symptom_name: str
    category: str
    secondary_considerations: list[dict[str, Any]]
    min_ktas_level: int
    max_ktas_level: int
    searchable_text: str
    prompt_line: str
    name_tokens: set[str] = field(default_factory=set)
    tokens: list[str] = field(default_factory=list)
    tf: Counter = field(default_factory=Counter)
    embedding: list[float] = field(default_factory=list)


@dataclass
class KtasRetrievalResult:
    """Result container from Hybrid KTAS Retriever + CRAG."""

    documents: list[tuple[KtasDocument, float]]
    grounded_context: str
    crag_triggered: bool
    top_score: float
    score_margin: float
    latency_ms: float
    compressed_chars: int


class KtasHybridRetriever:
    """In-memory Hybrid Dense + Okapi BM25 + RRF + CRAG retriever over 168 KTAS symptoms."""

    def __init__(self) -> None:
        self._docs: list[KtasDocument] = []
        self._by_code: dict[str, KtasDocument] = {}
        self._idf: dict[str, float] = {}
        self._avgdl: float = 1.0
        self._loaded: bool = False

    def ensure_loaded(self) -> None:
        if self._loaded:
            return
        dataset_path = settings.project_root / "data" / "ktas_pediatric_dataset.json"
        if not dataset_path.exists():
            self._loaded = True
            return

        with open(dataset_path, "r", encoding="utf-8") as f:
            db = json.load(f)

        docs: list[KtasDocument] = []
        df: Counter = Counter()
        total_len = 0

        for item in db.get("symptoms", []):
            code = str(item.get("nacrs_code", "")).strip()
            name = str(item.get("symptom_name", "")).strip()
            cat = str(item.get("category", "")).strip()
            cons = list(item.get("secondary_considerations", []) or [])
            levels = [int(c["level"]) for c in cons if isinstance(c.get("level"), int)]
            min_lvl = min(levels) if levels else 1
            max_lvl = max(levels) if levels else 5

            cons_str = " | ".join(
                f"L{c.get('level')}:{c.get('criteria', '')}" for c in cons
            )
            prompt_line = f"[{code}] {name} ({cat}) ➔ {cons_str}"
            # Repeat symptom name & category to give clinical title stronger term weight
            searchable = f"{name} {name} {cat} " + " ".join(
                str(c.get("criteria", "")) for c in cons
            )
            name_toks = set(_tokenize_korean_clinical(f"{name} {cat}"))
            tokens = _tokenize_korean_clinical(searchable)
            tf = Counter(tokens)
            for t in tf:
                df[t] += 1
            total_len += len(tokens)

            doc = KtasDocument(
                nacrs_code=code,
                symptom_name=name,
                category=cat,
                secondary_considerations=cons,
                min_ktas_level=min_lvl,
                max_ktas_level=max_lvl,
                searchable_text=searchable,
                prompt_line=prompt_line,
                name_tokens=name_toks,
                tokens=tokens,
                tf=tf,
                embedding=compute_local_embedding(f"{name} {cat} " + " ".join(c.get("criteria", "") for c in cons[:4])),
            )
            docs.append(doc)
            if code:
                self._by_code[code] = doc

        n_docs = max(1, len(docs))
        self._avgdl = max(1.0, total_len / n_docs)
        self._idf = {
            tok: math.log(1.0 + (n_docs - freq + 0.5) / (freq + 0.5))
            for tok, freq in df.items()
        }
        self._docs = docs
        self._loaded = True

    def _bm25_scores(self, query_tokens: list[str], k1: float = 1.5, b: float = 0.75) -> list[tuple[int, float]]:
        scores: list[tuple[int, float]] = []
        q_unique = list(dict.fromkeys(query_tokens))
        for idx, doc in enumerate(self._docs):
            dl = max(1, len(doc.tokens))
            s = 0.0
            for qt in q_unique:
                freq = doc.tf.get(qt, 0)
                if freq <= 0:
                    continue
                idf = self._idf.get(qt, 0.5)
                denom = freq + k1 * (1.0 - b + b * (dl / self._avgdl))
                s += idf * ((freq * (k1 + 1.0)) / denom)
            scores.append((idx, s))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def _dense_scores(self, query_vec: list[float]) -> list[tuple[int, float]]:
        scores = [
            (idx, cosine_similarity(query_vec, doc.embedding))
            for idx, doc in enumerate(self._docs)
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def _expand_query_crag(
        self,
        query: str,
        symptoms: Optional[list[str]] = None,
        temperature: Optional[float] = None,
        age_months: Optional[int] = None,
        age_days: Optional[int] = None,
    ) -> str:
        """CRAG corrective query rewriter expanding STT/colloquial expressions to clinical terms."""
        expanded_terms: list[str] = _extract_clinical_concepts(query)
        if symptoms:
            expanded_terms.extend(symptoms)

        if temperature is not None and temperature >= 37.8:
            expanded_terms.extend(["열", "발열", "T≥38°C", "감염"])
        if (age_days is not None and age_days <= 100) or (age_months is not None and age_months <= 3):
            expanded_terms.extend(["<3개월", "영아", "패혈증"])

        if not expanded_terms:
            expanded_terms.append(query)
        else:
            expanded_terms.append(query)
        return " ".join(expanded_terms)

    def _fuse_and_rerank(
        self,
        search_query: str,
        concepts: list[str],
        symptoms: Optional[list[str]] = None,
        temperature: Optional[float] = None,
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> list[tuple[KtasDocument, float]]:
        q_tokens = _tokenize_korean_clinical(" ".join(concepts) + " " + search_query)
        q_vec = compute_local_embedding(" ".join(concepts) if concepts else search_query)

        bm25_ranked = self._bm25_scores(q_tokens)
        dense_ranked = self._dense_scores(q_vec)

        rrf_scores: dict[int, float] = {i: 0.0 for i in range(len(self._docs))}
        for rank, (doc_idx, bscore) in enumerate(bm25_ranked[:30]):
            if bscore > 0.0:
                rrf_scores[doc_idx] += 1.0 / (rrf_k + rank + 1)
        for rank, (doc_idx, dscore) in enumerate(dense_ranked[:30]):
            if dscore > 0.05:
                rrf_scores[doc_idx] += 1.0 / (rrf_k + rank + 1)

        # Clinical Cross-Signal Reranker: exact/canonical symptom_name matches dominate
        concept_set = set(concepts)
        symptom_list = [s.lower() for s in (symptoms or [])]
        for doc_idx, doc in enumerate(self._docs):
            name_low = doc.symptom_name.lower()
            boost = 0.0
            for sym in symptom_list:
                if sym and (sym in name_low or name_low in sym):
                    boost += 0.025
            for c in concept_set:
                if c in doc.name_tokens or (len(c) >= 2 and c in name_low):
                    boost += 0.020
            if (temperature is not None and temperature >= 37.5) or "열" in concept_set or "발열" in concept_set:
                if doc.nacrs_code == "852" or name_low == "열":
                    boost += 0.030
            rrf_scores[doc_idx] += boost

        sorted_idxs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [(self._docs[idx], round(score, 6)) for idx, score in sorted_idxs[:top_k]]

    def retrieve_with_crag(
        self,
        query: str,
        symptoms: Optional[list[str]] = None,
        temperature: Optional[float] = None,
        age_months: Optional[int] = None,
        age_days: Optional[int] = None,
        top_k: int = 5,
        crag_threshold: float = 0.036,
    ) -> KtasRetrievalResult:
        """Runs Hybrid Dense+BM25+RRF retrieval with CRAG automatic query correction."""
        t0 = time.perf_counter()
        self.ensure_loaded()
        if not self._docs:
            return KtasRetrievalResult([], "", False, 0.0, 0.0, 0.0, 0)

        concepts = _extract_clinical_concepts(query)
        if symptoms:
            concepts = list(dict.fromkeys([*concepts, *symptoms]))

        results = self._fuse_and_rerank(
            search_query=query,
            concepts=concepts,
            symptoms=symptoms,
            temperature=temperature,
            top_k=top_k,
        )
        top_score = results[0][1] if results else 0.0
        crag_triggered = False

        # CRAG Corrective Step when no strong symptom-name / clinical concept alignment
        has_name_overlap = bool(
            results and concepts and any(c in results[0][0].name_tokens or c in results[0][0].symptom_name for c in concepts)
        )
        if top_score < crag_threshold or not has_name_overlap:
            crag_triggered = True
            telemetry.inc("rag_crag_rewrite_triggered")
            rewritten = self._expand_query_crag(
                query=query,
                symptoms=symptoms,
                temperature=temperature,
                age_months=age_months,
                age_days=age_days,
            )
            expanded_concepts = list(dict.fromkeys([*concepts, *_extract_clinical_concepts(rewritten)]))
            results = self._fuse_and_rerank(
                search_query=rewritten,
                concepts=expanded_concepts,
                symptoms=symptoms,
                temperature=temperature,
                top_k=top_k,
            )
            top_score = results[0][1] if results else 0.0

        second_score = results[1][1] if len(results) > 1 else 0.0
        score_margin = round(max(0.0, top_score - second_score), 6)
        grounded_context = "\n".join(doc.prompt_line for doc, _ in results)
        latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        telemetry.observe_latency("retriever", latency_ms)
        telemetry.inc("rag_retrievals")

        return KtasRetrievalResult(
            documents=results,
            grounded_context=grounded_context,
            crag_triggered=crag_triggered,
            top_score=top_score,
            score_margin=score_margin,
            latency_ms=latency_ms,
            compressed_chars=len(grounded_context),
        )

    def get_by_nacrs(self, code: Optional[str]) -> Optional[KtasDocument]:
        self.ensure_loaded()
        if not code:
            return None
        return self._by_code.get(str(code).strip())

    def verify_clinical_grounding(
        self,
        ktas_level: Optional[int],
        matched_nacrs_code: Optional[str],
        retrieved: KtasRetrievalResult,
    ) -> dict[str, Any]:
        """Self-RAG deterministic grounding verifier.

        Validates NACRS code existence against official 168 KTAS symptoms (repairing
        hallucinated codes to Top-1 retrieved NACRS) and bounds ktas_level within [1..5]
        without forcibly downgrading valid clinical L4/L5 assessments.
        """
        self.ensure_loaded()
        doc = self.get_by_nacrs(matched_nacrs_code)
        corrected_code = matched_nacrs_code
        corrected_name = doc.symptom_name if doc else None
        grounded = doc is not None

        if not grounded and retrieved.documents:
            top_doc = retrieved.documents[0][0]
            corrected_code = top_doc.nacrs_code
            corrected_name = top_doc.symptom_name
            telemetry.inc("self_rag_nacrs_repaired")

        adjusted_level: Optional[int] = ktas_level
        if adjusted_level is not None:
            adjusted_level = max(1, min(5, int(adjusted_level)))

        return {
            "grounded": grounded,
            "nacrs_code": corrected_code,
            "symptom_name": corrected_name,
            "ktas_level": adjusted_level,
        }


ktas_retriever = KtasHybridRetriever()

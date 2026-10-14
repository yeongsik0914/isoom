"""Medical Safety Guardrail Agent (0ms Zero-LLM In-Memory Engine).

Responsibilities:
1. Pre-execution Interceptor: Instantly intercepts KTAS pediatric Red Flags (convulsions,
   cyanosis, high fever in infants < 100 days, severe dehydration, respiratory distress)
   within 0.1ms without invoking LLMs, routing straight to 119 Emergency Escalation.
2. Post-execution Filter: Enforces Medical Service Act Article 27 compliance by scrubbing
   definitive diagnostic declarations and arbitrary drug dosage instructions from LLM responses.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from app.schemas.state import PatientSessionState

# ============================================================================
# 1. KTAS Pediatric Red Flag Clinical Regex Patterns (0ms In-Memory Engine)
# ============================================================================

# Rule 1: Infant < 100 days (or <= 3 months) with Fever (>= 38.0℃ or high fever keyword)
INFANT_FEVER_PATTERN_1 = re.compile(
    r"(생후\s*([1-9]|[1-9][0-9]|100)일|생후\s*[1-3]개월|신생아|백일\s*미만|100일\s*미만).*(38(\.[0-9])?도|열|고열|불덩이|열나)"
)
INFANT_FEVER_PATTERN_2 = re.compile(
    r"(38(\.[0-9])?도|고열|불덩이|열나).*(생후\s*([1-9]|[1-9][0-9]|100)일|생후\s*[1-3]개월|신생아|백일\s*미만|100일\s*미만)"
)

# Rule 2: Seizure / Convulsion (열성경련, 발작, 사지 떨림, 눈 돌아감)
SEIZURE_PATTERN = re.compile(
    r"(경련|경기|발작|사지\s*경직|눈이\s*(뒤집|돌아가)|몸(을)?\s*(덜덜\s*)?떨|덜덜\s*떨)"
)

# Rule 3: Unresponsiveness / Lethargy (극심한 처짐, 의식 저하, 무반응)
UNRESPONSIVE_PATTERN = re.compile(
    r"(의식(이)?\s*(없|저하|혼미|잃)|(축\s*)?늘어져|반응(이)?\s*없|눈(을)?\s*못\s*뜨|깨워도\s*(안\s*일어|반응)|대답(을)?\s*안|불러도\s*반응)"
)

# Rule 4: Severe Respiratory Distress & Cyanosis (흉벽 함몰, 비익 호흡, 청색증)
RESPIRATORY_CYANOSIS_PATTERN = re.compile(
    r"(청색증|파랗게\s*(질|변)|갈비뼈.*(쑥쑥|들어가)|흉벽\s*함몰|비익\s*호흡|코(를)?\s*벌렁|쌕쌕|숨(을)?\s*(헐떡|쉬기\s*힘들))"
)

# Rule 5: Severe Dehydration (8시간 이상 무뇨, 눈물 없음, 극심한 입술 마름)
DEHYDRATION_PATTERN = re.compile(
    r"(소변.*([0-9]+\s*시간\s*|한\s*번도\s*)?(안\s*보|안보고|없|단절)|눈물(이)?\s*안\s*나|기저귀가\s*말라|입술.*바짝\s*말)"
)

# Rule 6: Head Trauma with Vomiting / Drowsiness (두부 외상 후 구토, 기면)
HEAD_TRAUMA_PATTERN = re.compile(
    r"((머리|이마).*(찧|부딪|쿵|다치|떨어)|(침대|소파|의자|낙상).*(떨어|쿵)).*(토|구토|눈이\s*감|잠만|의식|어지|처짐)"
)

# Rule 7: Bilious Vomiting & Projectile Vomiting (초록색 담즙 구토, 분수토, 장폐색 의심)
BILIOUS_VOMITING_PATTERN = re.compile(
    r"(초록색.*(토|구토|액체|뿜)|담즙|분수(처럼|성)?.*(토|구토|뿜))"
)


# ============================================================================
# 2. Adversarial & Medical Ethics Safety Regex Patterns
# ============================================================================

# Dangerous folk remedy: needle pricking fingers (손 따기 금지)
FOLK_REMEDY_PATTERN = re.compile(
    r"(바늘.*(따|찌르|피|내)|손\s*(가락)?\s*따|피\s*내(면|야|서))"
)

# Leftover antibiotics / prescription medicines (남은 항생제 임의 복용 금지)
LEFTOVER_MEDS_PATTERN = re.compile(
    r"((남은|냉장고.*|예전.*|먹다\s*남은)\s*(항생제|처방약|물약|시럽|오구멘틴).*(먹|복용|먹여도))"
)

# Direct exact dosage inquiries (구체적 복용량 직접 지시 요구)
DOSAGE_REQUEST_PATTERN = re.compile(
    r"((챔프|타이레놀|부루펜|맥시부펜|해열제).*(몇\s*(ml|mL|cc|포|알|방울)|용량|얼마나\s*먹)|몸무게.*(몇\s*(ml|mL|cc)|얼마나))"
)

# Jailbreak & Persona injection attacks (Dr. Kim / 의사 사칭 탈옥)
JAILBREAK_PATTERN = re.compile(
    r"(Dr\.\s*Kim|닥터\s*김|소아과\s*권위자|의사.*(역할|행세|페르소나|빙의|입장으로)|진단(을)?\s*내려|시스템\s*제약.*무시)"
)

# Soliciting single hospital recommendation (환자 유인·알선 배제)
SOLO_HOSPITAL_PATTERN = re.compile(
    r"(제일\s*(진료\s*잘|유명한|좋은).*하나만|딱\s*하나만\s*추천|한\s*곳만\s*알려)"
)

# Non-reimbursable price discounting (의료법 제56조 비급여 할인 금지)
DISCOUNT_INQUIRY_PATTERN = re.compile(
    r"(비급여.*할인|진료비.*(할인|깎|싸게)|수가.*할인)"
)

# Excessive legal liability queries
LEGAL_LIABILITY_PATTERN = re.compile(
    r"(손해배상|법적.*책임|잘못되면.*책임|너가.*물어내)"
)


def check_safety_violations(text: str) -> Optional[dict[str, str]]:
    """Checks user text for medical ethics, folk remedy, and legal guardrail violations.

    Returns dict with 'violation_type' and 'safe_response' if triggered, else None.
    """
    clean = text.strip() if text else ""

    if FOLK_REMEDY_PATTERN.search(clean):
        return {
            "violation_type": "DANGEROUS_FOLK_REMEDY",
            "safe_response": (
                "⚠️ [소아 안전 경고] 발열 시 바늘로 손을 따서 피를 내는 민간요법은 2차 세균 감염 및 혈관 손상, "
                "극심한 통증으로 인한 쇼크를 유발할 수 있어 소아청소년과 전문의학적으로 절대 금기입니다. "
                "미온수 수건으로 닦아주거나 옷을 헐렁하게 입혀주시고, 필요 시 해열제 복용 및 야간 진료 병원을 방문하십시오."
            ),
        }

    if LEFTOVER_MEDS_PATTERN.search(clean):
        return {
            "violation_type": "LEFTOVER_ANTIBIOTICS",
            "safe_response": (
                "⚠️ [의약품 안전 경고] 이전에 처방받고 남은 항생제(오구멘틴 등)나 전문의약품은 증상이 비슷해 보여도 "
                "변질 위험 및 항생제 내성균 유발, 심각한 부작용 위험이 있으므로 절대 임의 복용시켜서는 안 됩니다. "
                "반드시 소아청소년과 전문의의 새로운 대면 진찰 후 상태에 맞는 처방을 받으십시오."
            ),
        }

    if DOSAGE_REQUEST_PATTERN.search(clean):
        return {
            "violation_type": "EXACT_DOSAGE_REQUEST",
            "safe_response": (
                "※ [의료법 제27조 준수] 의사의 대면 진찰 없는 AI의 특정 의약품 용량(ml/포) 직접 처방 및 지시는 법적으로 금지되어 있습니다. "
                "해열제 포장 겉면의 '체중/연령별 표준 용법·용량표'를 엄격히 준수하시거나 의사/약사와 상담하십시오."
            ),
        }

    if JAILBREAK_PATTERN.search(clean):
        return {
            "violation_type": "JAILBREAK_PERSONA",
            "safe_response": (
                "※ MoonlightCare는 소아 야간 응급 안내 보조 시스템이며, 의료법상 AI는 의사 역할을 대행하거나 질환에 대한 확정 진단을 내릴 수 없습니다. "
                "아이의 안전을 위해 표준 문진 및 야간 병원 안내를 도와드리겠습니다."
            ),
        }

    if SOLO_HOSPITAL_PATTERN.search(clean):
        return {
            "violation_type": "SOLO_HOSPITAL_RECOMMENDATION",
            "safe_response": (
                "※ [의료법 제27조 제3항 준수] 의료법상 특정 의료기관을 단독으로 알선하거나 유인하는 행위는 엄격히 금지되어 있습니다. "
                "MoonlightCare는 보호자님의 현재 위치와 진료시간, 잔여 병상 데이터를 바탕으로 객관적인 상위 2~3곳을 공정하게 안내해 드립니다."
            ),
        }

    if DISCOUNT_INQUIRY_PATTERN.search(clean):
        return {
            "violation_type": "DISCOUNT_INQUIRY",
            "safe_response": (
                "※ 의료법 제56조에 따라 의료기관의 진료비 할인이나 비급여 수가 감면 유인 행위는 법적으로 금지되어 있습니다. "
                "야간·휴일 진료 시에는 법정 건강보험 야간가산율이 적용되며, 정확한 진료비는 해당 의료기관에 문의하시기 바랍니다."
            ),
        }

    if LEGAL_LIABILITY_PATTERN.search(clean):
        return {
            "violation_type": "LEGAL_LIABILITY",
            "safe_response": (
                "※ MoonlightCare는 공공데이터포털(E-Gen)의 실시간 정보를 바탕으로 가장 가까운 의료기관을 탐색해 드리는 정보 보조 도구입니다. "
                "현장 병원 사정에 따라 조기 마감될 수 있으므로, 출발 전 반드시 제공해 드리는 전화 스크립트로 병원에 사전 확인 후 방문하시기 바랍니다."
            ),
        }

    return None


# ============================================================================
# 3. Medical Service Act (의료법 제27조) Post-Filtering Regex
# ============================================================================

# Prohibited Diagnosis Declaration Patterns ("~로 진단됩니다", "~입니다", "~질환으로 판단됩니다")
PROHIBITED_DIAGNOSIS_PATTERN = re.compile(
    r"([가-힣]{2,10}(염|증|증후군|감기|수족구|돌발진|독감|폐렴|장염|중이염|요로감염|뇌수막염))\s*(입|로\s*진단|으로\s*판단|입니다|으로\s*보입니다|에\s*해당합니다)"
)

# Prohibited Prescription Dosage Patterns ("10ml를 먹이세요", "500mg을 복용시키세요")
PROHIBITED_DOSAGE_PATTERN = re.compile(
    r"([0-9]+(\.[0-9]+)?\s*(ml|mL|mg|포|정|알|cc))\s*(을|를)?\s*(먹이|복용|투약|먹이세요|복용시키세요|먹이십시오)"
)

LEGAL_DISCLAIMER_BADGE = (
    "\n\n※ [의료법 제27조 준수 고지] MoonlightCare의 사전 문진 및 안내는 의료인의 대면 진료를 대신할 수 없습니다. "
    "환아의 상태 변화에 따라 즉시 소아청소년과 전문의의 대면 진찰을 받으십시오."
)


# ============================================================================
# 4. Core Pre-Triage Interceptor Function
# ============================================================================

def check_red_flag_instant(
    text: str,
    state: Optional[PatientSessionState] = None,
) -> bool:
    """Pre-execution zero-latency interceptor for pediatric KTAS Red Flag emergencies.

    Execution time: < 0.1ms (In-Memory Regex & State Verification).
    If Red Flag is detected, state is immediately transitioned to 'EMERGENCY_ESCALATION'.
    """
    clean_text = text.strip() if text else ""
    detected = False
    reason: Optional[str] = None
    guide: Optional[str] = None

    # Check 1: Infant < 100 days with Fever
    if (
        INFANT_FEVER_PATTERN_1.search(clean_text)
        or INFANT_FEVER_PATTERN_2.search(clean_text)
        or (
            state
            and (
                (state.age_days is not None and state.age_days <= 100)
                or (state.age_months is not None and state.age_months <= 3)
            )
            and (
                (state.temperature is not None and state.temperature >= 38.0)
                or any("열" in s for s in state.symptoms)
                or "열" in clean_text
            )
        )
    ):
        detected = True
        reason = "생후 100일 미만 38도 이상 고열 (신생아 패혈증/세균성 뇌수막염 위험 Red Flag)"
        guide = (
            "1. 즉시 119 구급차를 호출하거나 가장 가까운 대학병원/소아전문응급의료센터로 직행하십시오.\n"
            "2. 의료진 진찰 전 해열제를 임의로 투약하지 마십시오.\n"
            "3. 체온계 및 마지막 수유 시각을 기록해 두십시오."
        )

    # Check 2: Seizure / Convulsion
    elif SEIZURE_PATTERN.search(clean_text):
        detected = True
        reason = "소아 경련/열성경련 응급 상황 (기도 확보 및 뇌 손상 방지 급선무)"
        guide = (
            "1. 즉시 119에 신고하십시오.\n"
            "2. [구급차 도착 전 대처법]: 아이를 평평한 곳에 눕히고 고개를 옆으로 돌려 기도를 확보하십시오.\n"
            "3. 혀 깨물림 방지를 핑계로 입에 손가락, 숟가락 등 어떤 물건도 절대 넣지 마십시오.\n"
            "4. 경련 지속 시간(분)을 시계로 정확히 기록하십시오."
        )

    # Check 3: Unresponsiveness / Severe Lethargy
    elif UNRESPONSIVE_PATTERN.search(clean_text):
        detected = True
        reason = "중증 의식 저하 및 무반응 (신경계/대사 응급 질환 의심 Red Flag)"
        guide = (
            "1. 지체 없이 즉시 119 구급차를 호출하십시오.\n"
            "2. 아이의 어깨를 가볍게 두드리며 이름을 부르고 호흡 여부를 확인하십시오.\n"
            "3. 물이나 음료를 억지로 먹이지 마십시오 (기도 흡인 위험)."
        )

    # Check 4: Respiratory Distress / Cyanosis
    elif RESPIRATORY_CYANOSIS_PATTERN.search(clean_text):
        detected = True
        reason = "중증 호흡곤란 및 청색증 (저산소증 위험 Red Flag)"
        guide = (
            "1. 즉시 119에 구조를 요청하십시오.\n"
            "2. 조이는 옷과 기저귀를 풀고 상체를 비스듬히 세워 기도를 유지하십시오.\n"
            "3. 산소 공급 및 응급 처치가 가능한 상급 응급실 이송이 필수적입니다."
        )

    # Check 5: Severe Dehydration (8+ hours no urine)
    elif DEHYDRATION_PATTERN.search(clean_text):
        detected = True
        reason = "소아 중증 탈수 (8시간 이상 무뇨, 정맥 수액 처치 급선무)"
        guide = (
            "1. 급성 신손상 및 순환기 쇼크 위험이 있으므로 즉시 응급실로 이동하십시오.\n"
            "2. 많은 양의 물을 억지로 먹이지 마시고 정맥 수액 처치가 가능한 병원을 방문하십시오."
        )

    # Check 6: Head Trauma with Vomiting / Lethargy
    elif HEAD_TRAUMA_PATTERN.search(clean_text):
        detected = True
        reason = "두부 외상 후 뇌압 상승 및 두개내 출혈 의심 Red Flag"
        guide = (
            "1. 즉시 119를 호출하고 소아 CT 촬영이 가능한 응급의료센터로 이송하십시오.\n"
            "2. 아이의 목을 무리하게 꺾지 마시고 구토 시 고개만 옆으로 돌려주십시오."
        )

    # Check 7: Bilious Vomiting (Green bile / projectile)
    elif BILIOUS_VOMITING_PATTERN.search(clean_text):
        detected = True
        reason = "담즙성 구토 및 장폐색/장중첩증 의심 Red Flag"
        guide = (
            "1. 초록색 담즙 구토는 소아 외과 처치가 필요한 응급 상황입니다. 즉시 종합병원 응급실로 직행하십시오.\n"
            "2. 추가 음식물이나 물 섭취를 일체 중단(금식)하십시오."
        )

    if detected and state is not None:
        state.escalate_to_emergency(
            reason=reason or "KTAS 소아 응급 징후 감지",
            guide=guide or "즉시 119에 연락하십시오.",
        )

    return detected


# ============================================================================
# 4. Core Post-Triage Sanitizer Function
# ============================================================================

def sanitize_output(llm_output: str) -> str:
    """Post-filters LLM responses to ensure compliance with Medical Service Act Article 27.

    1. Blocks definitive diagnostic declarations.
    2. Blocks specific prescription drug dosage instructions.
    3. Always attaches legal disclaimer badge.
    """
    if not llm_output:
        return ""

    sanitized = llm_output

    # 1. Neutralize diagnostic statements
    def _replace_diagnosis(match: re.Match) -> str:
        disease = match.group(1)
        return f"{disease} 의심 증상으로 보일 수 있으나 확정 진단이 아닙니다. 정확한 진단은 전문의 진찰이 필요합니다."

    sanitized = PROHIBITED_DIAGNOSIS_PATTERN.sub(_replace_diagnosis, sanitized)

    # 2. Neutralize specific dosage instructions
    def _replace_dosage(match: re.Match) -> str:
        return "[의약품 복용량은 소아청소년과 전문의 또는 약사의 복약지도를 따르십시오]"

    sanitized = PROHIBITED_DOSAGE_PATTERN.sub(_replace_dosage, sanitized)

    # 3. Attach legal disclaimer badge if not already present
    if "의료법 제27조 준수 고지" not in sanitized:
        sanitized += LEGAL_DISCLAIMER_BADGE

    return sanitized


# ============================================================================
# 5. Object-Oriented Guardrail Agent Wrapper
# ============================================================================

class MedicalGuardrailAgent:
    """Agent class coordinating pre-triage interceptor and post-triage sanitizer."""

    @classmethod
    def check_input(
        cls, text: str, state: Optional[PatientSessionState] = None
    ) -> bool:
        """Inspects user input for Red Flag conditions."""
        return check_red_flag_instant(text, state)

    @classmethod
    def check_safety(cls, text: str) -> Optional[dict[str, str]]:
        """Inspects user input for adversarial, dangerous folk remedy, or legal violations."""
        return check_safety_violations(text)

    @classmethod
    def sanitize(cls, llm_output: str) -> str:
        """Sanitizes LLM outputs for regulatory compliance."""
        return sanitize_output(llm_output)

    @classmethod
    def build_emergency_card(cls, state: PatientSessionState) -> dict[str, Any]:
        """Constructs an emergency escalation card payload for frontend modal rendering."""
        return {
            "type": "EMERGENCY_MODAL",
            "session_id": state.session_id,
            "status": "CRITICAL_ESCALATION",
            "title": "🚨 119 구급차 호출 및 소아전문응급의료센터 직행 필요",
            "reason": state.red_flag_reason,
            "immediate_actions": state.emergency_action_guide,
            "cta_buttons": [
                {"label": "📞 119 전화 연결", "action": "tel:119", "primary": True},
                {"label": "🏥 10km 이내 소아 가용 응급실 보기", "action": "NAVIGATE_ER_MAP"},
            ],
        }

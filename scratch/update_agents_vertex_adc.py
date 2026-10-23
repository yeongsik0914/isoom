# -*- coding: utf-8 -*-
import os

# 1. triage_agent.py
triage_path = "e:/isoom/app/agents/triage_agent.py"
with open(triage_path, "r", encoding="utf-8") as f:
    code = f.read()

target = """        if self.api_key:
            try:
                import google.genai as genai

                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"[TriageAgent] Failed to initialize Google GenAI Client: {e}")
                self._client = None"""

replacement = """        if self.api_key:
            try:
                import google.genai as genai

                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"[TriageAgent] Failed to initialize Google GenAI Client with API Key: {e}")
                self._client = None
        elif os.getenv("K_SERVICE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("USE_VERTEX_AI", "").lower() == "true":
            try:
                import google.genai as genai

                project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or "iceu-songpa10"
                location = os.getenv("GOOGLE_CLOUD_LOCATION", "asia-northeast3")
                self._client = genai.Client(vertexai=True, project=project_id, location=location)
                logger.info(f"[TriageAgent] Initialized Vertex AI ADC Client (Project: {project_id}, Region: {location})")
            except Exception as e:
                logger.warning(f"[TriageAgent] Failed to initialize Vertex AI ADC Client: {e}")
                self._client = None"""

if target in code:
    code = code.replace(target, replacement, 1)
    with open(triage_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(code)
    print("triage_agent.py updated with Vertex AI ADC fallback!")
else:
    print("triage_agent.py target not found or already updated.")

# 2. logistics_agent.py
logistics_path = "e:/isoom/app/agents/logistics_agent.py"
with open(logistics_path, "r", encoding="utf-8") as f:
    code2 = f.read()

target2 = """        if self.api_key:
            try:
                import google.genai as genai

                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"[LogisticsAgent] Failed to initialize Google GenAI Client: {e}")
                self._client = None"""

replacement2 = """        if self.api_key:
            try:
                import google.genai as genai

                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"[LogisticsAgent] Failed to initialize Google GenAI Client with API Key: {e}")
                self._client = None
        elif os.getenv("K_SERVICE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("USE_VERTEX_AI", "").lower() == "true":
            try:
                import google.genai as genai

                project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or "iceu-songpa10"
                location = os.getenv("GOOGLE_CLOUD_LOCATION", "asia-northeast3")
                self._client = genai.Client(vertexai=True, project=project_id, location=location)
                logger.info(f"[LogisticsAgent] Initialized Vertex AI ADC Client (Project: {project_id}, Region: {location})")
            except Exception as e:
                logger.warning(f"[LogisticsAgent] Failed to initialize Vertex AI ADC Client: {e}")
                self._client = None"""

if target2 in code2:
    code2 = code2.replace(target2, replacement2, 1)
    with open(logistics_path, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(code2)
    print("logistics_agent.py updated with Vertex AI ADC fallback!")
else:
    print("logistics_agent.py target not found or already updated.")


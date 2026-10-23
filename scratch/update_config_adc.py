# -*- coding: utf-8 -*-
with open("e:/isoom/app/config.py", "r", encoding="utf-8") as f:
    code = f.read()

old_has = """    def has_firebase_key(self) -> bool:
        has_file = bool(self.firebase_key_path and os.path.exists(self.firebase_key_path))
        has_json_env = bool(os.getenv("FIREBASE_KEY_JSON"))
        is_cloud_run = bool(os.getenv("K_SERVICE"))
        return has_file or has_json_env or is_cloud_run"""

new_has = """    def has_firebase_key(self) -> bool:
        has_file = bool(self.firebase_key_path and os.path.exists(self.firebase_key_path))
        has_json_env = bool(os.getenv("FIREBASE_KEY_JSON"))
        is_cloud_run = bool(os.getenv("K_SERVICE"))
        has_adc = bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("USE_ADC", "").lower() == "true")
        return has_file or has_json_env or is_cloud_run or has_adc"""

assert old_has in code, "old_has not found"
code = code.replace(old_has, new_has, 1)

old_init = """        elif os.getenv("K_SERVICE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            # 3. Google Application Default Credentials (ADC / Cloud Run IAM Keyless)
            firebase_admin.initialize_app()"""

new_init = """        elif os.getenv("K_SERVICE") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("USE_ADC", "").lower() == "true":
            # 3. Google Application Default Credentials (ADC / Cloud Run IAM Keyless)
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT") or "iceu-songpa10"
            firebase_admin.initialize_app(options={"projectId": project_id})"""

assert old_init in code, "old_init not found"
code = code.replace(old_init, new_init, 1)

with open("e:/isoom/app/config.py", "w", encoding="utf-8", newline="\r\n") as f:
    f.write(code)

print("app/config.py successfully updated with ADC enhancements!")


from pathlib import Path

# 1. Update api.py
api_file = Path(r"D:\Projects\SIH26101\SIH26101-Integrated\backend\competency_engine\api.py")
text = api_file.read_text(encoding="utf-8")

old_provider = """@app.get("/api/trainer/provider-status", tags=["Trainer Material Ingestion"])
def get_provider_status() -> Dict[str, Any]:
    \"\"\"Report whether an external LLM API provider or deterministic source extractor is active.\"\"\"
    import os
    has_api_key = bool(os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY"))
    model = os.getenv("LLM_MODEL", "gpt-4o-mini" if has_api_key else "deterministic_source_extractor")
    return {
        "configured": has_api_key,
        "mode": "llm_api" if has_api_key else "offline_source_grounded_heuristic",
        "model": model,
        "demonstration_notice": "When no LLM API key is set, questions are derived deterministically from the authentic text of the uploaded document without external API dependencies."
    }"""

new_provider = """@app.get("/api/trainer/provider-status", tags=["Trainer Material Ingestion"])
def get_provider_status() -> Dict[str, Any]:
    \"\"\"Report whether an external LLM API provider or deterministic source extractor is active.\"\"\"
    import os
    has_api_key = bool(os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY"))
    if has_api_key:
        if os.getenv("GEMINI_API_KEY") and not (os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")):
            default_model = "gemini-1.5-flash"
        else:
            default_model = "gpt-4o-mini"
        model = os.getenv("LLM_MODEL", default_model)
        mode = "openai_compatible"
    else:
        model = "deterministic_source_extractor"
        mode = "offline_source_grounded_heuristic"

    return {
        "configured": has_api_key,
        "mode": mode,
        "model": model,
        "demonstration_notice": "When no LLM API key is set, questions are derived deterministically from the authentic text of the uploaded document without external API dependencies."
    }"""

if old_provider in text:
    text = text.replace(old_provider, new_provider)
    api_file.write_text(text, encoding="utf-8")
    print("Updated api.py successfully.")
else:
    print("Pattern not found in api.py.")

# 2. Update question_generator_service.py for Gemini auto-endpoint
qg_file = Path(r"D:\Projects\SIH26101\SIH26101-Integrated\backend\competency_engine\question_generator_service.py")
qg_text = qg_file.read_text(encoding="utf-8")

old_cfg = """        # Check if LLM provider is configured
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("LLM_MODEL", "gpt-4o-mini")"""

new_cfg = """        # Check if LLM provider is configured
        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        model = os.getenv("LLM_MODEL")

        if not base_url:
            if os.getenv("GEMINI_API_KEY") and not (os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")):
                base_url = "https://generativelanguage.googleapis.com/v1beta/openai"
                model = model or "gemini-1.5-flash"
            else:
                base_url = "https://api.openai.com/v1"
                model = model or "gpt-4o-mini"
        else:
            model = model or "gpt-4o-mini" """

if old_cfg in qg_text:
    qg_text = qg_text.replace(old_cfg, new_cfg)
    qg_file.write_text(qg_text, encoding="utf-8")
    print("Updated question_generator_service.py successfully.")
else:
    print("Pattern not found in question_generator_service.py.")

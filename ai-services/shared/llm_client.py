# ──────────────────────────────────────────────────────────────
#  Module: shared/llm_client.py
#  Responsibility: Shared Azure OpenAI client wrapper.
#
#  Class: LLMClient
#    - Singleton pattern
#    - Reads config from environment
#    - Wraps AzureOpenAI with tenacity retry (3x, exponential)
#    - Methods:
#        chat_completion(messages, response_format) → str
#        parse_json_response(raw_text) → dict
#    - Structured logging of all API calls (latency, tokens used)
#    - Never logs prompt content (PII safety)
# ──────────────────────────────────────────────────────────────
# TODO: Implement

# ──────────────────────────────────────────────────────────────
#  Module: resume_parser/parser.py
#  Responsibility: End-to-end resume parsing pipeline.
#
#  Pipeline:
#    1. Receive PDF bytes or Blob URL
#    2. Extract text via Azure Document Intelligence
#       (AnalyzeDocument prebuilt-read model)
#    3. Send extracted text to llm_client.parse_resume()
#    4. Validate structured JSON against ParsedResume schema
#    5. Run confidence scoring
#    6. Return ParsedResume dataclass
#
#  Class: ResumeParser
#    Methods:
#      parse_from_bytes(pdf_bytes) → ParsedResume
#      parse_from_url(blob_url)   → ParsedResume
#      _extract_text(pdf_bytes)   → str
#      _call_llm(text)            → dict
#      _validate(raw)             → ParsedResume
# ──────────────────────────────────────────────────────────────
# TODO: Implement

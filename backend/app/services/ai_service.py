from __future__ import annotations

import logging

from app.services.ai_client import AIServiceUnavailableError, azure_openai_client
from app.services.ai_schemas import DuplicateResult, EmailContent, ParsedResume
from app.services.prompts import build_duplicate_messages, build_email_messages
from app.services.resume_parser import resume_parser

logger = logging.getLogger(__name__)


class AIService:
    async def parse_resume_bytes(self, pdf_bytes: bytes) -> ParsedResume:
        try:
            return await resume_parser.pipeline(pdf_bytes)
        except AIServiceUnavailableError:
            logger.warning("AI service not configured; returning empty ParsedResume")
            return ParsedResume(confidence_score=0.0)
        except Exception as exc:
            logger.error("Resume parsing failed: %s", exc, exc_info=True)
            return ParsedResume(confidence_score=0.0)

    async def parse_resume_text(self, resume_text: str) -> ParsedResume:
        try:
            return await resume_parser.pipeline_from_text(resume_text)
        except AIServiceUnavailableError:
            logger.warning("AI service not configured; returning empty ParsedResume")
            return ParsedResume(confidence_score=0.0)
        except Exception as exc:
            logger.error("Resume text parsing failed: %s", exc, exc_info=True)
            return ParsedResume(confidence_score=0.0)

    async def generate_email(self, event: str, context: dict) -> EmailContent:
        recipient = context.get("recipient_name", "Candidate")
        try:
            messages = build_email_messages(event, context)
            raw = await azure_openai_client.chat_json(messages, temperature=0.4, max_tokens=1024)
            return EmailContent(
                subject=raw.get("subject", f"[InternFlow] {event.replace('_', ' ').title()}"),
                body=raw.get("body", self._fallback_body(event, recipient)),
                recipient_name=recipient,
            )
        except AIServiceUnavailableError:
            logger.warning("AI not configured; using fallback email")
            return self._fallback_email(event, context)
        except Exception as exc:
            logger.error("Email generation failed: %s", exc, exc_info=True)
            return self._fallback_email(event, context)

    @staticmethod
    def _fallback_email(event: str, context: dict) -> EmailContent:
        recipient = context.get("recipient_name", "Candidate")
        return EmailContent(
            subject=f"[InternFlow] {event.replace('_', ' ').title()}",
            body=(
                f"Dear {recipient},\n\nThis is an automated message from the Intern Flow platform "
                "regarding your internship application.\n\n"
                "Please log in to the Intern Flow portal for the latest updates.\n\n"
                "Best regards,\nThe Intern Flow Team"
            ),
            recipient_name=recipient,
        )

    @staticmethod
    def _fallback_body(event: str, recipient: str) -> str:
        return (
            f"Dear {recipient},\n\nThis is an automated notification from Intern Flow.\n\n"
            "Best regards,\nThe Intern Flow Team"
        )

    async def check_duplicate(
        self,
        candidate_email: str,
        candidate_name: str,
        existing_referrals: list[dict],
    ) -> DuplicateResult:
        email_norm = candidate_email.lower().strip()
        for ref in existing_referrals:
            if ref.get("candidate_email", "").lower().strip() == email_norm:
                return DuplicateResult(
                    is_duplicate=True,
                    confidence=1.0,
                    matched_email=ref["candidate_email"],
                    matched_referral_id=str(ref.get("id", "")),
                    reason="Exact email match found in existing referrals.",
                )
        if not existing_referrals:
            return DuplicateResult(is_duplicate=False, confidence=1.0,
                                   reason="No existing referrals to compare against.")
        try:
            messages = build_duplicate_messages(
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                existing=existing_referrals,
            )
            raw = await azure_openai_client.chat_json(messages, temperature=0.0, max_tokens=256)
            result = DuplicateResult(
                is_duplicate=raw.get("is_duplicate", False),
                confidence=float(raw.get("confidence", 0.0)),
                matched_email=raw.get("matched_email"),
                reason=raw.get("reason"),
            )
            if result.matched_email:
                for ref in existing_referrals:
                    if ref.get("candidate_email", "").lower() == result.matched_email.lower():
                        result.matched_referral_id = str(ref.get("id", ""))
                        break
            return result
        except AIServiceUnavailableError:
            logger.warning("AI duplicate check not configured; exact-email only.")
            return DuplicateResult(is_duplicate=False, confidence=0.5,
                                   reason="AI service not configured; only exact-email check performed.")
        except Exception as exc:
            logger.error("Duplicate check failed: %s", exc, exc_info=True)
            return DuplicateResult(is_duplicate=False, confidence=0.0,
                                   reason=f"AI check error: {type(exc).__name__}")


ai_service = AIService()

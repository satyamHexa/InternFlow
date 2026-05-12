# ──────────────────────────────────────────────────────────────
#  Module: app/core/constants.py
#  Responsibility: Shared enumerations and literals.
# ──────────────────────────────────────────────────────────────

from enum import Enum


class UserRole(str, Enum):
    EMPLOYEE           = "employee"
    HR                 = "hr"
    MENTOR             = "mentor"
    IT_ADMIN           = "it_admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    PROGRAM_OWNER      = "program_owner"


class ReferralStatus(str, Enum):
    DRAFT              = "draft"
    SUBMITTED          = "submitted"
    HR_REVIEW          = "hr_review"
    ELIGIBILITY_CHECK  = "eligibility_check"
    NDA_PENDING        = "nda_pending"
    NDA_SIGNED         = "nda_signed"
    JOINING_FORM       = "joining_form"
    ID_CREATION        = "id_creation"
    IT_PROVISIONING    = "it_provisioning"
    MENTOR_ASSIGNED    = "mentor_assigned"
    ACTIVE             = "active"
    CLOSED             = "closed"
    CERTIFICATE_ISSUED = "certificate_issued"
    REJECTED           = "rejected"


class WorkflowTaskStatus(str, Enum):
    PENDING     = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED   = "completed"
    SKIPPED     = "skipped"


class SLAStatus(str, Enum):
    ON_TRACK = "on_track"
    AT_RISK  = "at_risk"
    BREACHED = "breached"


class NotificationEvent(str, Enum):
    REFERRAL_SUBMITTED   = "referral_submitted"
    NDA_PENDING          = "nda_pending"
    NDA_SIGNED           = "nda_signed"
    SLA_BREACH           = "sla_breach"
    CERTIFICATE_READY    = "certificate_ready"
    INTERN_START_REMINDER= "intern_start_reminder"
    TASK_ASSIGNED        = "task_assigned"


class AuditAction(str, Enum):
    FORM_EDIT          = "form_edit"
    AI_OVERRIDE        = "ai_override"
    NDA_DOWNLOAD       = "nda_download"
    ACCESS_PROVISION   = "access_provision"
    WORKFLOW_TRANSITION= "workflow_transition"
    LOGIN              = "login"
    LOGOUT             = "logout"
    ROLE_CHANGE        = "role_change"


# SLA target days per workflow stage
SLA_TARGETS: dict[str, int] = {
    "HR Review":               2,
    "Eligibility Validation":  1,
    "NDA Sent":                1,
    "NDA Signed":              5,
    "Joining Form Completed":  3,
    "Non-Worker ID Creation":  3,
    "IT Provisioning":         5,
    "Mentor Assignment":       2,
}

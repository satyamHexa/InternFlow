"""
Import all ORM models here so that:
  1. SQLAlchemy's metadata knows about every table.
  2. Alembic's env.py can discover all tables via Base.metadata.
"""

from app.models.user import User  # noqa: F401
from app.models.referral import Referral  # noqa: F401
from app.models.workflow import WorkflowTask  # noqa: F401
from app.models.onboarding import OnboardingTask  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
from app.models.notification import Notification, NotificationTemplate  # noqa: F401
from app.models.document import NDADocument, Certificate  # noqa: F401

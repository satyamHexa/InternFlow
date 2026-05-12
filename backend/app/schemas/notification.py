from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    event: str
    title: str
    message: str
    channel: str
    is_read: bool
    referral_id: uuid.UUID | None
    created_at: datetime


class UnreadCountResponse(BaseModel):
    count: int

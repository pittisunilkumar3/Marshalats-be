from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import uuid

class NotificationType(str, Enum):
    SMS = "sms"
    WHATSAPP = "whatsapp"
    EMAIL = "email"

class NotificationTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: NotificationType
    subject: Optional[str] = None
    body: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationTemplateCreate(BaseModel):
    name: str
    type: NotificationType
    subject: Optional[str] = None
    body: str

class TriggerNotification(BaseModel):
    user_id: str
    template_id: str
    context: Optional[Dict[str, Any]] = {}

class NotificationLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    template_id: str
    type: NotificationType
    status: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BroadcastAnnouncement(BaseModel):
    branch_id: Optional[str] = None
    template_id: str
    context: Optional[Dict[str, Any]] = {}

class ClassReminder(BaseModel):
    course_id: str
    branch_id: str

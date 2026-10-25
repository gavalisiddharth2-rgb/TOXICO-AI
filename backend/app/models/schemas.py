"""
Pydantic Schemas for API Requests and Responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")
    role: Optional[str] = Field(None, description="Optional target role for quick switch")

class AnalyzeTextRequest(BaseModel):
    text: str = Field(..., description="Raw text content to analyze")
    language: Optional[str] = Field("auto", description="Language code or 'auto'")

class ModerationActionRequest(BaseModel):
    content_item_id: int
    action: str = Field(..., description="One of: approve, flag, report, resolve, mark_false_positive")
    notes: Optional[str] = None
    moderator_name: Optional[str] = "AI Safety Moderator"

class SubmitReportRequest(BaseModel):
    content_item_id: int
    violation_category: str
    custom_notes: Optional[str] = None
    moderator_name: Optional[str] = "AI Safety Moderator"

class ConnectAccountRequest(BaseModel):
    platform: str
    account_name: str
    handle: str
    is_demo: bool = True

class SettingsUpdateRequest(BaseModel):
    safe_threshold: Optional[float] = None
    review_threshold: Optional[float] = None
    flag_threshold: Optional[float] = None
    auto_flag_enabled: Optional[bool] = None
    active_languages: Optional[List[str]] = None

class QueueFilterParams(BaseModel):
    platform: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
    page: int = 1
    page_size: int = 20

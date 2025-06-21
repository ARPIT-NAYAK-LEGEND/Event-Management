from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ResponseType(str, Enum):
    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"

class EventInvitation(BaseModel):
    event_id: str
    host_id: str
    event_name: str
    event_date: datetime
    description: str
    location: str

class GuestResponse(BaseModel):
    event_id: str
    guest_id: str
    response: ResponseType
    message: Optional[str] = None

class EventSummary(BaseModel):
    event_id: str
    host_id: str
    event_name: str
    event_date: datetime
    responses: List[GuestResponse]
    
    def get_summary(self) -> dict:
        summary = {
            "event_id": self.event_id,
            "event_name": self.event_name,
            "event_date": self.event_date.isoformat(),
            "total_invited": len(self.responses),
            "yes_count": len([r for r in self.responses if r.response == ResponseType.YES]),
            "no_count": len([r for r in self.responses if r.response == ResponseType.NO]),
            "maybe_count": len([r for r in self.responses if r.response == ResponseType.MAYBE]),
            "responses": [r.dict() for r in self.responses]
        }
        return summary 
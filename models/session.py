"""Session model representing a phone call session."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .session_text import SessionText


class Session(BaseModel):
    """A phone call session.
    
    Attributes:
        uuid: UUID of the session
        from_user_uuid: UUID of the user who initiated the call
        session_type: Type of session
        begin_at: When the call began
        end_at: When the call ended
        duration: Duration of the call in seconds
        from_language: Language of the caller
        to_language: Language of the recipient
        is_paid: Whether the call was paid
        is_translation_enabled: Whether translation was enabled
        is_ai_call: Whether this is an AI call
        messages: List of conversation messages (populated by DataLoader)
    """
    
    uuid: UUID
    from_user_uuid: Optional[UUID] = None
    session_type: int = 0
    begin_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    duration: float = 0.0
    from_language: str = ""
    to_language: str = ""
    is_paid: bool = False
    is_translation_enabled: bool = False
    is_ai_call: bool = False
    
    # Relationship field - populated by DataLoader
    messages: list[SessionText] = Field(default_factory=list)
    
    model_config = {
        "populate_by_name": True,
    }
    
    @classmethod
    def load_from_csv(cls, file_path: str | Path) -> list["Session"]:
        """Load Session records from a CSV file.
        
        Args:
            file_path: Path to the session.csv file
            
        Returns:
            List of Session instances (without messages populated)
        """
        records = []
        file_path = Path(file_path)
        
        def parse_datetime(value: str) -> Optional[datetime]:
            if not value:
                return None
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        
        def parse_uuid(value: str) -> Optional[UUID]:
            if not value:
                return None
            try:
                return UUID(value)
            except ValueError:
                return None
        
        def parse_int(value: str, default: int = 0) -> int:
            if not value:
                return default
            try:
                return int(value)
            except ValueError:
                return default
        
        def parse_float(value: str, default: float = 0.0) -> float:
            if not value:
                return default
            try:
                return float(value)
            except ValueError:
                return default
        
        def parse_bool(value: str, default: bool = False) -> bool:
            if not value:
                return default
            # Handle both string representations and numeric 0/1
            if value.lower() in ('true', '1', 'yes'):
                return True
            elif value.lower() in ('false', '0', 'no'):
                return False
            return default
        
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    record = cls(
                        uuid=UUID(row["uuid"]),
                        from_user_uuid=parse_uuid(row.get("from_user_uuid", "")),
                        session_type=parse_int(row.get("session_type", "")),
                        begin_at=parse_datetime(row.get("begin_at", "")),
                        end_at=parse_datetime(row.get("end_at", "")),
                        duration=parse_float(row.get("duration", "")),
                        from_language=row.get("from_language", ""),
                        to_language=row.get("to_language", ""),
                        is_paid=parse_bool(row.get("is_paid", "")),
                        is_translation_enabled=parse_bool(row.get("is_translation_enabled", "")),
                        is_ai_call=parse_bool(row.get("is_ai_call", "")),
                    )
                    records.append(record)
                except (ValueError, KeyError):
                    # Skip malformed rows
                    continue
                    
        return records


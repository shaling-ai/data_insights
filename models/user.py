"""User model representing a user in the system."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from .session import Session


class User(BaseModel):
    """A user in the system.
    
    Attributes:
        uuid: UUID of the user
        nick_name: User's nickname/display name
        credits: User's credit balance
        email: User's email address
        registration_time: Registration timestamp
        sessions: List of user's sessions (populated by DataLoader)
    """
    
    uuid: UUID
    nick_name: str = ""
    credits: float = 0.0
    email: str = ""
    registration_time: Optional[datetime] = None
    
    # Relationship field - populated by DataLoader
    sessions: list[Session] = Field(default_factory=list)
    
    model_config = {
        "populate_by_name": True,
    }
    
    @classmethod
    def load_from_csv(cls, file_path: str | Path) -> list["User"]:
        """Load User records from a CSV file.
        
        Args:
            file_path: Path to the user.csv file
            
        Returns:
            List of User instances (without sessions populated)
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
        
        def parse_float(value: str, default: float = 0.0) -> float:
            if not value:
                return default
            try:
                return float(value)
            except ValueError:
                return default
        
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    record = cls(
                        uuid=UUID(row["uuid"]),
                        nick_name=row.get("nick_name", ""),
                        credits=parse_float(row.get("credits", "")),
                        email=row.get("email", ""),
                        registration_time=parse_datetime(row.get("created_at", "")),
                    )
                    records.append(record)
                except (ValueError, KeyError):
                    # Skip malformed rows
                    continue
                    
        return records
    
    @property
    def session_ids(self) -> list[UUID]:
        """Get list of session UUIDs for this user."""
        return [session.uuid for session in self.sessions]


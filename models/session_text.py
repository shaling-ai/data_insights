"""SessionText model representing individual messages in a conversation."""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SessionText(BaseModel):
    """A single message/text entry within a session conversation.
    
    Attributes:
        id: Unique identifier for the text entry
        uuid: UUID of the text entry
        session_uuid: UUID of the parent session
        start_at: Timestamp when the message was sent
        text: Original text content
        text_translated: Translated text content (if applicable)
        speaker: Speaker identifier (0 = user, 1 = AI/system)
        is_input: Whether this is an input message
        type: Message type identifier
    """
    
    id: int
    uuid: UUID
    session_uuid: UUID
    start_at: Optional[datetime] = None
    text: str = ""
    text_translated: str = ""
    speaker: int = 0
    is_input: int = 0
    type: int = Field(default=0, alias="type")
    
    model_config = {
        "populate_by_name": True,
    }
    
    @classmethod
    def load_from_csv(cls, file_path: str | Path) -> list["SessionText"]:
        """Load SessionText records from a CSV file.
        
        Args:
            file_path: Path to the session_text.csv file
            
        Returns:
            List of SessionText instances
        """
        records = []
        file_path = Path(file_path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Parse datetime
                    start_at = None
                    if row.get("start_at"):
                        try:
                            start_at = datetime.fromisoformat(row["start_at"])
                        except ValueError:
                            pass
                    
                    record = cls(
                        id=int(row["id"]),
                        uuid=UUID(row["uuid"]),
                        session_uuid=UUID(row["session_uuid"]),
                        start_at=start_at,
                        text=row.get("text", ""),
                        text_translated=row.get("text_translated", ""),
                        speaker=int(row.get("speaker", 0)),
                        is_input=int(row.get("is_input", 0)),
                        type=int(row.get("type", 0)),
                    )
                    records.append(record)
                except (ValueError, KeyError) as e:
                    # Skip malformed rows
                    continue
                    
        return records


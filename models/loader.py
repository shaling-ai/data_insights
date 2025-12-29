"""DataLoader for loading and linking all models from CSV files."""

from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID

from config import REGISTRATION_DAYS
from .session_text import SessionText
from .session import Session
from .user import User


class DataLoader:
    """Load and link all data models from CSV files.
    
    This class handles loading users, sessions, and session texts from CSV files
    and establishes the relationships between them:
    - User.sessions: populated with Session objects
    - Session.messages: populated with SessionText objects
    
    Example:
        loader = DataLoader("raw_data/")
        loader.load_all()
        
        # Access all users with their sessions and messages
        for user in loader.users:
            print(f"User: {user.nick_name}")
            for session in user.sessions:
                print(f"  Session: {session.uuid}")
                for msg in session.messages:
                    print(f"    {msg.speaker}: {msg.text[:50]}...")
    """
    
    def __init__(self, data_dir: str | Path):
        """Initialize the DataLoader.
        
        Args:
            data_dir: Path to the directory containing the CSV files
        """
        self.data_dir = Path(data_dir)
        self.users: list[User] = []
        self.sessions: list[Session] = []
        self.session_texts: list[SessionText] = []
        
        # Lookup dictionaries for fast access
        self._users_by_uuid: dict[UUID, User] = {}
        self._sessions_by_uuid: dict[UUID, Session] = {}
    
    def load_all(
        self,
        user_file: str = "user.csv",
        session_file: str = "session.csv",
        session_text_file: str = "session_text.csv",
        link_relationships: bool = True,
    ) -> None:
        """Load all data from CSV files.
        
        Args:
            user_file: Filename for user data
            session_file: Filename for session data
            session_text_file: Filename for session text data
            link_relationships: Whether to populate relationship fields
        """
        self.load_users(user_file)
        self.load_sessions(session_file)
        self.load_session_texts(session_text_file)
        
        if link_relationships:
            self.link_all()
    
    def load_users(self, filename: str = "user.csv") -> list[User]:
        """Load users from CSV file, filtering to only those registered in the past N days.
        
        Args:
            filename: Name of the user CSV file
            
        Returns:
            List of loaded User objects registered in the past REGISTRATION_DAYS days
        """
        file_path = self.data_dir / filename
        all_users = User.load_from_csv(file_path)
        
        # Filter users by registration time
        cutoff_date = datetime.now() - timedelta(days=REGISTRATION_DAYS)
        self.users = [
            user for user in all_users
            if user.registration_time and user.registration_time >= cutoff_date
        ]
        
        self._users_by_uuid = {user.uuid: user for user in self.users}
        return self.users
    
    def load_sessions(self, filename: str = "session.csv") -> list[Session]:
        """Load sessions from CSV file.
        
        Args:
            filename: Name of the session CSV file
            
        Returns:
            List of loaded Session objects
        """
        file_path = self.data_dir / filename
        self.sessions = Session.load_from_csv(file_path)
        self._sessions_by_uuid = {session.uuid: session for session in self.sessions}
        return self.sessions
    
    def load_session_texts(self, filename: str = "session_text.csv") -> list[SessionText]:
        """Load session texts from CSV file.
        
        Args:
            filename: Name of the session text CSV file
            
        Returns:
            List of loaded SessionText objects
        """
        file_path = self.data_dir / filename
        self.session_texts = SessionText.load_from_csv(file_path)
        return self.session_texts
    
    def link_all(self) -> None:
        """Link all relationships between models.
        
        This populates:
        - Session.messages with SessionText objects
        - User.sessions with Session objects
        """
        self.link_session_texts_to_sessions()
        self.link_sessions_to_users()
    
    def link_session_texts_to_sessions(self) -> None:
        """Link SessionText objects to their parent Session.
        
        Populates Session.messages for each session.
        """
        # Group session texts by session_uuid
        texts_by_session: dict[UUID, list[SessionText]] = defaultdict(list)
        for text in self.session_texts:
            texts_by_session[text.session_uuid].append(text)
        
        # Sort messages by start_at and assign to sessions
        for session in self.sessions:
            messages = texts_by_session.get(session.uuid, [])
            # Sort by start_at timestamp
            messages.sort(key=lambda x: x.start_at or x.id)
            session.messages = messages
    
    def link_sessions_to_users(self) -> None:
        """Link Session objects to their parent User.
        
        Populates User.sessions for each user.
        """
        # Group sessions by from_user_uuid
        sessions_by_user: dict[UUID, list[Session]] = defaultdict(list)
        for session in self.sessions:
            if session.from_user_uuid:
                sessions_by_user[session.from_user_uuid].append(session)
        
        # Sort sessions by begin_at and assign to users
        for user in self.users:
            user_sessions = sessions_by_user.get(user.uuid, [])
            # Sort by begin_at timestamp (session start time)
            user_sessions.sort(key=lambda x: x.begin_at or datetime.min)
            user.sessions = user_sessions
    
    def get_user_by_uuid(self, uuid: UUID) -> User | None:
        """Get a user by their UUID.
        
        Args:
            uuid: The user's UUID
            
        Returns:
            User object or None if not found
        """
        return self._users_by_uuid.get(uuid)
    
    def get_session_by_uuid(self, uuid: UUID) -> Session | None:
        """Get a session by its UUID.
        
        Args:
            uuid: The session's UUID
            
        Returns:
            Session object or None if not found
        """
        return self._sessions_by_uuid.get(uuid)
    
    @property
    def stats(self) -> dict:
        """Get statistics about the loaded data.
        
        Returns:
            Dictionary with counts of users, sessions, and session texts
        """
        return {
            "users": len(self.users),
            "sessions": len(self.sessions),
            "session_texts": len(self.session_texts),
            "users_with_sessions": sum(1 for u in self.users if u.sessions),
            "sessions_with_messages": sum(1 for s in self.sessions if s.messages),
        }


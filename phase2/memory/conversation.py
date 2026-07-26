"""
Phase 2 - Conversation Memory
Track multi-turn conversations and conversation context
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Message:
    """Single message in conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)


@dataclass
class ConversationSession:
    """Conversation session tracking"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict = field(default_factory=dict)

    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to conversation"""
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        self.last_updated = datetime.now()

    def get_history(self, max_messages: Optional[int] = None) -> List[Tuple[str, str]]:
        """Get conversation history as (role, content) tuples"""
        messages = self.messages
        if max_messages:
            messages = messages[-max_messages:]
        return [(msg.role, msg.content) for msg in messages]

    def get_context(self, max_messages: int = 5) -> str:
        """Get conversation context as formatted string"""
        context_msgs = self.messages[-max_messages:]
        context = []

        for msg in context_msgs:
            prefix = "User:" if msg.role == "user" else "Assistant:"
            context.append(f"{prefix} {msg.content}")

        return "\n".join(context)

    def get_last_question(self) -> Optional[str]:
        """Get the last user question"""
        for msg in reversed(self.messages):
            if msg.role == "user":
                return msg.content
        return None

    def get_conversation_length(self) -> int:
        """Get number of turns in conversation"""
        return len([m for m in self.messages if m.role == "user"])


class ConversationManager:
    """
    Manage multiple conversation sessions
    """

    def __init__(self, max_sessions: int = 100, max_messages_per_session: int = 50):
        """
        Initialize conversation manager

        Args:
            max_sessions: Maximum concurrent sessions to track
            max_messages_per_session: Maximum messages per session before pruning
        """
        self.max_sessions = max_sessions
        self.max_messages_per_session = max_messages_per_session
        self.sessions: Dict[str, ConversationSession] = {}

    def create_session(self, session_id: str, metadata: Optional[Dict] = None) -> ConversationSession:
        """Create new conversation session"""
        if len(self.sessions) >= self.max_sessions:
            # Remove oldest inactive session
            self._prune_oldest_session()

        session = ConversationSession(
            session_id=session_id,
            metadata=metadata or {}
        )
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """Get existing session or create new"""
        if session_id not in self.sessions:
            return self.create_session(session_id)
        return self.sessions[session_id]

    def add_user_message(self, session_id: str, content: str) -> ConversationSession:
        """Add user message to session"""
        session = self.get_session(session_id)
        session.add_message('user', content)

        if len(session.messages) > self.max_messages_per_session:
            self._prune_session(session_id)

        return session

    def add_assistant_message(self, session_id: str, content: str, metadata: Optional[Dict] = None) -> ConversationSession:
        """Add assistant response to session"""
        session = self.get_session(session_id)
        session.add_message('assistant', content, metadata)
        return session

    def get_conversation_context(self, session_id: str, max_messages: int = 5) -> str:
        """Get context for this session"""
        session = self.get_session(session_id)
        return session.get_context(max_messages=max_messages)

    def _prune_oldest_session(self):
        """Remove oldest inactive session"""
        if not self.sessions:
            return

        oldest = min(self.sessions.values(), key=lambda s: s.last_updated)
        del self.sessions[oldest.session_id]

    def _prune_session(self, session_id: str):
        """Remove old messages from session (keep recent)"""
        session = self.sessions.get(session_id)
        if not session:
            return

        # Keep only recent messages
        keep_count = max(10, self.max_messages_per_session // 2)
        if len(session.messages) > keep_count:
            session.messages = session.messages[-keep_count:]

    def clear_session(self, session_id: str):
        """Clear all messages from session"""
        if session_id in self.sessions:
            self.sessions[session_id].messages = []

    def export_session(self, session_id: str) -> str:
        """Export session as JSON"""
        session = self.get_session(session_id)
        if not session:
            return ""

        data = {
            'session_id': session.session_id,
            'created_at': session.created_at.isoformat(),
            'messages': [
                {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat()
                }
                for msg in session.messages
            ]
        }

        return json.dumps(data, indent=2)

    def import_session(self, json_data: str) -> Optional[ConversationSession]:
        """Import session from JSON"""
        try:
            data = json.loads(json_data)
            session = self.create_session(data['session_id'])

            for msg_data in data.get('messages', []):
                session.add_message(msg_data['role'], msg_data['content'])

            return session
        except:
            return None

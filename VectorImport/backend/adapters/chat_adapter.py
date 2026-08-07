"""
adapters/chat_adapter.py
-------------------------
Loads chat messages from data/projects/{code}/chats.json.
Returns a list of validated ChatMessageSchema.
"""

from __future__ import annotations

from adapters.file_adapter import FileAdapter
from exceptions import AdapterError
from schemas.domain.communications import ChatMessageSchema


class ChatAdapter(FileAdapter[list[ChatMessageSchema]]):
    adapter_name = "ChatAdapter"
    _filename    = "chats.json"

    def load(self, project_id: int) -> list[ChatMessageSchema]:
        self._log.debug("Loading chat messages for project_id=%s", project_id)
        try:
            raw      = self._read_json(project_id)
            messages = [ChatMessageSchema(**item) for item in raw]
            self._validate(messages)
            channels = {m.channel for m in messages if m.channel}
            self._log.info(
                "Loaded %d message(s) from %d channel(s) for project_id=%s",
                len(messages), len(channels), project_id,
            )
            return messages
        except AdapterError:
            raise
        except Exception as exc:
            self._raise(f"Failed to parse chat messages for project_id={project_id}", exc)

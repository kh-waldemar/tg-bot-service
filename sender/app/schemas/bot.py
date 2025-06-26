from pydantic import BaseModel
from typing import Optional

class SendMessage(BaseModel):
    chat_id: int
    text: str
    parse_mode: Optional[str] = None

class SendPhoto(BaseModel):
    chat_id: int
    photo: str
    caption: Optional[str] = None

class SendDocument(BaseModel):
    chat_id: int
    document: str
    caption: Optional[str] = None

class SendAudio(BaseModel):
    chat_id: int
    audio: str
    caption: Optional[str] = None

class SendVoice(BaseModel):
    chat_id: int
    voice: str
    caption: Optional[str] = None

class SendVideo(BaseModel):
    chat_id: int
    video: str
    caption: Optional[str] = None

class EditMessageText(BaseModel):
    chat_id: int
    message_id: int
    text: str
    parse_mode: Optional[str] = None

class DeleteMessage(BaseModel):
    chat_id: int
    message_id: int

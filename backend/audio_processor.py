"""
Audio Processor - Handles audio format conversion and streaming
Prepares audio for web frontend
"""

import logging
import base64
from typing import Optional

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Handle audio processing for frontend-backend communication"""
    
    def __init__(self):
        """Initialize audio processor"""
        self.supported_formats = ["wav", "mp3", "ogg", "webm"]
    
    def encode_audio_to_base64(self, audio_bytes: bytes) -> str:
        """
        Encode audio bytes to base64 for transmission
        
        Args:
            audio_bytes: Raw audio bytes
        
        Returns:
            Base64 encoded string
        """
        try:
            return base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding audio to base64: {e}")
            raise
    
    def decode_audio_from_base64(self, audio_base64: str) -> bytes:
        """
        Decode base64 audio string to bytes
        
        Args:
            audio_base64: Base64 encoded audio string
        
        Returns:
            Raw audio bytes
        """
        try:
            return base64.b64decode(audio_base64)
        except Exception as e:
            logger.error(f"Error decoding audio from base64: {e}")
            raise
    
    def create_audio_data_url(self, audio_base64: str, format: str = "wav") -> str:
        """
        Create data URL for audio playback in browser
        
        Args:
            audio_base64: Base64 encoded audio
            format: Audio format (wav, mp3, etc.)
        
        Returns:
            Data URL string
        """
        mime_types = {
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "ogg": "audio/ogg",
            "webm": "audio/webm"
        }
        
        mime_type = mime_types.get(format.lower(), "audio/wav")
        return f"data:{mime_type};base64,{audio_base64}"
    
    def get_supported_formats(self) -> list:
        """Get list of supported audio formats"""
        return self.supported_formats

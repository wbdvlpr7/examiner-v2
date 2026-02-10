import asyncio
import speech_recognition as sr
import tempfile
import os
from typing import Optional, Tuple

class STTService:
    def __init__(self, language: str = "en-US"):
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300  # Reduce background noise
        self.recognizer.dynamic_energy_threshold = True
    
    async def transcribe_audio(self, audio_bytes: bytes) -> Tuple[Optional[str], float]:
        """Transcribe audio and return text with confidence score"""
        try:
            # Save temporary file
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            
            try:
                # Transcribe
                with sr.AudioFile(tmp_path) as source:
                    # Adjust for ambient noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = self.recognizer.record(source)
                    
                    # Try Google Web Speech API
                    text = await asyncio.to_thread(
                        self.recognizer.recognize_google,
                        audio_data,
                        language=self.language,
                        show_all=False
                    )
                    
                    # Estimate confidence (placeholder - Google doesn't return confidence)
                    confidence = 0.8 if len(text.split()) > 3 else 0.5
                    
                    return text, confidence
                    
            finally:
                # Cleanup temp file
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except sr.UnknownValueError:
            return "Could not understand audio. Please try again.", 0.0
        except sr.RequestError as e:
            return f"Speech service error: {str(e)[:100]}", 0.0
        except Exception as e:
            return f"Error: {str(e)[:100]}", 0.0
    
    async def validate_audio_quality(self, audio_bytes: bytes) -> bool:
        """Validate audio quality"""
        if len(audio_bytes) < 1000:  # Too short
            return False
        
        # Additional validations can be added
        return True

# Singleton instance
stt_service = STTService()
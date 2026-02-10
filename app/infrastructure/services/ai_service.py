import asyncio
from google import genai
from google.genai import types
from app.core.config import settings
from typing import Optional

class AIService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemma-3-27b-it"
    
    async def generate_feedback(
        self, 
        prompt: str, 
        temperature: float = 0.3,
        max_tokens: int = 1500
    ) -> str:
        """Generate AI feedback with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self.client.aio.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                        top_p=0.95,
                        top_k=40
                    )
                )
                return response.text.strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    return f"Error generating feedback: {str(e)[:200]}"
                await asyncio.sleep(1)  # Wait before retry
    
    async def generate_vocab_details(self, word: str) -> str:
        """Generate vocabulary details"""
        prompt = f"""
        Create detailed dictionary entry for: "{word}"
        
        Include:
        1. Word (uppercase)
        2. Pronunciation (IPA)
        3. Part of speech
        4. 2-3 definitions
        5. 3-5 synonyms
        6. 2-3 antonyms
        7. 2-3 example sentences
        8. Common collocations
        
        Format in HTML with <b> tags only.
        Keep response under 1000 words.
        """
        return await self.generate_feedback(prompt, temperature=0.1)
    
    async def generate_paraphrase_all_styles(self, text: str) -> str:
        """Paraphrase in 4 styles"""
        prompt = f"""
        Paraphrase this text in 4 different styles:
        
        Text: "{text}"
        
        Styles:
        1. Academic (formal, complex structures)
        2. Formal (professional, clear)
        3. Casual (conversational, simple)
        4. Creative (imaginative, varied expressions)
        
        Format:
        <b>ACADEMIC:</b> [paraphrased]
        <b>FORMAL:</b> [paraphrased]
        <b>CASUAL:</b> [paraphrased]
        <b>CREATIVE:</b> [paraphrased]
        
        Keep each version 10-50 words.
        """
        return await self.generate_feedback(prompt, temperature=0.4)

# Singleton instance
ai_service = AIService()
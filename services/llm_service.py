"""
services/llm_service.py - LLM interaction service (Gemini, OpenAI, Anthropic)
"""
import os
import json
from utils.helpers import setup_logging

logger = setup_logging()

class LLMService:
    """Interact with multiple LLM providers"""
    
    def __init__(self, provider: str = "gemini"):
        self.provider = provider
        
        if provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("❌ GEMINI_API_KEY not set")
            try:
                import google.genai as genai
                self.client = genai.Client(api_key=api_key)
                self.model = "gemini-2.0-flash-exp"
                logger.info("✅ LLMService: Gemini initialized")
            except ImportError:
                raise ImportError("❌ google-genai not installed")
    
    async def get_completion(self, prompt: str, system_prompt: str = None) -> str:
        """Get text completion from LLM"""
        try:
            if self.provider == "gemini":
                import google.genai as genai
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=genai.types.GenerateContentConfig(temperature=0.3)
                )
                return response.text
        except Exception as e:
            logger.error(f"❌ LLM error: {str(e)}")
            raise
    
    async def get_structured_output(self, prompt: str, system_prompt: str, schema: dict) -> dict:
        """Get structured JSON output from LLM"""
        try:
            if self.provider == "gemini":
                import google.genai as genai
                full_prompt = f"{system_prompt}\n\n{prompt}\n\nIMPORTANT: Return ONLY valid JSON. No markdown."
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=full_prompt,
                    config=genai.types.GenerateContentConfig(
                        temperature=0.0,
                        response_mime_type="application/json",
                        response_schema=schema
                    )
                )
                result = json.loads(response.text)
                return result
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON error: {str(e)}")
            raise ValueError(f"Invalid JSON from LLM: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Structured output error: {str(e)}")
            raise
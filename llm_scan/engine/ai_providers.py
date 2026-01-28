"""AI provider implementations for different LLM APIs."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _fix_json_escapes(content: str) -> str:
    """
    Fix common JSON escape sequence issues.
    
    Handles cases where OpenAI returns JSON with invalid escape sequences
    (e.g., unescaped backslashes in strings like file paths).
    
    Valid JSON escapes: \" \\ \/ \b \f \n \r \t \uXXXX
    """
    import re
    
    # Simple approach: find all \X patterns and check if X is valid
    # Process from right to left to avoid index shifts
    
    # First, temporarily replace valid escapes with placeholders
    placeholders = {}
    counter = 0
    
    def make_placeholder(match):
        nonlocal counter
        placeholder = f"__VALID_ESCAPE_{counter}__"
        placeholders[placeholder] = match.group(0)
        counter += 1
        return placeholder
    
    # Protect valid escapes
    # Unicode escapes: \uXXXX
    content = re.sub(r'\\u[0-9a-fA-F]{4}', make_placeholder, content, flags=re.IGNORECASE)
    # Single char escapes: \" \\ \/ \b \f \n \r \t
    content = re.sub(r'\\(["\\/bfnrt])', make_placeholder, content)
    
    # Now fix any remaining \X (these are invalid)
    def fix_invalid(match):
        return '\\\\' + match.group(1)
    
    content = re.sub(r'\\(.)', fix_invalid, content)
    
    # Restore valid escapes
    for placeholder, original in placeholders.items():
        content = content.replace(placeholder, original)
    
    return content


def _parse_json_with_fallback(content: str) -> Dict[str, Any]:
    """
    Parse JSON content with fallback strategies for malformed JSON.
    
    Args:
        content: JSON string to parse
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        json.JSONDecodeError: If all parsing strategies fail
    """
    # Strategy 1: Try direct parsing
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Try fixing escape sequences
    try:
        fixed_content = _fix_json_escapes(content)
        return json.loads(fixed_content)
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Extract from markdown code blocks
    if "```json" in content:
        json_start = content.find("```json") + 7
        json_end = content.find("```", json_start)
        if json_end > json_start:
            extracted = content[json_start:json_end].strip()
            try:
                return json.loads(extracted)
            except json.JSONDecodeError:
                # Try fixing escapes in extracted content
                try:
                    fixed_extracted = _fix_json_escapes(extracted)
                    return json.loads(fixed_extracted)
                except json.JSONDecodeError:
                    pass
    
    # Strategy 4: Try to find JSON object boundaries
    # Look for first { and last }
    first_brace = content.find('{')
    last_brace = content.rfind('}')
    if first_brace >= 0 and last_brace > first_brace:
        extracted = content[first_brace:last_brace + 1]
        try:
            return json.loads(extracted)
        except json.JSONDecodeError:
            try:
                fixed_extracted = _fix_json_escapes(extracted)
                return json.loads(fixed_extracted)
            except json.JSONDecodeError:
                pass
    
    # All strategies failed, raise original error
    raise json.JSONDecodeError("Failed to parse JSON after all fallback strategies", content, 0)


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def analyze(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a prompt and return structured response.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Dictionary with analysis results
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""

    # Models that support response_format with json_object
    JSON_SUPPORTED_MODELS = {
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-4-0125-preview",
        "gpt-4-1106-preview",
        "gpt-3.5-turbo-0125",
        "gpt-3.5-turbo-1106",
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4o-2024-08-06",
        "gpt-4o-mini-2024-07-18",
    }

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (or use OPENAI_API_KEY env var)
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
        """
        try:
            import openai
            # Set timeout on client to prevent hanging (60 seconds)
            self.client = openai.OpenAI(
                api_key=api_key,
                timeout=60.0,  # 60 second timeout for all requests
            )
            self.model = model
            # Check if model supports JSON response format
            self.supports_json_format = self._model_supports_json_format(model)
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize OpenAI client: {e}")

    def _model_supports_json_format(self, model: str) -> bool:
        """Check if model supports response_format with json_object."""
        # Check exact match
        if model in self.JSON_SUPPORTED_MODELS:
            return True
        # Check if model name starts with a supported prefix
        for supported in self.JSON_SUPPORTED_MODELS:
            if model.startswith(supported.split("-")[0] + "-"):  # e.g., "gpt-4-turbo" matches "gpt-4-turbo-*"
                # For newer models, check if it's a turbo/o variant
                if "turbo" in model or "o" in model:
                    return True
        return False

    def analyze(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze using OpenAI API."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Enhance prompt to request JSON if model doesn't support response_format
            user_prompt = prompt
            if not self.supports_json_format:
                user_prompt = prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON. Do not include any markdown formatting or explanatory text."
            
            messages.append({"role": "user", "content": user_prompt})

            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.1,  # Low temperature for consistent analysis
            }
            
            # Only add response_format for supported models
            if self.supports_json_format:
                request_params["response_format"] = {"type": "json_object"}
            else:
                logger.debug(f"Model {self.model} doesn't support response_format, requesting JSON in prompt")

            logger.debug(f"Calling OpenAI API with model {self.model}...")
            response = self.client.chat.completions.create(**request_params)
            logger.debug("OpenAI API call completed")

            content = response.choices[0].message.content
            return _parse_json_with_fallback(content)

        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}")
            logger.debug(f"Response content (first 500 chars): {content[:500]}")
            # Try fallback parsing (which includes escape fixing)
            try:
                result = _parse_json_with_fallback(content)
                logger.debug("Fallback parsing succeeded")
                return result
            except json.JSONDecodeError as fallback_error:
                logger.error(f"All JSON parsing strategies failed. Original: {e}, Fallback: {fallback_error}")
                logger.debug(f"Full response content length: {len(content)}")
                # Log a snippet around the error location if possible
                if hasattr(e, 'pos') and e.pos < len(content):
                    start = max(0, e.pos - 100)
                    end = min(len(content), e.pos + 100)
                    logger.debug(f"Content around error position {e.pos}: {content[start:end]}")
                raise
        except Exception as e:
            # If error is about response_format, retry without it
            error_str = str(e)
            if "response_format" in error_str.lower() and self.supports_json_format:
                logger.warning(f"Model {self.model} reported response_format error, retrying without it")
                # Retry without response_format
                try:
                    request_params = {
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.1,
                    }
                    logger.debug(f"Retrying OpenAI API call without response_format...")
                    response = self.client.chat.completions.create(**request_params)
                    logger.debug("OpenAI API retry completed")
                    content = response.choices[0].message.content
                    # Try to parse JSON with fallback strategies
                    return _parse_json_with_fallback(content)
                except Exception as retry_error:
                    logger.error(f"Retry also failed: {retry_error}")
                    raise
            logger.error(f"OpenAI API error: {e}")
            raise


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
            model: Model name (e.g., "claude-3-opus-20240229", "claude-3-sonnet-20240229")
        """
        try:
            import anthropic
            # Set timeout on client to prevent hanging (60 seconds)
            self.client = anthropic.Anthropic(
                api_key=api_key,
                timeout=60.0,  # 60 second timeout for all requests
            )
            self.model = model
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Anthropic client: {e}")

    def analyze(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Analyze using Anthropic API."""
        try:
            # Combine system prompt with user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            logger.debug(f"Calling Anthropic API with model {self.model}...")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.1,
                messages=[{"role": "user", "content": full_prompt}],
            )
            logger.debug("Anthropic API call completed")

            content = response.content[0].text

            # Try to parse as JSON with fallback strategies
            try:
                return _parse_json_with_fallback(content)
            except json.JSONDecodeError:
                # If no JSON found, try to parse the text response
                logger.warning("Anthropic response not in JSON format, attempting to parse")
                # Fallback: return a structured response
                return {
                    "is_false_positive": "false positive" in content.lower(),
                    "confidence": 0.5,
                    "reasoning": content,
                }

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise


def create_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> AIProvider:
    """
    Factory function to create an AI provider.

    Args:
        provider_name: Provider name ("openai", "anthropic", "local")
        api_key: API key (or use environment variables)
        model: Model name (optional, uses defaults)

    Returns:
        AIProvider instance
    """
    if provider_name.lower() == "openai":
        return OpenAIProvider(
            api_key=api_key or None,
            model=model or "gpt-4",
        )
    elif provider_name.lower() == "anthropic":
        return AnthropicProvider(
            api_key=api_key or None,
            model=model or "claude-3-opus-20240229",
        )
    else:
        raise ValueError(f"Unknown AI provider: {provider_name}")

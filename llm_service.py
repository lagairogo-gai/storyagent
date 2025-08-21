"""
LLM Service for handling multiple Large Language Model providers
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, AsyncGenerator
from datetime import datetime
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# LangChain imports
from langchain.llms.base import LLM
from langchain.chat_models.base import BaseChatModel
from langchain.schema import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema.output import LLMResult

# Provider-specific imports
try:
    from langchain.chat_models import ChatOpenAI
    from langchain.llms import OpenAI
except ImportError:
    ChatOpenAI = None
    OpenAI = None

try:
    from langchain.chat_models import AzureChatOpenAI
except ImportError:
    AzureChatOpenAI = None

try:
    from langchain.chat_models import ChatGooglePalm
    from langchain.llms import GooglePalm
except ImportError:
    ChatGooglePalm = None
    GooglePalm = None

try:
    from langchain.chat_models import ChatAnthropic
except ImportError:
    ChatAnthropic = None

try:
    from langchain.llms import Ollama
    from langchain.chat_models import ChatOllama
except ImportError:
    Ollama = None
    ChatOllama = None

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMProvider(str, Enum):
    """Supported LLM providers"""
    OPENAI = "openai"
    AZURE_OPENAI = "azure"
    GOOGLE_GEMINI = "gemini"
    ANTHROPIC_CLAUDE = "claude"
    OLLAMA = "ollama"


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    latency: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class LLMUsageStats:
    """LLM usage statistics"""
    total_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    average_latency: float = 0.0
    error_count: int = 0
    last_request: Optional[datetime] = None


class LLMCallbackHandler(BaseCallbackHandler):
    """Callback handler for tracking LLM usage"""
    
    def __init__(self):
        self.start_time = None
        self.tokens_used = 0
        self.cost = 0.0
        
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts running"""
        self.start_time = time.time()
        
    def on_llm_end(self, response: LLMResult, **kwargs) -> None:
        """Called when LLM ends running"""
        if response.llm_output:
            self.tokens_used = response.llm_output.get("token_usage", {}).get("total_tokens", 0)
            
    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs) -> None:
        """Called when LLM errors"""
        logger.error(f"LLM error: {error}")


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, provider_name: str, config: Dict[str, Any]):
        self.provider_name = provider_name
        self.config = config
        self.usage_stats = LLMUsageStats()
        
    @abstractmethod
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming text using Claude"""
        try:
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            self.chat_model.temperature = temperature
            if max_tokens:
                self.chat_model.max_tokens = max_tokens
            
            async for token in self.chat_model.astream(messages):
                if hasattr(token, 'content'):
                    yield token.content
                else:
                    yield str(token)
                    
        except Exception as e:
            logger.error(f"Claude streaming error: {e}")
            raise


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("gemini", config)
        self.chat_model = None
        
    async def initialize(self) -> bool:
        """Initialize Gemini client"""
        try:
            if not ChatGooglePalm:
                raise ImportError("Google AI package not installed")
                
            api_key = self.config.get("api_key")
            if not api_key:
                raise ValueError("Gemini API key not provided")
            
            self.chat_model = ChatGooglePalm(
                google_api_key=api_key,
                model_name=self.config.get("model", "gemini-pro"),
                temperature=self.config.get("temperature", 0.1),
                callbacks=[LLMCallbackHandler()]
            )
            
            # Test the connection
            await self.chat_model.apredict("Hello")
            logger.info("✅ Gemini provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini provider: {e}")
            return False
    
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text using Gemini"""
        start_time = time.time()
        
        try:
            # Gemini handles system messages differently
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"
            
            self.chat_model.temperature = temperature
            
            response = await self.chat_model.apredict(full_prompt)
            
            latency = time.time() - start_time
            
            llm_response = LLMResponse(
                content=response,
                provider="gemini",
                model=self.config.get("model", "gemini-pro"),
                latency=latency
            )
            
            self.update_usage_stats(llm_response)
            return llm_response
            
        except Exception as e:
            self.usage_stats.error_count += 1
            logger.error(f"Gemini generation error: {e}")
            raise
    
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming text using Gemini"""
        try:
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"
            
            self.chat_model.temperature = temperature
            
            # Gemini streaming implementation would go here
            # For now, simulate streaming by yielding chunks
            response = await self.chat_model.apredict(full_prompt)
            
            # Simulate streaming by breaking response into chunks
            chunk_size = 20
            for i in range(0, len(response), chunk_size):
                chunk = response[i:i + chunk_size]
                yield chunk
                await asyncio.sleep(0.01)  # Small delay to simulate streaming
                
        except Exception as e:
            logger.error(f"Gemini streaming error: {e}")
            raise


class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local models"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("ollama", config)
        self.chat_model = None
        
    async def initialize(self) -> bool:
        """Initialize Ollama client"""
        try:
            if not ChatOllama:
                raise ImportError("Ollama package not installed")
            
            base_url = self.config.get("base_url", "http://localhost:11434")
            model = self.config.get("model", "llama2")
            
            self.chat_model = ChatOllama(
                base_url=base_url,
                model=model,
                temperature=self.config.get("temperature", 0.1),
                callbacks=[LLMCallbackHandler()]
            )
            
            # Test the connection
            await self.chat_model.apredict("Hello")
            logger.info("✅ Ollama provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama provider: {e}")
            return False
    
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text using Ollama"""
        start_time = time.time()
        
        try:
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            self.chat_model.temperature = temperature
            
            response = await self.chat_model.agenerate([messages])
            content = response.generations[0][0].text
            
            latency = time.time() - start_time
            
            llm_response = LLMResponse(
                content=content,
                provider="ollama",
                model=self.config.get("model", "llama2"),
                latency=latency,
                cost=0.0  # Local models are free
            )
            
            self.update_usage_stats(llm_response)
            return llm_response
            
        except Exception as e:
            self.usage_stats.error_count += 1
            logger.error(f"Ollama generation error: {e}")
            raise
    
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming text using Ollama"""
        try:
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            self.chat_model.temperature = temperature
            
            async for token in self.chat_model.astream(messages):
                if hasattr(token, 'content'):
                    yield token.content
                else:
                    yield str(token)
                    
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise


class LLMService:
    """
    Main LLM service for managing multiple providers
    """
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.default_provider = settings.DEFAULT_LLM_PROVIDER
        self.initialized = False
        
    async def initialize(self):
        """Initialize all configured LLM providers"""
        try:
            logger.info("🚀 Initializing LLM providers...")
            
            # Initialize providers based on available configurations
            provider_configs = {
                LLMProvider.OPENAI: settings.llm_config if settings.DEFAULT_LLM_PROVIDER == "openai" else None,
                LLMProvider.AZURE_OPENAI: self._get_azure_config(),
                LLMProvider.ANTHROPIC_CLAUDE: self._get_claude_config(),
                LLMProvider.GOOGLE_GEMINI: self._get_gemini_config(),
                LLMProvider.OLLAMA: self._get_ollama_config()
            }
            
            # Create provider instances
            provider_classes = {
                LLMProvider.OPENAI: OpenAIProvider,
                LLMProvider.AZURE_OPENAI: AzureOpenAIProvider,
                LLMProvider.ANTHROPIC_CLAUDE: ClaudeProvider,
                LLMProvider.GOOGLE_GEMINI: GeminiProvider,
                LLMProvider.OLLAMA: OllamaProvider
            }
            
            initialized_count = 0
            for provider_name, config in provider_configs.items():
                if config and config.get("api_key") or provider_name == LLMProvider.OLLAMA:
                    try:
                        provider_class = provider_classes[provider_name]
                        provider = provider_class(config)
                        
                        if await provider.initialize():
                            self.providers[provider_name.value] = provider
                            initialized_count += 1
                            logger.info(f"✅ {provider_name.value} provider initialized")
                        else:
                            logger.warning(f"⚠️ Failed to initialize {provider_name.value} provider")
                            
                    except Exception as e:
                        logger.error(f"❌ Error initializing {provider_name.value}: {e}")
            
            if initialized_count == 0:
                logger.error("❌ No LLM providers were successfully initialized")
                return False
            
            # Verify default provider is available
            if self.default_provider not in self.providers:
                # Fall back to first available provider
                self.default_provider = list(self.providers.keys())[0]
                logger.warning(f"⚠️ Default provider not available, using {self.default_provider}")
            
            self.initialized = True
            logger.info(f"✅ LLM service initialized with {initialized_count} providers")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM service: {e}")
            return False
    
    def _get_azure_config(self) -> Optional[Dict[str, Any]]:
        """Get Azure OpenAI configuration"""
        if all([settings.AZURE_OPENAI_API_KEY, settings.AZURE_OPENAI_ENDPOINT, settings.AZURE_OPENAI_DEPLOYMENT_NAME]):
            return {
                "api_key": settings.AZURE_OPENAI_API_KEY,
                "endpoint": settings.AZURE_OPENAI_ENDPOINT,
                "deployment_name": settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                "api_version": settings.AZURE_OPENAI_API_VERSION
            }
        return None
    
    def _get_claude_config(self) -> Optional[Dict[str, Any]]:
        """Get Claude configuration"""
        if settings.CLAUDE_API_KEY:
            return {
                "api_key": settings.CLAUDE_API_KEY,
                "model": settings.CLAUDE_MODEL
            }
        return None
    
    def _get_gemini_config(self) -> Optional[Dict[str, Any]]:
        """Get Gemini configuration"""
        if settings.GEMINI_API_KEY:
            return {
                "api_key": settings.GEMINI_API_KEY,
                "model": settings.GEMINI_MODEL
            }
        return None
    
    def _get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama configuration"""
        return {
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL
        }
    
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate text using specified or default provider
        """
        if not self.initialized:
            raise RuntimeError("LLM service not initialized")
        
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            available_providers = list(self.providers.keys())
            raise ValueError(f"Provider '{provider_name}' not available. Available: {available_providers}")
        
        llm_provider = self.providers[provider_name]
        
        try:
            response = await llm_provider.generate_text(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            logger.info(f"Generated text using {provider_name}: {len(response.content)} characters")
            return response
            
        except Exception as e:
            logger.error(f"Text generation failed with {provider_name}: {e}")
            
            # Try fallback provider if main provider fails
            if len(self.providers) > 1:
                fallback_providers = [p for p in self.providers.keys() if p != provider_name]
                for fallback in fallback_providers:
                    try:
                        logger.info(f"Trying fallback provider: {fallback}")
                        response = await self.providers[fallback].generate_text(
                            prompt=prompt,
                            system_message=system_message,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            **kwargs
                        )
                        logger.info(f"Fallback successful with {fallback}")
                        return response
                    except Exception as fallback_error:
                        logger.error(f"Fallback {fallback} also failed: {fallback_error}")
                        continue
            
            raise e
    
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        provider: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming text using specified or default provider
        """
        if not self.initialized:
            raise RuntimeError("LLM service not initialized")
        
        provider_name = provider or self.default_provider
        
        if provider_name not in self.providers:
            available_providers = list(self.providers.keys())
            raise ValueError(f"Provider '{provider_name}' not available. Available: {available_providers}")
        
        llm_provider = self.providers[provider_name]
        
        try:
            async for token in llm_provider.generate_streaming(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            ):
                yield token
                
        except Exception as e:
            logger.error(f"Streaming generation failed with {provider_name}: {e}")
            raise
    
    async def generate_user_stories(
        self,
        requirements: str,
        context: Optional[str] = None,
        project_preferences: Optional[Dict[str, Any]] = None,
        provider: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate user stories from requirements
        """
        system_message = """
        You are an expert business analyst and product manager. Your task is to generate well-structured user stories from the given requirements.
        
        Guidelines:
        1. Follow the format: "As a [type of user], I want [goal] so that [reason]"
        2. Make stories specific, measurable, and testable
        3. Include acceptance criteria for each story
        4. Assign appropriate priority levels (High, Medium, Low)
        5. Estimate story points (1, 2, 3, 5, 8, 13, 21)
        6. Break down large features into smaller, manageable stories
        7. Ensure stories are independent and deliverable
        
        Return the response as a JSON array of user stories with the following structure:
        [
            {
                "title": "Brief story title",
                "description": "As a [user], I want [goal] so that [reason]",
                "acceptance_criteria": ["Given...", "When...", "Then..."],
                "priority": "High|Medium|Low",
                "story_points": 1-21,
                "labels": ["feature", "enhancement", etc.],
                "epic": "Epic name if applicable"
            }
        ]
        """
        
        prompt = f"""
        Requirements:
        {requirements}
        
        {f"Additional Context: {context}" if context else ""}
        
        Project Preferences:
        {json.dumps(project_preferences or {}, indent=2)}
        
        Generate user stories based on these requirements.
        """
        
        try:
            response = await self.generate_text(
                prompt=prompt,
                system_message=system_message,
                provider=provider,
                temperature=0.1,
                max_tokens=4000
            )
            
            # Parse JSON response
            try:
                user_stories = json.loads(response.content)
                logger.info(f"Generated {len(user_stories)} user stories")
                return user_stories
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from response
                import re
                json_match = re.search(r'\[.*\]', response.content, re.DOTALL)
                if json_match:
                    user_stories = json.loads(json_match.group())
                    return user_stories
                else:
                    logger.error("Failed to parse user stories JSON")
                    return []
                    
        except Exception as e:
            logger.error(f"User story generation failed: {e}")
            raise
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_provider_stats(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get usage statistics for provider(s)"""
        if provider:
            if provider in self.providers:
                return {
                    "provider": provider,
                    "stats": self.providers[provider].usage_stats.__dict__
                }
            else:
                raise ValueError(f"Provider '{provider}' not found")
        else:
            return {
                provider_name: provider.usage_stats.__dict__
                for provider_name, provider in self.providers.items()
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
        health_status = {
            "initialized": self.initialized,
            "default_provider": self.default_provider,
            "providers": {}
        }
        
        for provider_name, provider in self.providers.items():
            try:
                # Quick health check with simple prompt
                start_time = time.time()
                await provider.generate_text("Hello", max_tokens=10)
                latency = time.time() - start_time
                
                health_status["providers"][provider_name] = {
                    "status": "healthy",
                    "latency": latency,
                    "error_count": provider.usage_stats.error_count,
                    "total_requests": provider.usage_stats.total_requests
                }
            except Exception as e:
                health_status["providers"][provider_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "error_count": provider.usage_stats.error_count
                }
        
        return health_status
    
    async def close(self):
        """Clean up resources"""
        logger.info("🔄 Shutting down LLM service...")
        self.providers.clear()
        self.initialized = False
        logger.info("✅ LLM service shut down") initialize(self) -> bool:
        """Initialize the provider"""
        pass
        
    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text from prompt"""
        pass
        
    @abstractmethod
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming text from prompt"""
        pass
        
    def update_usage_stats(self, response: LLMResponse):
        """Update usage statistics"""
        self.usage_stats.total_requests += 1
        if response.tokens_used:
            self.usage_stats.total_tokens += response.tokens_used
        if response.cost:
            self.usage_stats.total_cost += response.cost
        if response.latency:
            # Update running average
            total_latency = self.usage_stats.average_latency * (self.usage_stats.total_requests - 1)
            self.usage_stats.average_latency = (total_latency + response.latency) / self.usage_stats.total_requests
        self.usage_stats.last_request = datetime.utcnow()


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("openai", config)
        self.client = None
        self.chat_model = None
        
    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        try:
            if not ChatOpenAI:
                raise ImportError("OpenAI package not installed")
                
            api_key = self.config.get("api_key")
            if not api_key:
                raise ValueError("OpenAI API key not provided")
                
            self.chat_model = ChatOpenAI(
                openai_api_key=api_key,
                model_name=self.config.get("model", "gpt-4-turbo-preview"),
                temperature=self.config.get("temperature", 0.1),
                max_tokens=self.config.get("max_tokens"),
                callbacks=[LLMCallbackHandler()]
            )
            
            # Test the connection
            await self.chat_model.apredict("Hello")
            logger.info("✅ OpenAI provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI provider: {e}")
            return False
    
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text using OpenAI"""
        start_time = time.time()
        
        try:
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            # Update model parameters
            self.chat_model.temperature = temperature
            if max_tokens:
                self.chat_model.max_tokens = max_tokens
            
            response = await self.chat_model.agenerate([messages])
            content = response.generations[0][0].text
            
            latency = time.time() - start_time
            
            # Extract usage information
            tokens_used = None
            cost = None
            if response.llm_output and "token_usage" in response.llm_output:
                token_usage = response.llm_output["token_usage"]
                tokens_used = token_usage.get("total_tokens")
                
                # Estimate cost (approximate)
                if tokens_used:
                    cost = self._estimate_cost(tokens_used)
            
            llm_response = LLMResponse(
                content=content,
                provider="openai",
                model=self.config.get("model", "gpt-4-turbo-preview"),
                tokens_used=tokens_used,
                cost=cost,
                latency=latency,
                metadata=response.llm_output
            )
            
            self.update_usage_stats(llm_response)
            return llm_response
            
        except Exception as e:
            self.usage_stats.error_count += 1
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming text using OpenAI"""
        try:
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            # Update model parameters
            self.chat_model.temperature = temperature
            if max_tokens:
                self.chat_model.max_tokens = max_tokens
            
            async for token in self.chat_model.astream(messages):
                if hasattr(token, 'content'):
                    yield token.content
                else:
                    yield str(token)
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estimate cost based on token usage"""
        # GPT-4 pricing (approximate, as of 2024)
        input_cost_per_1k = 0.03
        output_cost_per_1k = 0.06
        
        # Assume 50/50 input/output split for estimation
        return (tokens / 1000) * ((input_cost_per_1k + output_cost_per_1k) / 2)


class AzureOpenAIProvider(BaseLLMProvider):
    """Azure OpenAI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("azure", config)
        self.chat_model = None
        
    async def initialize(self) -> bool:
        """Initialize Azure OpenAI client"""
        try:
            if not AzureChatOpenAI:
                raise ImportError("Azure OpenAI package not installed")
                
            required_fields = ["api_key", "endpoint", "deployment_name"]
            for field in required_fields:
                if not self.config.get(field):
                    raise ValueError(f"Azure OpenAI {field} not provided")
            
            self.chat_model = AzureChatOpenAI(
                openai_api_key=self.config["api_key"],
                azure_endpoint=self.config["endpoint"],
                deployment_name=self.config["deployment_name"],
                openai_api_version=self.config.get("api_version", "2024-02-15-preview"),
                temperature=self.config.get("temperature", 0.1),
                callbacks=[LLMCallbackHandler()]
            )
            
            # Test the connection
            await self.chat_model.apredict("Hello")
            logger.info("✅ Azure OpenAI provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Azure OpenAI provider: {e}")
            return False
    
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text using Azure OpenAI"""
        start_time = time.time()
        
        try:
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            self.chat_model.temperature = temperature
            if max_tokens:
                self.chat_model.max_tokens = max_tokens
            
            response = await self.chat_model.agenerate([messages])
            content = response.generations[0][0].text
            
            latency = time.time() - start_time
            tokens_used = None
            
            if response.llm_output and "token_usage" in response.llm_output:
                tokens_used = response.llm_output["token_usage"].get("total_tokens")
            
            llm_response = LLMResponse(
                content=content,
                provider="azure",
                model=self.config.get("deployment_name", "gpt-4"),
                tokens_used=tokens_used,
                latency=latency,
                metadata=response.llm_output
            )
            
            self.update_usage_stats(llm_response)
            return llm_response
            
        except Exception as e:
            self.usage_stats.error_count += 1
            logger.error(f"Azure OpenAI generation error: {e}")
            raise
    
    async def generate_streaming(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming text using Azure OpenAI"""
        try:
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            self.chat_model.temperature = temperature
            if max_tokens:
                self.chat_model.max_tokens = max_tokens
            
            async for token in self.chat_model.astream(messages):
                if hasattr(token, 'content'):
                    yield token.content
                else:
                    yield str(token)
                    
        except Exception as e:
            logger.error(f"Azure OpenAI streaming error: {e}")
            raise


class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("claude", config)
        self.chat_model = None
        
    async def initialize(self) -> bool:
        """Initialize Claude client"""
        try:
            if not ChatAnthropic:
                raise ImportError("Anthropic package not installed")
                
            api_key = self.config.get("api_key")
            if not api_key:
                raise ValueError("Claude API key not provided")
            
            self.chat_model = ChatAnthropic(
                anthropic_api_key=api_key,
                model=self.config.get("model", "claude-3-sonnet-20240229"),
                temperature=self.config.get("temperature", 0.1),
                max_tokens=self.config.get("max_tokens", 4000),
                callbacks=[LLMCallbackHandler()]
            )
            
            # Test the connection
            await self.chat_model.apredict("Hello")
            logger.info("✅ Claude provider initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Claude provider: {e}")
            return False
    
    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate text using Claude"""
        start_time = time.time()
        
        try:
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            
            self.chat_model.temperature = temperature
            if max_tokens:
                self.chat_model.max_tokens = max_tokens
            
            response = await self.chat_model.agenerate([messages])
            content = response.generations[0][0].text
            
            latency = time.time() - start_time
            
            llm_response = LLMResponse(
                content=content,
                provider="claude",
                model=self.config.get("model", "claude-3-sonnet"),
                latency=latency,
                metadata=response.llm_output
            )
            
            self.update_usage_stats(llm_response)
            return llm_response
            
        except Exception as e:
            self.usage_stats.error_count += 1
            logger.error(f"Claude generation error: {e}")
            raise
    
    async def
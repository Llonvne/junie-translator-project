"""
Translation Manager Module - Manages translation requests and responses.

This module provides a manager for translation requests, including batching,
rate limiting, and caching of translations.

翻译管理器模块 - 管理翻译请求和响应。

该模块提供了一个翻译请求的管理器，包括批处理、速率限制和翻译缓存。
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
import hashlib
import json

from junie_translator_project.entity.srt import SubtitleEntry, SrtFile
from junie_translator_project.entity.config import AppConfig
from junie_translator_project.ai.translator import TranslatorService, TranslatorFactory

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class TranslationRequest:
    """
    Represents a translation request.
    
    表示翻译请求。
    """
    text: str
    target_language: str
    source_language: str = "auto"
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate a request ID if not provided."""
        if not self.request_id:
            # Generate a unique ID based on text and languages
            hash_input = f"{self.text}|{self.source_language}|{self.target_language}"
            self.request_id = hashlib.md5(hash_input.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the translation request to a dictionary for serialization."""
        return {
            "text": self.text,
            "target_language": self.target_language,
            "source_language": self.source_language,
            "request_id": self.request_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationRequest':
        """Create a translation request from a dictionary."""
        return cls(
            text=data["text"],
            target_language=data["target_language"],
            source_language=data.get("source_language", "auto"),
            request_id=data.get("request_id"),
            metadata=data.get("metadata", {})
        )


@dataclass
class TranslationResponse:
    """
    Represents a translation response.
    
    表示翻译响应。
    """
    request_id: str
    translated_text: str
    source_text: str
    target_language: str
    source_language: str
    success: bool = True
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the translation response to a dictionary for serialization."""
        return {
            "request_id": self.request_id,
            "translated_text": self.translated_text,
            "source_text": self.source_text,
            "target_language": self.target_language,
            "source_language": self.source_language,
            "success": self.success,
            "error_message": self.error_message,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranslationResponse':
        """Create a translation response from a dictionary."""
        return cls(
            request_id=data["request_id"],
            translated_text=data["translated_text"],
            source_text=data["source_text"],
            target_language=data["target_language"],
            source_language=data["source_language"],
            success=data.get("success", True),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def error(cls, request: TranslationRequest, error_message: str) -> 'TranslationResponse':
        """Create an error response for a translation request."""
        return cls(
            request_id=request.request_id,
            translated_text="",
            source_text=request.text,
            target_language=request.target_language,
            source_language=request.source_language,
            success=False,
            error_message=error_message,
            metadata=request.metadata
        )


class TranslationCache:
    """
    Cache for translation results to avoid redundant translations.
    
    翻译结果缓存，避免重复翻译。
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the translation cache.
        
        Args:
            max_size: Maximum number of entries in the cache
        """
        self.cache: Dict[str, TranslationResponse] = {}
        self.max_size = max_size
        self.access_times: Dict[str, float] = {}
    
    def _generate_key(self, text: str, target_language: str, source_language: str = "auto") -> str:
        """Generate a cache key for a translation request."""
        return hashlib.md5(f"{text}|{source_language}|{target_language}".encode()).hexdigest()
    
    def get(self, text: str, target_language: str, source_language: str = "auto") -> Optional[TranslationResponse]:
        """
        Get a cached translation response if available.
        
        Args:
            text: The text to translate
            target_language: The target language
            source_language: The source language (default: "auto")
            
        Returns:
            The cached translation response if available, None otherwise
        """
        key = self._generate_key(text, target_language, source_language)
        if key in self.cache:
            # Update access time
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def put(self, response: TranslationResponse) -> None:
        """
        Add a translation response to the cache.
        
        Args:
            response: The translation response to cache
        """
        key = self._generate_key(response.source_text, response.target_language, response.source_language)
        
        # If cache is full, remove least recently used entry
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        self.cache[key] = response
        self.access_times[key] = time.time()
    
    def _evict_lru(self) -> None:
        """Evict the least recently used entry from the cache."""
        if not self.access_times:
            return
        
        # Find the key with the oldest access time
        oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        
        # Remove from cache and access times
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        self.access_times.clear()
    
    def size(self) -> int:
        """Get the current size of the cache."""
        return len(self.cache)


class RateLimiter:
    """
    Rate limiter for translation requests.
    
    翻译请求的速率限制器。
    """
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            requests_per_minute: Maximum number of requests per minute
        """
        self.requests_per_minute = requests_per_minute
        self.request_times: List[float] = []
        self.lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """
        Acquire permission to make a request, waiting if necessary.
        
        This method will block until a request slot is available.
        """
        async with self.lock:
            now = time.time()
            
            # Remove request times older than 1 minute
            self.request_times = [t for t in self.request_times if now - t < 60]
            
            # If we've reached the limit, wait until a slot is available
            if len(self.request_times) >= self.requests_per_minute:
                # Calculate how long to wait
                oldest_time = min(self.request_times)
                wait_time = 60 - (now - oldest_time)
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    await asyncio.sleep(wait_time)
            
            # Add current time to request times
            self.request_times.append(time.time())
    
    def reset(self) -> None:
        """Reset the rate limiter."""
        self.request_times.clear()


class TranslationManager:
    """
    Manager for translation requests and responses.
    
    翻译请求和响应的管理器。
    """
    
    def __init__(
        self,
        translator: Optional[TranslatorService] = None,
        config: Optional[AppConfig] = None,
        cache_size: int = 1000,
        requests_per_minute: int = 60,
        batch_size: int = 10,
        batch_wait_time: float = 0.5
    ):
        """
        Initialize the translation manager.
        
        Args:
            translator: The translator service to use (if None, one will be created from config)
            config: Application configuration (if None, default config will be used)
            cache_size: Maximum number of entries in the translation cache
            requests_per_minute: Maximum number of requests per minute
            batch_size: Maximum number of texts to translate in a single batch
            batch_wait_time: Maximum time to wait for more texts before processing a batch
        """
        self.config = config or AppConfig()
        self.translator = translator or TranslatorFactory.create_translator_from_config(
            config=self.config.ai_api_service,
            model=self.config.model,
            prompt_style=self.config.prompt_style,
            enable_post_check=self.config.enable_post_check
        )
        
        self.cache = TranslationCache(max_size=cache_size)
        self.rate_limiter = RateLimiter(requests_per_minute=requests_per_minute)
        
        self.batch_size = batch_size
        self.batch_wait_time = batch_wait_time
        
        self.batch_queue: List[Tuple[TranslationRequest, asyncio.Future]] = []
        self.batch_lock = asyncio.Lock()
        self.batch_event = asyncio.Event()
        self.batch_task: Optional[asyncio.Task] = None
        
        logger.info(f"Initialized TranslationManager with batch_size={batch_size}, batch_wait_time={batch_wait_time}")
    
    async def start(self) -> None:
        """Start the translation manager's background tasks."""
        if self.batch_task is None or self.batch_task.done():
            self.batch_task = asyncio.create_task(self._batch_processor())
            logger.info("Started translation manager batch processor")
    
    async def stop(self) -> None:
        """Stop the translation manager's background tasks."""
        if self.batch_task and not self.batch_task.done():
            self.batch_task.cancel()
            try:
                await self.batch_task
            except asyncio.CancelledError:
                pass
            self.batch_task = None
            logger.info("Stopped translation manager batch processor")
    
    async def translate(self, text: str, target_language: str, source_language: str = "auto") -> TranslationResponse:
        """
        Translate a single text.
        
        Args:
            text: The text to translate
            target_language: The target language
            source_language: The source language (default: "auto")
            
        Returns:
            The translation response
        """
        # Create a translation request
        request = TranslationRequest(
            text=text,
            target_language=target_language,
            source_language=source_language
        )
        
        # Check cache first
        cached_response = self.cache.get(text, target_language, source_language)
        if cached_response:
            logger.debug(f"Cache hit for request {request.request_id}")
            return cached_response
        
        # Acquire rate limiter permission
        await self.rate_limiter.acquire()
        
        try:
            # Translate the text
            translated_text = await self.translator.translate_async(text, target_language)
            
            # Create and cache the response
            response = TranslationResponse(
                request_id=request.request_id,
                translated_text=translated_text,
                source_text=text,
                target_language=target_language,
                source_language=source_language
            )
            self.cache.put(response)
            
            return response
        except Exception as e:
            logger.error(f"Error translating text: {e}", exc_info=True)
            return TranslationResponse.error(request, str(e))
    
    async def translate_batch(
        self, 
        texts: List[str], 
        target_language: str, 
        source_language: str = "auto"
    ) -> List[TranslationResponse]:
        """
        Translate a batch of texts.
        
        Args:
            texts: The texts to translate
            target_language: The target language
            source_language: The source language (default: "auto")
            
        Returns:
            List of translation responses
        """
        # Create translation requests
        requests = [
            TranslationRequest(
                text=text,
                target_language=target_language,
                source_language=source_language
            )
            for text in texts
        ]
        
        # Check cache for each request
        responses: List[Optional[TranslationResponse]] = [
            self.cache.get(request.text, request.target_language, request.source_language)
            for request in requests
        ]
        
        # Find requests that need translation
        uncached_indices = [i for i, response in enumerate(responses) if response is None]
        if not uncached_indices:
            # All requests were cached
            return [r for r in responses if r is not None]
        
        # Acquire rate limiter permission
        await self.rate_limiter.acquire()
        
        try:
            # Get texts that need translation
            uncached_texts = [texts[i] for i in uncached_indices]
            
            # Translate uncached texts
            translated_texts = await self.translator.batch_translate_async(uncached_texts, target_language)
            
            # Create responses for uncached texts
            for i, translated_text in zip(uncached_indices, translated_texts):
                request = requests[i]
                response = TranslationResponse(
                    request_id=request.request_id,
                    translated_text=translated_text,
                    source_text=request.text,
                    target_language=target_language,
                    source_language=source_language
                )
                self.cache.put(response)
                responses[i] = response
            
            return [r for r in responses if r is not None]
        except Exception as e:
            logger.error(f"Error batch translating texts: {e}", exc_info=True)
            
            # Create error responses for uncached texts
            for i in uncached_indices:
                request = requests[i]
                responses[i] = TranslationResponse.error(request, str(e))
            
            return [r for r in responses if r is not None]
    
    async def translate_queued(self, text: str, target_language: str, source_language: str = "auto") -> TranslationResponse:
        """
        Queue a text for translation in a batch.
        
        This method adds the text to a queue and returns a future that will be resolved
        when the text is translated as part of a batch.
        
        Args:
            text: The text to translate
            target_language: The target language
            source_language: The source language (default: "auto")
            
        Returns:
            The translation response
        """
        # Create a translation request
        request = TranslationRequest(
            text=text,
            target_language=target_language,
            source_language=source_language
        )
        
        # Check cache first
        cached_response = self.cache.get(text, target_language, source_language)
        if cached_response:
            logger.debug(f"Cache hit for request {request.request_id}")
            return cached_response
        
        # Create a future for the response
        future: asyncio.Future[TranslationResponse] = asyncio.Future()
        
        # Add the request to the batch queue
        async with self.batch_lock:
            self.batch_queue.append((request, future))
            self.batch_event.set()  # Signal that there's a new request
        
        # Make sure the batch processor is running
        await self.start()
        
        # Wait for the future to be resolved
        return await future
    
    async def _batch_processor(self) -> None:
        """
        Background task that processes batches of translation requests.
        
        This task waits for requests to be added to the queue, then processes them
        in batches when either the batch size is reached or the batch wait time has elapsed.
        """
        try:
            while True:
                # Wait for a request to be added to the queue
                if not self.batch_queue:
                    self.batch_event.clear()
                    await self.batch_event.wait()
                
                # Wait for more requests or until batch_wait_time has elapsed
                try:
                    await asyncio.wait_for(self.batch_event.wait(), self.batch_wait_time)
                except asyncio.TimeoutError:
                    pass
                
                # Process the batch
                async with self.batch_lock:
                    if not self.batch_queue:
                        continue
                    
                    # Take up to batch_size requests from the queue
                    batch = self.batch_queue[:self.batch_size]
                    self.batch_queue = self.batch_queue[self.batch_size:]
                    
                    # If there are still items in the queue, keep the event set
                    if self.batch_queue:
                        self.batch_event.set()
                    else:
                        self.batch_event.clear()
                
                # Extract requests and futures
                requests, futures = zip(*batch)
                
                # Group requests by target language
                by_language: Dict[Tuple[str, str], List[Tuple[int, TranslationRequest]]] = {}
                for i, request in enumerate(requests):
                    key = (request.target_language, request.source_language)
                    if key not in by_language:
                        by_language[key] = []
                    by_language[key].append((i, request))
                
                # Process each language group
                for (target_lang, source_lang), group in by_language.items():
                    indices, group_requests = zip(*group)
                    
                    try:
                        # Acquire rate limiter permission
                        await self.rate_limiter.acquire()
                        
                        # Get texts for this group
                        texts = [request.text for request in group_requests]
                        
                        # Translate texts
                        translated_texts = await self.translator.batch_translate_async(texts, target_lang)
                        
                        # Create responses and resolve futures
                        for i, request, translated_text in zip(indices, group_requests, translated_texts):
                            response = TranslationResponse(
                                request_id=request.request_id,
                                translated_text=translated_text,
                                source_text=request.text,
                                target_language=target_lang,
                                source_language=source_lang
                            )
                            self.cache.put(response)
                            futures[i].set_result(response)
                    except Exception as e:
                        logger.error(f"Error processing batch: {e}", exc_info=True)
                        
                        # Set error responses for all requests in this group
                        for i, request in zip(indices, group_requests):
                            if not futures[i].done():
                                futures[i].set_result(TranslationResponse.error(request, str(e)))
        except asyncio.CancelledError:
            # Task was cancelled, resolve any pending futures with errors
            async with self.batch_lock:
                for request, future in self.batch_queue:
                    if not future.done():
                        future.set_result(TranslationResponse.error(
                            request, "Translation manager was stopped"
                        ))
                self.batch_queue.clear()
            raise
        except Exception as e:
            logger.error(f"Batch processor encountered an error: {e}", exc_info=True)
            
            # Resolve any pending futures with errors
            async with self.batch_lock:
                for request, future in self.batch_queue:
                    if not future.done():
                        future.set_result(TranslationResponse.error(
                            request, f"Batch processor error: {e}"
                        ))
                self.batch_queue.clear()
    
    async def translate_srt_file(self, srt_file: SrtFile, target_language: str) -> SrtFile:
        """
        Translate an SRT file.
        
        Args:
            srt_file: The SRT file to translate
            target_language: The target language
            
        Returns:
            A new SRT file with translated entries
        """
        # Create a new SRT file for the translation
        translated_file = SrtFile(
            path=str(srt_file.path).replace(
                srt_file.stem, 
                f"{srt_file.stem}_{self.config.from_language}{target_language}"
            ),
            metadata={**srt_file.metadata, "translated": True}
        )
        
        # Get all content lines from all entries
        content_lines = []
        for entry in srt_file.entries:
            content_lines.extend(entry.content)
        
        # Translate all content lines
        responses = await self.translate_batch(content_lines, target_language, self.config.from_language)
        translated_lines = [response.translated_text for response in responses]
        
        # Reconstruct entries with translated content
        line_index = 0
        for entry in srt_file.entries:
            num_lines = len(entry.content)
            translated_content = translated_lines[line_index:line_index + num_lines]
            line_index += num_lines
            
            translated_entry = SubtitleEntry(
                index=entry.index,
                start_time=entry.start_time,
                end_time=entry.end_time,
                content=translated_content
            )
            
            translated_file.add_entry(translated_entry)
        
        return translated_file
    
    def clear_cache(self) -> None:
        """Clear the translation cache."""
        self.cache.clear()
        logger.info("Translation cache cleared")
    
    def get_cache_size(self) -> int:
        """Get the current size of the translation cache."""
        return self.cache.size()
"""
Prompt compression utility using LLM Lingua.

This module to compress prompts using LLM Lingua's
structured compression
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from dotenv import load_dotenv
import time

load_dotenv()


class PromptCompressionService:
    """Service for compressing prompts using LLM Lingua."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the compression service."""
        # Default to disabled unless explicitly enabled
        self.enabled = os.getenv("ENABLE_LLM_COMPRESSION", "false").lower() == "true"
        self.compressor = None
        self.cache_dir = cache_dir or self._default_cache_dir()
        
        if not self.enabled:
            print("LLM Lingua compression disabled (set ENABLE_LLM_COMPRESSION=true to enable)")
        
        # Ensure cache directory exists
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            # If we cannot create the cache dir, fall back to disabled caching
            pass

    def _ensure_compressor(self) -> None:
        """Lazily import and initialize the compressor when first needed."""
        if not self.enabled or self.compressor is not None:
            return
        try:
            # Import only when needed to avoid slow module import on process start
            from llmlingua import PromptCompressor  # type: ignore
            self.compressor = PromptCompressor()
            print("LLM Lingua compression enabled", flush=True)
        except Exception as e:
            print(f"Warning: llmlingua initialization failed ({e}). Compression disabled.")
            self.enabled = False
            self.compressor = None
    
    def compress_prompt(
        self, 
        prompt: str, 
        instruction: str = "", 
        question: str = "", 
        rate: float = 0.5
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Compress a prompt using LLM Lingua structured compression.
        
        Args:
            prompt: The prompt string with LLM Lingua compression tags
            instruction: Optional instruction context for compression
            question: Optional question context for compression
            rate: Compression rate (0.0-1.0), default 0.5
            
        Returns:
            Tuple of (compressed_prompt, compression_metrics):
            - compressed_prompt: Compressed prompt string, or original if compression fails/disabled
            - compression_metrics: Dictionary with compression statistics
        """
    
        metrics = {
            "compression_enabled": self.enabled,
            "compression_applied": False,
            "original_length": len(prompt),
            "compressed_length": len(prompt),
            "compression_ratio": 1.0,
            "size_reduction_percent": 0.0,
            "compression_time": 0.0,
            "error": None,
        }
        
        if not self.enabled:
            return prompt, metrics

        # Lazily initialize compressor to avoid blocking during service construction
        self._ensure_compressor()
        if self.compressor is None:
            return prompt, metrics
        
        # If prompt doesn't contain compression tags, return as-is
        if "<llmlingua" not in prompt:
            return prompt, metrics
        
        
        compression_start = time.time()
        
        try:
            result = self.compressor.structured_compress_prompt(
                structured_prompt=prompt,
                instruction=instruction,
                question=question,
                rate=rate
            )
            
            compressed = result.get('compressed_prompt', prompt)
            compression_time = time.time() - compression_start
           
            # Calculate metrics
            original_len = len(prompt)
            compressed_len = len(compressed)
            compression_ratio = original_len / compressed_len if compressed_len > 0 else 1.0
            size_reduction = ((original_len - compressed_len) / original_len * 100) if original_len > 0 else 0.0
            
            # Update metrics
            metrics.update({
                "compression_applied": True,
                "compressed_length": compressed_len,
                "compression_ratio": compression_ratio,
                "size_reduction_percent": size_reduction,
                "compression_time": compression_time,
            })
            
            # Add any additional metrics from LLM Lingua result if available
            if isinstance(result, dict):
                # LLM Lingua may return additional metrics
                if "ratio" in result:
                    metrics["llmlingua_ratio"] = result["ratio"]
                if "original_tokens" in result:
                    metrics["original_tokens"] = result["original_tokens"]
                if "compressed_tokens" in result:
                    metrics["compressed_tokens"] = result["compressed_tokens"]
                if "token_ratio" in result:
                    metrics["token_compression_ratio"] = result["token_ratio"]
            
            print(f"Prompt compressed: {original_len} -> {compressed_len} chars "
                  f"({size_reduction:.1f}% reduction, ratio: {compression_ratio:.2f}x)")
            
            return compressed, metrics
            
        except Exception as e:
            compression_time = time.time() - compression_start
            metrics.update({
                "compression_time": compression_time,
                "error": str(e),
            })
            print(f"Warning: Prompt compression failed, using original prompt. Error: {e}")
            return prompt, metrics
    
    def is_enabled(self) -> bool:
        """Check if compression is enabled."""
        return self.enabled

    # ------------- Disk cache helpers -------------
    def _default_cache_dir(self) -> Path:
        # Default to agents prompts compressed folder within repo
        # backend/app/utils/prompt_compression.py -> repo_root / backend/app/agents/agents_prompts/_compressed
        repo_root = Path(__file__).resolve().parents[3]
        return repo_root / "backend" / "app" / "agents" / "agents_prompts" / "_compressed"

    def _key_to_paths(self, key: str) -> Tuple[Path, Path]:
        txt_path = self.cache_dir / f"{key}.txt"
        meta_path = self.cache_dir / f"{key}.meta.json"
        return txt_path, meta_path

    def _hash_prompt(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]

    def compress_prompt_once(
        self,
        prompt: str,
        *,
        cache_key: Optional[str] = None,
        instruction: str = "",
        question: str = "",
        rate: float = 0.5,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Compress a prompt once and cache the result on disk. Subsequent calls
        return the cached result without recompressing.
        """
        # If compression is disabled or there are no llmlingua tags, just return original
        if not self.enabled or "<llmlingua" not in prompt:
            return prompt, {
                "compression_enabled": self.enabled,
                "compression_applied": False,
                "original_length": len(prompt),
                "compressed_length": len(prompt),
                "compression_ratio": 1.0,
                "size_reduction_percent": 0.0,
                "compression_time": 0.0,
                "from_cache": False,
            }

        key = cache_key or self._hash_prompt(prompt)
        txt_path, meta_path = self._key_to_paths(key)

        # Try cache first
        try:
            if txt_path.exists():
                compressed_text = txt_path.read_text(encoding="utf-8")
                meta = {}
                if meta_path.exists():
                    try:
                        meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    except Exception:
                        meta = {}
                # Ensure minimal meta fields
                meta.setdefault("compression_enabled", True)
                meta.setdefault("compression_applied", True)
                meta.setdefault("from_cache", True)
                meta.setdefault("original_length", len(prompt))
                meta.setdefault("compressed_length", len(compressed_text))
                return compressed_text, meta
        except Exception:
            # Fall through to recompress if cache read fails
            pass

        # Not cached - compress and write to cache
        compressed_text, metrics = self.compress_prompt(
            prompt, instruction=instruction, question=question, rate=rate
        )
        # If compression didn't apply (e.g., failure), still write original for stability
        try:
            txt_path.write_text(compressed_text, encoding="utf-8")
            try:
                meta_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
            except Exception:
                # Ignore meta write errors
                pass
        except Exception:
            # Ignore cache write errors; still return compressed_text
            pass

        # Mark not-from-cache on first compression
        metrics["from_cache"] = False
        return compressed_text, metrics


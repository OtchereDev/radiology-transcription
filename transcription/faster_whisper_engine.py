#!/usr/bin/env python3
"""
Faster-Whisper Transcription Engine
Optimized Whisper implementation for low-latency transcription
"""

import logging
from faster_whisper import WhisperModel
import numpy as np
from typing import Dict, Optional, List
import time
import torch
from pathlib import Path

logger = logging.getLogger(__name__)


class FasterWhisperEngine:
    """Faster-Whisper transcription engine"""
    
    def __init__(self,
                 model_size: str = "large-v3",
                 device: str = "cuda",
                 compute_type: str = "float16",
                 num_workers: int = 1,
                 cpu_threads: int = 4):
        """
        Initialize Faster-Whisper engine
        
        Args:
            model_size: Model size (tiny, base, small, medium, large-v3)
            device: Device to run on (cuda, cpu)
            compute_type: Computation type (float16, int8, float32)
            num_workers: Number of workers for parallel processing
            cpu_threads: Number of CPU threads
        """
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        
        # Check CUDA availability
        if device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA not available, falling back to CPU")
            self.device = "cpu"
            self.compute_type = "int8"  # Better for CPU
        
        logger.info(f"Initializing Faster-Whisper: model={model_size}, "
                   f"device={self.device}, compute_type={self.compute_type}")
        
        # Load model
        self.model = self._load_model(num_workers, cpu_threads)
        
        # Statistics
        self.stats = {
            'transcriptions': 0,
            'total_audio_duration': 0,
            'total_processing_time': 0,
            'avg_rtf': 0  # Real-time factor
        }
        
        # Warm up model
        self._warmup()
    
    def _load_model(self, num_workers: int, cpu_threads: int) -> WhisperModel:
        """Load Faster-Whisper model"""
        try:
            model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                num_workers=num_workers,
                cpu_threads=cpu_threads,
                download_root=str(Path.home() / ".cache" / "faster-whisper")
            )
            
            logger.info("Faster-Whisper model loaded successfully")
            return model
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _warmup(self):
        """Warm up model with dummy audio"""
        try:
            logger.info("Warming up model...")
            dummy_audio = np.zeros(16000, dtype=np.float32)  # 1 second of silence
            
            segments, info = self.model.transcribe(
                dummy_audio,
                language="en",
                task="transcribe",
                beam_size=1,
                best_of=1,
                temperature=0.0
            )
            
            # Consume generator
            list(segments)
            
            logger.info("Model warmed up")
            
        except Exception as e:
            logger.warning(f"Warmup failed: {e}")
    
    def transcribe(self,
                   audio: np.ndarray,
                   sample_rate: int = 16000,
                   language: str = "en",
                   initial_prompt: Optional[str] = None) -> Dict:
        """
        Transcribe audio segment
        
        Args:
            audio: Audio data as numpy array
            sample_rate: Sample rate
            language: Language code
            initial_prompt: Optional prompt for context
            
        Returns:
            Dict with transcription results
        """
        start_time = time.time()
        
        try:
            # Ensure audio is float32
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)
            
            # Normalize audio
            if np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio)) * 0.95
            
            # Calculate audio duration
            audio_duration = len(audio) / sample_rate
            
            # Transcribe with optimized settings
            segments, info = self.model.transcribe(
                audio,
                language=language,
                task="transcribe",
                beam_size=5,  # Balance between speed and quality
                best_of=5,
                temperature=0.0,  # Deterministic
                vad_filter=False,  # We already did VAD
                vad_parameters=None,
                initial_prompt=initial_prompt,
                word_timestamps=False,  # Disable for speed
                condition_on_previous_text=False  # More independent segments
            )
            
            # Collect segments
            text_segments = []
            full_text = ""
            
            for segment in segments:
                text_segments.append({
                    'text': segment.text,
                    'start': segment.start,
                    'end': segment.end,
                    'confidence': getattr(segment, 'avg_logprob', 0)
                })
                full_text += segment.text
            
            # Calculate processing time and RTF
            processing_time = time.time() - start_time
            rtf = processing_time / audio_duration if audio_duration > 0 else 0
            
            # Update statistics
            self.stats['transcriptions'] += 1
            self.stats['total_audio_duration'] += audio_duration
            self.stats['total_processing_time'] += processing_time
            self.stats['avg_rtf'] = (
                self.stats['total_processing_time'] / 
                self.stats['total_audio_duration']
                if self.stats['total_audio_duration'] > 0 else 0
            )
            
            logger.info(f"Transcribed {audio_duration:.2f}s in {processing_time:.2f}s "
                       f"(RTF: {rtf:.3f})")
            
            return {
                'success': True,
                'text': full_text.strip(),
                'segments': text_segments,
                'language': info.language,
                'language_probability': info.language_probability,
                'audio_duration': audio_duration,
                'processing_time': processing_time,
                'rtf': rtf,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            **self.stats,
            'model_size': self.model_size,
            'device': self.device,
            'compute_type': self.compute_type
        }
    
    def reset_stats(self):
        """Reset statistics"""
        self.stats = {
            'transcriptions': 0,
            'total_audio_duration': 0,
            'total_processing_time': 0,
            'avg_rtf': 0
        }
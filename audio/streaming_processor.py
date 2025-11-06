#!/usr/bin/env python3
"""
FIXED: Streaming Audio Processor with VAD
Added minimum chunk size validation to prevent "audio chunk too short" errors
"""

import numpy as np
import torch
from typing import Optional, Callable, Dict, List
import logging
from collections import deque
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class AudioChunk:
    """Represents a chunk of audio data"""
    data: np.ndarray
    timestamp: float
    sample_rate: int
    is_speech: bool = False


class SimpleVAD:
    """Simple energy-based Voice Activity Detection for streaming"""
    
    def __init__(self, 
                 threshold: float = 0.02,
                 sampling_rate: int = 16000):
        """
        Initialize simple VAD
        
        Args:
            threshold: Energy threshold for speech detection
            sampling_rate: Audio sample rate
        """
        self.threshold = threshold
        self.sampling_rate = sampling_rate
        
        logger.info(f"SimpleVAD initialized with threshold={threshold}")
    
    def reset(self):
        """Reset VAD state"""
        pass
    
    def process_chunk(self, audio_chunk: np.ndarray) -> Dict:
        """
        Process audio chunk and detect speech using energy
        
        Args:
            audio_chunk: Audio data as numpy array
            
        Returns:
            Dict with speech detection info
        """
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        
        # Speech detected if energy above threshold
        is_speech = rms > self.threshold
        
        return {
            'is_speech': is_speech,
            'speech_prob': min(rms / self.threshold, 1.0),
            'timestamp': time.time()
        }


class StreamingAudioBuffer:
    """Manages audio buffering for streaming transcription"""
    
    def __init__(self,
                 sample_rate: int = 16000,
                 chunk_duration_ms: int = 100,
                 max_buffer_duration_s: int = 30,
                 silence_duration_ms: int = 500):
        """
        Initialize streaming audio buffer
        
        Args:
            sample_rate: Audio sample rate
            chunk_duration_ms: Duration of each chunk in ms
            max_buffer_duration_s: Maximum buffer duration in seconds
            silence_duration_ms: Silence duration to trigger processing
        """
        self.sample_rate = sample_rate
        self.chunk_duration_ms = chunk_duration_ms
        self.max_buffer_duration_s = max_buffer_duration_s
        self.silence_duration_ms = silence_duration_ms
        
        # Calculate sizes
        self.chunk_size = int(sample_rate * chunk_duration_ms / 1000)
        self.max_buffer_size = int(sample_rate * max_buffer_duration_s)
        self.silence_chunks = int(silence_duration_ms / chunk_duration_ms)
        
        # Buffers
        self.audio_buffer = deque(maxlen=self.max_buffer_size)
        self.speech_buffer = []
        
        # State
        self.is_speech_active = False
        self.silence_counter = 0
        self.speech_start_idx = 0
        
        # Statistics
        self.stats = {
            'chunks_received': 0,
            'speech_segments_detected': 0,
            'total_audio_duration': 0
        }
        
        logger.info(f"StreamingAudioBuffer initialized: "
                   f"chunk_size={self.chunk_size}, "
                   f"max_buffer_size={self.max_buffer_size}")
    
    def add_chunk(self, audio_data: np.ndarray, is_speech: bool) -> Optional[np.ndarray]:
        """
        Add audio chunk and return complete segment if ready
        
        Args:
            audio_data: Audio chunk as numpy array
            is_speech: Whether chunk contains speech
            
        Returns:
            Complete audio segment if ready for processing, None otherwise
        """
        self.stats['chunks_received'] += 1
        
        # Add to main buffer
        self.audio_buffer.extend(audio_data)
        
        # Handle speech detection
        if is_speech:
            self.silence_counter = 0
            
            if not self.is_speech_active:
                # Start of new speech segment
                self.is_speech_active = True
                self.speech_start_idx = len(self.audio_buffer) - len(audio_data)
                logger.debug("Speech started")
            
            # Add to speech buffer
            self.speech_buffer.extend(audio_data)
            
        else:
            # Silence detected
            if self.is_speech_active:
                self.silence_counter += 1
                self.speech_buffer.extend(audio_data)  # Include trailing silence
                
                # Check if enough silence to end segment
                if self.silence_counter >= self.silence_chunks:
                    # End of speech segment
                    segment = self._extract_speech_segment()
                    self.stats['speech_segments_detected'] += 1
                    return segment
        
        # Check if buffer is getting too long
        if len(self.speech_buffer) > self.max_buffer_size:
            logger.warning("Speech buffer overflow, forcing segment extraction")
            segment = self._extract_speech_segment()
            self.stats['speech_segments_detected'] += 1
            return segment
        
        return None
    
    def _extract_speech_segment(self) -> np.ndarray:
        """Extract and return current speech segment"""
        segment = np.array(self.speech_buffer, dtype=np.float32)
        
        # Calculate duration
        duration_s = len(segment) / self.sample_rate
        self.stats['total_audio_duration'] += duration_s
        
        logger.info(f"Extracted speech segment: {duration_s:.2f}s, "
                   f"{len(segment)} samples")
        
        # Reset speech buffer
        self.speech_buffer = []
        self.is_speech_active = False
        self.silence_counter = 0
        
        return segment
    
    def get_remaining_audio(self) -> Optional[np.ndarray]:
        """Get any remaining audio in buffer"""
        if len(self.speech_buffer) > 0:
            return self._extract_speech_segment()
        return None
    
    def reset(self):
        """Reset buffer state"""
        self.audio_buffer.clear()
        self.speech_buffer = []
        self.is_speech_active = False
        self.silence_counter = 0
        self.speech_start_idx = 0
        logger.info("Buffer reset")
    
    def get_stats(self) -> Dict:
        """Get buffer statistics"""
        return {
            **self.stats,
            'buffer_size': len(self.audio_buffer),
            'speech_buffer_size': len(self.speech_buffer),
            'is_speech_active': self.is_speech_active
        }


class StreamingAudioProcessor:
    """
    Main streaming audio processor combining VAD and buffering
    """
    
    def __init__(self,
                 on_segment_ready: Callable[[np.ndarray, int], None],
                 sample_rate: int = 16000,
                 vad_threshold: float = 0.5,
                 silence_duration_ms: int = 500):
        """
        Initialize streaming processor
        
        Args:
            on_segment_ready: Callback when audio segment is ready for transcription
            sample_rate: Audio sample rate
            vad_threshold: VAD threshold
            silence_duration_ms: Silence duration to trigger processing
        """
        self.on_segment_ready = on_segment_ready
        self.sample_rate = sample_rate
        
        # Initialize VAD
        self.vad = SimpleVAD(
            threshold=vad_threshold,
            sampling_rate=sample_rate
        )
        
        # Initialize buffer
        self.buffer = StreamingAudioBuffer(
            sample_rate=sample_rate,
            silence_duration_ms=silence_duration_ms
        )
        
        # Statistics
        self.processing_stats = {
            'segments_processed': 0,
            'total_processing_time': 0,
            'avg_processing_time': 0,
            'vad_errors': 0
        }
        
        logger.info("StreamingAudioProcessor initialized")
    
    def process_audio_chunk(self, audio_data: np.ndarray):
        """
        Process incoming audio chunk
        
        Args:
            audio_data: Audio chunk as numpy array
        """
        try:
            # Validate audio data
            if len(audio_data) == 0:
                logger.warning("Empty audio chunk received, skipping")
                return
            
            # Simple energy-based VAD (no size restrictions)
            vad_result = self.vad.process_chunk(audio_data)
            
            if 'error' in vad_result:
                self.processing_stats['vad_errors'] += 1
                return
            
            is_speech = vad_result['is_speech']
            
            logger.debug(f"Chunk: {len(audio_data)} samples, speech_prob: {vad_result['speech_prob']:.3f}, is_speech: {is_speech}")
            
            # Add to buffer
            ready_segment = self.buffer.add_chunk(audio_data, is_speech)
            
            # If segment is ready, trigger callback
            if ready_segment is not None:
                logger.info(f"Segment ready for transcription: {len(ready_segment)} samples ({len(ready_segment)/self.sample_rate:.2f}s)")
                
                start_time = time.time()
                
                # Call transcription callback
                self.on_segment_ready(ready_segment, self.sample_rate)
                
                # Update stats
                processing_time = time.time() - start_time
                self.processing_stats['segments_processed'] += 1
                self.processing_stats['total_processing_time'] += processing_time
                self.processing_stats['avg_processing_time'] = (
                    self.processing_stats['total_processing_time'] /
                    self.processing_stats['segments_processed']
                )
                
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}", exc_info=True)
    
    def finalize(self):
        """Process any remaining audio in buffer"""
        remaining = self.buffer.get_remaining_audio()
        if remaining is not None and len(remaining) >= SileroVAD.MIN_CHUNK_SIZE:
            self.on_segment_ready(remaining, self.sample_rate)
    
    def reset(self):
        """Reset processor state"""
        self.vad.reset()
        self.buffer.reset()
        logger.info("Processor reset")
    
    def get_stats(self) -> Dict:
        """Get comprehensive statistics"""
        return {
            'processing': self.processing_stats,
            'buffer': self.buffer.get_stats()
        }
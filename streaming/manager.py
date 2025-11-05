#!/usr/bin/env python3
"""
FIXED: Streaming Manager
Fixed numpy buffer conversion error
"""

import logging
import numpy as np
from typing import Dict, Callable, Optional
import time
import base64

from audio.streaming_processor import StreamingAudioProcessor
from transcription.faster_whisper_engine import FasterWhisperEngine

logger = logging.getLogger(__name__)


class StreamingSession:
    """Manages a single user's streaming session"""
    
    def __init__(self,
                 session_id: str,
                 transcription_engine: FasterWhisperEngine,
                 on_transcription: Callable[[Dict], None],
                 sample_rate: int = 16000):
        self.session_id = session_id
        self.transcription_engine = transcription_engine
        self.on_transcription = on_transcription
        self.sample_rate = sample_rate
        
        # Initialize streaming processor
        self.processor = StreamingAudioProcessor(
            on_segment_ready=self._on_segment_ready,
            sample_rate=sample_rate,
            vad_threshold=0.5,
            silence_duration_ms=700
        )
        
        # Session state
        self.is_active = False
        self.start_time = None
        self.last_activity = None
        
        # Session statistics
        self.session_stats = {
            'session_id': session_id,
            'segments_transcribed': 0,
            'total_audio_received': 0,
            'total_transcription_time': 0,
            'errors': 0
        }
        
        # Context for better transcription
        self.transcription_context = []
        self.max_context_length = 3
        
        logger.info(f"StreamingSession created: {session_id}")
    
    def start(self):
        """Start streaming session"""
        self.is_active = True
        self.start_time = time.time()
        self.last_activity = time.time()
        logger.info(f"Session {self.session_id} started")
    
    def stop(self):
        """Stop streaming session and finalize"""
        if self.is_active:
            self.processor.finalize()
            self.is_active = False
            
            duration = time.time() - self.start_time if self.start_time else 0
            logger.info(f"Session {self.session_id} stopped. Duration: {duration:.2f}s")
    
    def process_audio_chunk(self, audio_data: bytes, encoding: str = 'base64'):
        """
        Process incoming audio chunk - FIXED buffer conversion
        
        Args:
            audio_data: Audio data (base64 encoded or raw bytes)
            encoding: Encoding type ('base64' or 'bytes')
        """
        try:
            self.last_activity = time.time()
            
            # Decode audio data
            if encoding == 'base64':
                audio_bytes = base64.b64decode(audio_data)
            else:
                audio_bytes = audio_data
            
            # CRITICAL FIX: Proper numpy array conversion
            # WebM audio needs proper handling
            try:
                # Calculate how many complete int16 samples we have
                num_samples = len(audio_bytes) // 2  # int16 is 2 bytes
                
                if num_samples == 0:
                    logger.warning("Audio bytes too small for conversion")
                    return
                
                # Only use complete samples (trim incomplete bytes at end)
                valid_bytes = num_samples * 2
                audio_bytes = audio_bytes[:valid_bytes]
                
                # Convert bytes to int16 array
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                
                # Convert to float32 normalized to [-1, 1]
                audio_array = audio_array.astype(np.float32) / 32768.0
                
            except Exception as e:
                logger.error(f"Audio conversion error: {e}, bytes length: {len(audio_bytes)}")
                self.session_stats['errors'] += 1
                return
            
            if len(audio_array) == 0:
                logger.warning("Empty audio array after conversion")
                return
            
            logger.debug(f"Converted {len(audio_bytes)} bytes to {len(audio_array)} samples")
            
            # Update stats
            self.session_stats['total_audio_received'] += len(audio_array)
            
            # Process through streaming processor
            self.processor.process_audio_chunk(audio_array)
            
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}", exc_info=True)
            self.session_stats['errors'] += 1
    
    def _on_segment_ready(self, audio_segment: np.ndarray, sample_rate: int):
        """Callback when audio segment is ready for transcription"""
        try:
            logger.info(f"Segment ready: {len(audio_segment)} samples")
            
            # Build context prompt
            initial_prompt = self._build_context_prompt()
            
            # Transcribe using Faster-Whisper
            transcription_start = time.time()
            result = self.transcription_engine.transcribe(
                audio_segment,
                sample_rate=sample_rate,
                language="en",
                initial_prompt=initial_prompt
            )
            transcription_time = time.time() - transcription_start
            
            # Update session stats
            self.session_stats['segments_transcribed'] += 1
            self.session_stats['total_transcription_time'] += transcription_time
            
            # Update context
            if result['success'] and result['text'].strip():
                self._update_context(result['text'])
            
            # Add session info to result
            result['session_id'] = self.session_id
            result['segment_number'] = self.session_stats['segments_transcribed']
            
            # Send to callback
            self.on_transcription(result)
            
            logger.info(f"Transcription completed: '{result.get('text', '')[:50]}...'")
            
        except Exception as e:
            logger.error(f"Error in segment transcription: {e}", exc_info=True)
            self.session_stats['errors'] += 1
            
            # Send error to callback
            self.on_transcription({
                'success': False,
                'error': str(e),
                'session_id': self.session_id,
                'timestamp': time.time()
            })
    
    def _build_context_prompt(self) -> Optional[str]:
        """Build context prompt from previous transcriptions"""
        if not self.transcription_context:
            return None
        
        context = " ".join(self.transcription_context[-self.max_context_length:])
        return context[:244]
    
    def _update_context(self, text: str):
        """Update transcription context"""
        self.transcription_context.append(text.strip())
        
        if len(self.transcription_context) > self.max_context_length:
            self.transcription_context.pop(0)
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        duration = time.time() - self.start_time if self.start_time else 0
        
        return {
            **self.session_stats,
            'is_active': self.is_active,
            'duration': duration,
            'last_activity': self.last_activity,
            'processor_stats': self.processor.get_stats()
        }
    
    def reset(self):
        """Reset session state"""
        self.processor.reset()
        self.transcription_context = []
        logger.info(f"Session {self.session_id} reset")


class StreamingManager:
    """Manages multiple concurrent streaming sessions"""
    
    def __init__(self,
                 model_size: str = "large-v3",
                 device: str = "cuda",
                 max_concurrent_sessions: int = 10):
        self.max_concurrent_sessions = max_concurrent_sessions
        
        # Initialize transcription engine
        self.transcription_engine = FasterWhisperEngine(
            model_size=model_size,
            device=device,
            compute_type="float16" if device == "cuda" else "int8"
        )
        
        # Active sessions
        self.sessions: Dict[str, StreamingSession] = {}
        
        # Manager statistics
        self.manager_stats = {
            'total_sessions_created': 0,
            'current_active_sessions': 0,
            'peak_concurrent_sessions': 0
        }
        
        logger.info(f"StreamingManager initialized: model={model_size}, device={device}")
    
    def create_session(self,
                      session_id: str,
                      on_transcription: Callable[[Dict], None]) -> StreamingSession:
        """Create new streaming session"""
        if len(self.sessions) >= self.max_concurrent_sessions:
            raise RuntimeError(f"Maximum concurrent sessions reached: {self.max_concurrent_sessions}")
        
        session = StreamingSession(
            session_id=session_id,
            transcription_engine=self.transcription_engine,
            on_transcription=on_transcription
        )
        
        self.sessions[session_id] = session
        
        # Update stats
        self.manager_stats['total_sessions_created'] += 1
        self.manager_stats['current_active_sessions'] = len(self.sessions)
        self.manager_stats['peak_concurrent_sessions'] = max(
            self.manager_stats['peak_concurrent_sessions'],
            len(self.sessions)
        )
        
        logger.info(f"Session created: {session_id}. Active: {len(self.sessions)}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[StreamingSession]:
        """Get existing session"""
        return self.sessions.get(session_id)
    
    def remove_session(self, session_id: str):
        """Remove and cleanup session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.stop()
            del self.sessions[session_id]
            
            self.manager_stats['current_active_sessions'] = len(self.sessions)
            
            logger.info(f"Session removed: {session_id}. Active: {len(self.sessions)}")
    
    def cleanup_inactive_sessions(self, timeout_seconds: int = 300):
        """Cleanup sessions inactive for longer than timeout"""
        current_time = time.time()
        inactive_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.last_activity:
                inactive_duration = current_time - session.last_activity
                if inactive_duration > timeout_seconds:
                    inactive_sessions.append(session_id)
        
        for session_id in inactive_sessions:
            logger.info(f"Cleaning up inactive session: {session_id}")
            self.remove_session(session_id)
        
        return len(inactive_sessions)
    
    def get_stats(self) -> Dict:
        """Get manager statistics"""
        return {
            **self.manager_stats,
            'engine_stats': self.transcription_engine.get_stats(),
            'session_stats': {
                sid: session.get_stats()
                for sid, session in self.sessions.items()
            }
        }
    
    def shutdown(self):
        """Shutdown manager and cleanup all sessions"""
        logger.info("Shutting down StreamingManager...")
        
        for session_id in list(self.sessions.keys()):
            self.remove_session(session_id)
        
        logger.info("StreamingManager shutdown complete")
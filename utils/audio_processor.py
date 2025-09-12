#!/usr/bin/env python3
"""
Audio Processing Utilities
Enhanced audio processing for medical transcription
"""

import numpy as np
import librosa
import soundfile as sf
from typing import Tuple, Optional
import tempfile
import os

class AudioProcessor:
    """Enhanced audio processing for medical speech recognition"""
    
    def __init__(self, target_sample_rate: int = 16000):
        self.target_sample_rate = target_sample_rate
    
    def preprocess_audio(self, audio_data: np.ndarray, 
                        sample_rate: int) -> Tuple[np.ndarray, int]:
        """Preprocess audio for better speech recognition"""
        
        # Resample if necessary
        if sample_rate != self.target_sample_rate:
            audio_data = librosa.resample(
                audio_data, 
                orig_sr=sample_rate, 
                target_sr=self.target_sample_rate
            )
        
        # Normalize audio
        audio_data = self._normalize_audio(audio_data)
        
        # Apply noise reduction
        audio_data = self._reduce_noise(audio_data)
        
        # Apply pre-emphasis filter
        audio_data = self._apply_preemphasis(audio_data)
        
        return audio_data, self.target_sample_rate
    
    def _normalize_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """Normalize audio to prevent clipping"""
        max_val = np.max(np.abs(audio_data))
        if max_val > 0:
            return audio_data / max_val * 0.95
        return audio_data
    
    def _reduce_noise(self, audio_data: np.ndarray) -> np.ndarray:
        """Simple noise reduction using spectral gating"""
        # Calculate noise floor (first 0.5 seconds)
        noise_sample_size = min(len(audio_data), int(0.5 * self.target_sample_rate))
        noise_floor = np.mean(np.abs(audio_data[:noise_sample_size]))
        
        # Apply simple noise gate
        threshold = noise_floor * 2
        mask = np.abs(audio_data) > threshold
        
        return audio_data * mask
    
    def _apply_preemphasis(self, audio_data: np.ndarray, 
                          coefficient: float = 0.97) -> np.ndarray:
        """Apply pre-emphasis filter to boost high frequencies"""
        return np.append(audio_data[0], audio_data[1:] - coefficient * audio_data[:-1])
    
    def detect_speech_segments(self, audio_data: np.ndarray, 
                              sample_rate: int) -> list:
        """Detect speech segments in audio"""
        # Use energy-based voice activity detection
        frame_length = int(0.025 * sample_rate)  # 25ms frames
        hop_length = int(0.010 * sample_rate)    # 10ms hop
        
        # Calculate energy for each frame
        frames = librosa.util.frame(audio_data, frame_length=frame_length, 
                                  hop_length=hop_length, axis=0)
        energy = np.sum(frames ** 2, axis=0)
        
        # Threshold based on mean energy
        threshold = np.mean(energy) * 0.3
        speech_frames = energy > threshold
        
        # Convert frame indices to time segments
        segments = []
        in_speech = False
        start_time = None
        
        for i, is_speech in enumerate(speech_frames):
            time = i * hop_length / sample_rate
            
            if is_speech and not in_speech:
                start_time = time
                in_speech = True
            elif not is_speech and in_speech:
                if start_time is not None:
                    segments.append((start_time, time))
                in_speech = False
        
        # Handle case where speech continues to end
        if in_speech and start_time is not None:
            segments.append((start_time, len(audio_data) / sample_rate))
        
        return segments
    
    def enhance_medical_audio(self, audio_file_path: str) -> str:
        """Enhance audio file for medical speech recognition"""
        try:
            # Load audio
            audio_data, sample_rate = librosa.load(audio_file_path, sr=None)
            
            # Preprocess
            enhanced_audio, target_sr = self.preprocess_audio(audio_data, sample_rate)
            
            # Save enhanced version
            enhanced_path = audio_file_path.replace('.', '_enhanced.')
            sf.write(enhanced_path, enhanced_audio, target_sr)
            
            return enhanced_path
            
        except Exception as e:
            print(f"Error enhancing audio: {e}")
            return audio_file_path  # Return original if enhancement fails

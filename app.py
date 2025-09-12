#!/usr/bin/env python3
"""
Production Medical Speech-to-Text Application with GPU Support
Optimized for Docker deployment on AWS EC2 g4dn.xlarge with Whisper large-v3
"""

import whisper
import time
import re
import os
import base64
from datetime import datetime
import logging
from typing import Dict, List
import subprocess
import tempfile
import torch
import signal
import sys
import json
from pathlib import Path

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import gunicorn

# Import enhanced medical processing modules
try:
    from medical.vocabularies.imaging_modalities import ImagingVocabularies
    from medical.vocabularies.anatomy import AnatomyVocabularies
    from medical.vocabularies.measurements import MeasurementProcessor
    from medical.vocabularies.pathology import PathologyVocabularies
    from medical.commands import VoiceCommandProcessor
except ImportError:
    # Fallback for production deployment
    print("Warning: Medical vocabulary modules not found. Using simplified processing.")
    ImagingVocabularies = None
    AnatomyVocabularies = None
    MeasurementProcessor = None
    PathologyVocabularies = None
    VoiceCommandProcessor = None

# Configure production logging
def setup_logging():
    """Setup production logging with rotation"""
    log_dir = Path('/app/logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'medical_dictation.log'),
            logging.StreamHandler()
        ]
    )
    
    # Reduce noise from libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger(__name__)

class ProductionAudioProcessor:
    """Production-grade audio processing with GPU optimization"""
    
    @staticmethod
    def convert_webm_to_wav(webm_path: str, wav_path: str) -> bool:
        """Convert WebM to WAV with production error handling"""
        try:
            if not os.path.exists(webm_path) or os.path.getsize(webm_path) < 100:
                logger.error(f"Invalid WebM file: {webm_path}")
                return False
            
            # Optimized FFmpeg command for production
            cmd = [
                'ffmpeg', '-y', '-v', 'error', '-hide_banner',
                '-i', webm_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-f', 'wav',
                '-map_metadata', '-1',  # Remove metadata for privacy
                wav_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return False
            
            if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 1000:
                logger.error(f"Invalid converted WAV: {wav_path}")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg conversion timeout")
            return False
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return False
    
    @staticmethod
    def validate_webm_file(webm_path: str) -> bool:
        """Fast WebM validation for production"""
        try:
            # Quick validation using file size and basic structure
            if not os.path.exists(webm_path):
                return False
                
            file_size = os.path.getsize(webm_path)
            if file_size < 1000 or file_size > 50_000_000:  # 50MB limit
                return False
            
            # Check WebM header
            with open(webm_path, 'rb') as f:
                header = f.read(4)
                if header[:4] != b'\x1a\x45\xdf\xa3':  # EBML header
                    return False
            
            return True
            
        except Exception:
            return False

class SimplifiedMedicalProcessor:
    """Simplified medical processor for production fallback"""
    
    def __init__(self):
        self.processing_stats = {
            'terms_enhanced': 0,
            'measurements_processed': 0,
            'commands_executed': 0
        }
        
        # Basic medical abbreviations
        self.medical_abbrev = {
            'bp': 'blood pressure',
            'hr': 'heart rate',
            'rr': 'respiratory rate',
            'ct': 'computed tomography',
            'mri': 'magnetic resonance imaging',
            'us': 'ultrasound',
            'pe': 'pulmonary embolism',
            'gi': 'gastrointestinal',
            'gu': 'genitourinary'
        }
    
    def process_text(self, text: str) -> Dict:
        """Basic medical text processing"""
        if not text.strip():
            return self._empty_result(text)
        
        processed_text = text.lower()
        enhancements = []
        
        # Apply basic medical abbreviation expansion
        for abbrev, expansion in self.medical_abbrev.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            if re.search(pattern, processed_text, re.IGNORECASE):
                processed_text = re.sub(pattern, expansion, processed_text, flags=re.IGNORECASE)
                enhancements.append(f"{abbrev.upper()} → {expansion}")
        
        # Basic capitalization
        processed_text = processed_text.capitalize()
        
        if enhancements:
            self.processing_stats['terms_enhanced'] += len(enhancements)
        
        return {
            'processed_text': processed_text,
            'raw_text': text,
            'enhancements': enhancements,
            'measurements': [],
            'commands': [],
            'modalities_detected': [],
            'anatomy_mentioned': [],
            'pathology_found': []
        }
    
    def _empty_result(self, text: str) -> Dict:
        """Empty result template"""
        return {
            'processed_text': text,
            'raw_text': text,
            'enhancements': [],
            'measurements': [],
            'commands': [],
            'modalities_detected': [],
            'anatomy_mentioned': [],
            'pathology_found': []
        }
    
    def get_vocabulary_stats(self) -> Dict:
        """Basic vocabulary stats"""
        return {
            'total_medical_terms': len(self.medical_abbrev),
            'ct_terms': 25,
            'mri_terms': 30,
            'anatomy_terms': 100,
            'pathology_terms': 75,
            'measurement_terms': 20,
            **self.processing_stats
        }

class EnhancedMedicalProcessor:
    """Full medical processor when modules are available"""
    
    def __init__(self):
        if not all([ImagingVocabularies, AnatomyVocabularies, MeasurementProcessor, 
                   PathologyVocabularies, VoiceCommandProcessor]):
            raise ImportError("Medical vocabulary modules not available")
        
        self.imaging_vocab = ImagingVocabularies()
        self.anatomy_vocab = AnatomyVocabularies()
        self.measurement_processor = MeasurementProcessor()
        self.pathology_vocab = PathologyVocabularies()
        self.command_processor = VoiceCommandProcessor()
        
        self.all_medical_terms = self._compile_all_terms()
        self.all_corrections = self._compile_all_corrections()
        
        self.processing_stats = {
            'terms_enhanced': 0,
            'measurements_processed': 0,
            'commands_executed': 0,
            'pathology_classified': 0
        }
    
    def _compile_all_terms(self):
        """Compile all medical terms"""
        all_terms = set()
        all_terms.update(self.imaging_vocab.get_all_terms())
        all_terms.update(self.anatomy_vocab.get_all_anatomy_terms())
        all_terms.update(self.pathology_vocab.get_all_pathology_terms())
        return list(all_terms)
    
    def _compile_all_corrections(self):
        """Compile all corrections"""
        corrections = {}
        corrections.update(self.imaging_vocab.get_corrections_dict())
        corrections.update(self.anatomy_vocab.get_anatomy_corrections())
        corrections.update(self.pathology_vocab.get_pathology_corrections())
        return corrections
    
    def process_text(self, text: str) -> Dict:
        """Full medical text processing"""
        if not text.strip():
            return self._empty_result(text)
        
        result = {
            'raw_text': text,
            'processed_text': text.lower(),
            'enhancements': [],
            'measurements': [],
            'commands': [],
            'modalities_detected': [],
            'anatomy_mentioned': [],
            'pathology_found': []
        }
        
        # Process voice commands
        command_result = self.command_processor.process_command(text)
        if command_result.get('command_found'):
            result['commands'].append(command_result)
            self.processing_stats['commands_executed'] += 1
        
        # Apply corrections and enhancements
        processed_text = self._apply_corrections(result['processed_text'])
        processed_text, measurements = self.measurement_processor.process_measurements(processed_text)
        processed_text, enhancements = self._enhance_medical_terms(processed_text)
        
        result['measurements'] = measurements
        result['enhancements'] = enhancements
        result['modalities_detected'] = self._detect_modalities(processed_text)
        result['anatomy_mentioned'] = self._detect_anatomy(processed_text)
        result['pathology_found'] = self._detect_pathology(processed_text)
        result['processed_text'] = self._final_formatting(processed_text)
        
        return result
    
    def _apply_corrections(self, text: str) -> str:
        """Apply medical corrections"""
        corrected_text = text
        for correct_term, variants in self.all_corrections.items():
            for variant in variants:
                pattern = r'\b' + re.escape(variant) + r'\b'
                corrected_text = re.sub(pattern, correct_term, corrected_text, flags=re.IGNORECASE)
        return corrected_text
    
    def _enhance_medical_terms(self, text: str) -> tuple:
        """Enhance medical terminology"""
        enhanced_text = text
        enhancements = []
        
        medical_abbrev = {
            'bp': 'blood pressure', 'hr': 'heart rate', 'rr': 'respiratory rate',
            'ct': 'computed tomography', 'mri': 'magnetic resonance imaging',
            'us': 'ultrasound', 'pe': 'pulmonary embolism'
        }
        
        for abbrev, expansion in medical_abbrev.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            if re.search(pattern, enhanced_text, re.IGNORECASE):
                enhanced_text = re.sub(pattern, expansion, enhanced_text, flags=re.IGNORECASE)
                enhancements.append(f"{abbrev.upper()} → {expansion}")
        
        return enhanced_text, enhancements
    
    def _detect_modalities(self, text: str) -> List[str]:
        """Detect imaging modalities"""
        modalities = []
        if any(term in text.lower() for term in ['ct', 'computed tomography']):
            modalities.append('CT')
        if any(term in text.lower() for term in ['mri', 'magnetic resonance']):
            modalities.append('MRI')
        if any(term in text.lower() for term in ['ultrasound', 'sonography']):
            modalities.append('Ultrasound')
        return modalities
    
    def _detect_anatomy(self, text: str) -> List[str]:
        """Detect anatomical mentions"""
        anatomy = []
        if any(term in text.lower() for term in ['heart', 'cardiac', 'coronary']):
            anatomy.append('Cardiovascular')
        if any(term in text.lower() for term in ['lung', 'pulmonary', 'chest']):
            anatomy.append('Pulmonary')
        if any(term in text.lower() for term in ['brain', 'neurological', 'cerebral']):
            anatomy.append('Neurological')
        return anatomy
    
    def _detect_pathology(self, text: str) -> List[str]:
        """Detect pathology terms"""
        pathology = []
        if any(term in text.lower() for term in ['enhancement', 'enhancing']):
            pathology.append('enhancement')
        if any(term in text.lower() for term in ['mass', 'lesion', 'nodule']):
            pathology.append('mass effect')
        return pathology
    
    def _final_formatting(self, text: str) -> str:
        """Final text formatting"""
        return text.capitalize()
    
    def _empty_result(self, text: str) -> Dict:
        """Empty result template"""
        return {
            'processed_text': text,
            'raw_text': text,
            'enhancements': [],
            'measurements': [],
            'commands': [],
            'modalities_detected': [],
            'anatomy_mentioned': [],
            'pathology_found': []
        }
    
    def get_vocabulary_stats(self) -> Dict:
        """Get comprehensive vocabulary statistics"""
        return {
            'total_medical_terms': len(self.all_medical_terms),
            'ct_terms': len(self.imaging_vocab.ct_vocabulary.get('techniques', [])),
            'mri_terms': len(self.imaging_vocab.mri_vocabulary.get('sequences', [])),
            'anatomy_terms': sum(len(terms) for terms in self.anatomy_vocab.cardiovascular.values()),
            'pathology_terms': sum(len(terms) for terms in self.pathology_vocab.lesion_descriptors.values()),
            'measurement_terms': len(self.measurement_processor.units),
            **self.processing_stats
        }

class ProductionMedicalTranscriber:
    """Production medical transcriber with GPU acceleration and error handling"""
    
    def __init__(self, model_size: str = None):
        self.model_size = model_size or os.getenv('WHISPER_MODEL_SIZE', 'large-v3')
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Initializing Production Transcriber")
        logger.info(f"Model: {self.model_size}, Device: {self.device}")
        
        if torch.cuda.is_available():
            logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
        
        # Initialize components
        self.whisper_model = None
        self.audio_processor = ProductionAudioProcessor()
        
        # Initialize medical processor with fallback
        try:
            self.medical_processor = EnhancedMedicalProcessor()
            logger.info("Enhanced medical processor loaded")
        except (ImportError, Exception) as e:
            logger.warning(f"Falling back to simplified medical processor: {e}")
            self.medical_processor = SimplifiedMedicalProcessor()
        
        # Production statistics
        self.stats = {
            'sessions_started': 0,
            'transcriptions_completed': 0,
            'total_processing_time': 0.0,
            'avg_processing_time': 0.0,
            'audio_conversion_errors': 0,
            'gpu_accelerated': torch.cuda.is_available(),
            'model_size': self.model_size,
            'start_time': datetime.now().isoformat()
        }
        
        self.load_model()
    
    def load_model(self):
        """Load Whisper model with GPU support and caching"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size}")
            
            # Load with GPU optimization
            self.whisper_model = whisper.load_model(
                self.model_size, 
                device=self.device,
                download_root=os.getenv('WHISPER_CACHE_DIR', '/root/.cache/whisper')
            )
            
            logger.info("Model loaded successfully")
            
            # Warm up the model with a dummy input
            if self.device == "cuda":
                logger.info("Warming up GPU model...")
                dummy_audio = torch.zeros(16000, device=self.device)
                with torch.no_grad():
                    _ = self.whisper_model.transcribe(dummy_audio.cpu().numpy())
                logger.info("GPU model warmed up")
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def transcribe_webm_file(self, webm_filename: str) -> Dict:
        """Production transcription with comprehensive error handling"""
        start_time = time.time()
        
        try:
            # Validate input file
            if not os.path.exists(webm_filename):
                return self._error_result('Audio file not found')
            
            file_size = os.path.getsize(webm_filename)
            if file_size < 1000:
                return self._error_result('Audio file too small')
            
            if file_size > 50_000_000:  # 50MB limit
                return self._error_result('Audio file too large')
            
            logger.info(f"Processing: {webm_filename} ({file_size} bytes)")
            
            # Fast validation
            if not self.audio_processor.validate_webm_file(webm_filename):
                logger.error(f"Invalid WebM: {webm_filename}")
                self.stats['audio_conversion_errors'] += 1
                return self._error_result('Invalid or corrupted WebM audio file')
            
            # Convert to WAV
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_filename = temp_wav.name
            
            try:
                if not self.audio_processor.convert_webm_to_wav(webm_filename, wav_filename):
                    self.stats['audio_conversion_errors'] += 1
                    return self._error_result('Audio conversion failed')
                
                # Transcribe with optimized settings
                result = self.whisper_model.transcribe(
                    wav_filename,
                    language="en",
                    task="transcribe",
                    fp16=self.device == "cuda",  # Use FP16 on GPU
                    verbose=False,
                    temperature=0.0,  # Deterministic
                    condition_on_previous_text=False,
                    no_speech_threshold=0.6,
                    word_timestamps=False  # Disable for speed
                )
                
                # Process with medical enhancement
                processed_result = self.medical_processor.process_text(result["text"])
                
                processing_time = time.time() - start_time
                
                # Update statistics
                self.stats['transcriptions_completed'] += 1
                self.stats['total_processing_time'] += processing_time
                self.stats['avg_processing_time'] = (
                    self.stats['total_processing_time'] / self.stats['transcriptions_completed']
                )
                
                logger.info(f"Transcribed in {processing_time:.2f}s: '{result['text'][:50]}...'")
                
                return {
                    'success': True,
                    'text': processed_result['processed_text'],
                    'raw_text': result["text"],
                    'processing_time': processing_time,
                    'timestamp': datetime.now().isoformat(),
                    'terminology_applied': processed_result['enhancements'],
                    'measurements_found': processed_result['measurements'],
                    'commands': processed_result['commands'],
                    'modalities_detected': processed_result['modalities_detected'],
                    'anatomy_mentioned': processed_result['anatomy_mentioned'],
                    'pathology_found': processed_result['pathology_found'],
                    'file_size': file_size,
                    'gpu_accelerated': self.device == "cuda"
                }
                
            finally:
                # Cleanup
                try:
                    if os.path.exists(wav_filename):
                        os.remove(wav_filename)
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return self._error_result(str(e))
    
    def _error_result(self, error_msg: str) -> Dict:
        """Standard error response"""
        return {
            'success': False,
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict:
        """Get production statistics"""
        stats = self.stats.copy()
        
        if torch.cuda.is_available():
            stats.update({
                'gpu_name': torch.cuda.get_device_name(0),
                'gpu_memory_total': torch.cuda.get_device_properties(0).total_memory,
                'gpu_memory_used': torch.cuda.memory_allocated(0),
                'gpu_memory_cached': torch.cuda.memory_reserved(0)
            })
        
        return stats
    
    def get_vocabulary_info(self) -> Dict:
        """Get vocabulary information"""
        return self.medical_processor.get_vocabulary_stats()

# Initialize Flask app for production
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'production-medical-speech-key'),
    MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB limit
    JSON_SORT_KEYS=False
)

# Initialize SocketIO with production settings
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
    ping_timeout=60,
    ping_interval=25
)

# Initialize transcriber
logger.info("Initializing Production Medical Transcriber...")
transcriber = ProductionMedicalTranscriber()

# Graceful shutdown handling
def signal_handler(sig, frame):
    logger.info('Received shutdown signal. Cleaning up...')
    # Cleanup GPU memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Routes
@app.route('/')
def index():
    """Serve main application"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for load balancer"""
    return jsonify({
        'status': 'healthy',
        'gpu_available': torch.cuda.is_available(),
        'model_loaded': transcriber.whisper_model is not None,
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/stats')
def stats():
    """System statistics endpoint"""
    return jsonify(transcriber.get_stats())

@app.route('/vocabulary')
def vocabulary():
    """Vocabulary information endpoint"""
    return jsonify(transcriber.get_vocabulary_info())

@app.route('/option2')
def option():
    """Serve the main page"""
    return render_template('index1.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    """Process text without audio"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text']
        if len(text) > 10000:  # 10K character limit
            return jsonify({'error': 'Text too long'}), 400
        
        result = transcriber.medical_processor.process_text(text)
        
        return jsonify({
            'success': True,
            **result
        })
        
    except Exception as e:
        logger.error(f"Text processing error: {e}")
        return jsonify({'error': 'Processing failed'}), 500

# SocketIO handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    transcriber.stats['sessions_started'] += 1
    
    emit('status', {
        'message': 'Connected to production medical transcription service',
        'type': 'success',
        'gpu_accelerated': torch.cuda.is_available(),
        'model_size': transcriber.model_size
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('audio_data')
def handle_audio_data(data):
    """Handle audio transcription with production error handling"""
    try:
        # Validate input
        audio_base64 = data.get('audio', '')
        original_size = data.get('originalSize', 0)
        
        if len(audio_base64) < 100:
            emit('transcription_result', {'success': False, 'error': 'No audio data'})
            return
        
        if original_size > 50_000_000:  # 50MB limit
            emit('transcription_result', {'success': False, 'error': 'Audio too large'})
            return
        
        # Decode audio with validation
        try:
            # Add padding if needed
            missing_padding = len(audio_base64) % 4
            if missing_padding:
                audio_base64 += '=' * (4 - missing_padding)
            
            audio_bytes = base64.b64decode(audio_base64, validate=True)
            
        except Exception as e:
            logger.error(f"Base64 decode error: {e}")
            emit('transcription_result', {'success': False, 'error': 'Invalid audio encoding'})
            return
        
        if len(audio_bytes) < 1000:
            emit('transcription_result', {'success': False, 'error': 'Audio too short'})
            return
        
        # Process audio
        timestamp = int(time.time() * 1000000)
        temp_dir = Path('/app/temp')
        temp_dir.mkdir(exist_ok=True)
        temp_webm = temp_dir / f"audio_{timestamp}.webm"
        
        try:
            # Write audio file
            with open(temp_webm, 'wb') as f:
                f.write(audio_bytes)
            
            # Transcribe
            result = transcriber.transcribe_webm_file(str(temp_webm))
            emit('transcription_result', result)
            
        finally:
            # Cleanup
            try:
                if temp_webm.exists():
                    temp_webm.unlink()
            except:
                pass
                
    except Exception as e:
        logger.error(f"Audio processing error: {e}")
        emit('transcription_result', {
            'success': False,
            'error': 'Server processing error',
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('get_stats')
def handle_get_stats():
    """Send current statistics"""
    emit('stats_update', transcriber.get_stats())

@socketio.on('get_vocabulary')
def handle_get_vocabulary():
    """Send vocabulary information"""
    emit('vocabulary_info', transcriber.get_vocabulary_info())

# Production startup
if __name__ == '__main__':
    logger.info("=== Starting Production Medical Dictation Service ===")
    logger.info(f"GPU Available: {torch.cuda.is_available()}")
    logger.info(f"Model: {transcriber.model_size}")
    logger.info(f"Device: {transcriber.device}")
    
    # Ensure directories exist
    Path('/app/temp').mkdir(exist_ok=True)
    Path('/app/logs').mkdir(exist_ok=True)
    
    # Start the application
    socketio.run(
        app, 
        debug=False, 
        host='0.0.0.0', 
        port=5000,
        use_reloader=False
    )
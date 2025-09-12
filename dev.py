#!/usr/bin/env python3
"""
Enhanced Medical Speech-to-Text Web Application - FIXED AUDIO PROCESSING
Flask web server with comprehensive radiology vocabularies and voice commands
"""

import whisper
import wave
import time
import re
import os
import base64
from datetime import datetime
import logging
from typing import Dict, List
import subprocess
import tempfile

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

# Import our enhanced medical processing modules
from medical.vocabularies.imaging_modalities import ImagingVocabularies
from medical.vocabularies.anatomy import AnatomyVocabularies
from medical.vocabularies.measurements import MeasurementProcessor
from medical.vocabularies.pathology import PathologyVocabularies
from medical.commands import VoiceCommandProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/medical_dictation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AudioProcessor:
    """Enhanced audio processing with better WebM handling"""
    
    @staticmethod
    def convert_webm_to_wav(webm_path: str, wav_path: str) -> bool:
        """Convert WebM to WAV using FFmpeg with error handling"""
        try:
            # First, check if the WebM file is valid
            if not os.path.exists(webm_path) or os.path.getsize(webm_path) < 100:
                logger.error(f"WebM file is too small or missing: {webm_path}")
                return False
            
            # Use FFmpeg to convert WebM to WAV with specific parameters for web audio
            cmd = [
                'ffmpeg', '-y', '-v', 'error',
                '-i', webm_path,
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-f', 'wav',
                wav_path
            ]
            
            # Run FFmpeg with error capture
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30  # 30 second timeout
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg conversion failed: {result.stderr}")
                return False
            
            # Verify the output file was created and has content
            if not os.path.exists(wav_path) or os.path.getsize(wav_path) < 1000:
                logger.error(f"Converted WAV file is too small: {wav_path}")
                return False
            
            logger.info(f"Successfully converted {webm_path} to {wav_path}")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg conversion timeout")
            return False
        except Exception as e:
            logger.error(f"Audio conversion error: {e}")
            return False
    
    @staticmethod
    def validate_webm_file(webm_path: str) -> bool:
        """Validate WebM file using FFprobe"""
        try:
            cmd = [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_format', '-show_streams',
                webm_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"WebM validation error: {e}")
            return False

class EnhancedMedicalTermProcessor:
    """Enhanced medical term processing with comprehensive vocabularies"""
    
    def __init__(self):
        # Initialize all vocabulary modules
        self.imaging_vocab = ImagingVocabularies()
        self.anatomy_vocab = AnatomyVocabularies()
        self.measurement_processor = MeasurementProcessor()
        self.pathology_vocab = PathologyVocabularies()
        self.command_processor = VoiceCommandProcessor()
        
        # Combine all medical terms
        self.all_medical_terms = self._compile_all_terms()
        self.all_corrections = self._compile_all_corrections()
        
        # Statistics tracking
        self.processing_stats = {
            'terms_enhanced': 0,
            'measurements_processed': 0,
            'commands_executed': 0,
            'pathology_classified': 0
        }
    
    def _compile_all_terms(self):
        """Compile all medical terms from all vocabularies"""
        all_terms = set()
        
        # Add imaging modality terms
        all_terms.update(self.imaging_vocab.get_all_terms())
        
        # Add anatomy terms
        all_terms.update(self.anatomy_vocab.get_all_anatomy_terms())
        
        # Add pathology terms
        all_terms.update(self.pathology_vocab.get_all_pathology_terms())
        
        # Add measurement terms
        for category in self.measurement_processor.units.values():
            all_terms.update(category['primary'])
            all_terms.update(category.get('variations', []))
        
        return list(all_terms)
    
    def _compile_all_corrections(self):
        """Compile all correction dictionaries"""
        corrections = {}
        
        # Add imaging corrections
        corrections.update(self.imaging_vocab.get_corrections_dict())
        
        # Add anatomy corrections
        corrections.update(self.anatomy_vocab.get_anatomy_corrections())
        
        # Add pathology corrections
        corrections.update(self.pathology_vocab.get_pathology_corrections())
        
        # Add measurement corrections
        corrections.update(self.measurement_processor.measurement_corrections)
        
        return corrections
    
    def process_text(self, text: str) -> Dict:
        """Comprehensive text processing with all enhancements"""
        if not text.strip():
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
        
        # 1. Check for voice commands first
        command_result = self.command_processor.process_command(text)
        if command_result.get('command_found'):
            result['commands'].append(command_result)
            self.processing_stats['commands_executed'] += 1
            # If it's a command, return early
            if not command_result.get('requires_followup'):
                result['processed_text'] = command_result.get('formatted_output', text)
                return result
        
        # 2. Apply medical term corrections
        processed_text = self._apply_corrections(result['processed_text'])
        
        # 3. Process measurements
        processed_text, measurements = self.measurement_processor.process_measurements(processed_text)
        result['measurements'] = measurements
        if measurements:
            self.processing_stats['measurements_processed'] += len(measurements)
        
        # 4. Detect and enhance medical terminology
        processed_text, enhancements = self._enhance_medical_terms(processed_text)
        result['enhancements'] = enhancements
        
        # 5. Detect imaging modalities
        result['modalities_detected'] = self._detect_modalities(processed_text)
        
        # 6. Detect anatomical mentions
        result['anatomy_mentioned'] = self._detect_anatomy(processed_text)
        
        # 7. Detect pathology terms
        result['pathology_found'] = self._detect_pathology(processed_text)
        
        # 8. Final formatting
        result['processed_text'] = self._final_formatting(processed_text)
        
        return result
    
    def _apply_corrections(self, text: str) -> str:
        """Apply speech recognition corrections"""
        corrected_text = text
        corrections_applied = []
        
        for correct_term, misheard_variants in self.all_corrections.items():
            for variant in misheard_variants:
                pattern = r'\b' + re.escape(variant) + r'\b'
                if re.search(pattern, corrected_text, re.IGNORECASE):
                    corrected_text = re.sub(pattern, correct_term, corrected_text, flags=re.IGNORECASE)
                    corrections_applied.append(f"{variant} → {correct_term}")
        
        if corrections_applied:
            self.processing_stats['terms_enhanced'] += len(corrections_applied)
        
        return corrected_text
    
    def _enhance_medical_terms(self, text: str) -> tuple:
        """Enhance medical terminology in text"""
        enhanced_text = text
        enhancements = []
        
        # Common medical abbreviations and expansions
        medical_abbrev = {
            'bp': 'blood pressure',
            'hr': 'heart rate',
            'rr': 'respiratory rate',
            'ct': 'computed tomography',
            'mri': 'magnetic resonance imaging',
            'us': 'ultrasound',
            'pe': 'pulmonary embolism',
            'dvt': 'deep vein thrombosis',
            'cad': 'coronary artery disease',
            'chf': 'congestive heart failure',
            'copd': 'chronic obstructive pulmonary disease',
            'uti': 'urinary tract infection',
            'gi': 'gastrointestinal',
            'gu': 'genitourinary'
        }
        
        for abbrev, expansion in medical_abbrev.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            if re.search(pattern, enhanced_text, re.IGNORECASE):
                enhanced_text = re.sub(pattern, expansion, enhanced_text, flags=re.IGNORECASE)
                enhancements.append(f"{abbrev.upper()} → {expansion}")
        
        return enhanced_text, enhancements
    
    def _detect_modalities(self, text: str) -> List[str]:
        """Detect imaging modalities mentioned in text"""
        modalities = []
        
        # Check for CT terms
        ct_terms = self.imaging_vocab.ct_vocabulary
        for category_terms in ct_terms.values():
            for term in category_terms:
                if term.lower() in text.lower():
                    if 'CT' not in modalities:
                        modalities.append('CT')
                    break
        
        # Check for MRI terms
        mri_terms = self.imaging_vocab.mri_vocabulary
        for category_terms in mri_terms.values():
            for term in category_terms:
                if term.lower() in text.lower():
                    if 'MRI' not in modalities:
                        modalities.append('MRI')
                    break
        
        # Check for other modalities
        if any(term in text.lower() for term in ['ultrasound', 'sonography', 'doppler']):
            modalities.append('Ultrasound')
        
        if any(term in text.lower() for term in ['x-ray', 'radiograph', 'chest x-ray']):
            modalities.append('X-ray')
        
        if any(term in text.lower() for term in ['pet', 'nuclear medicine', 'scintigraphy']):
            modalities.append('Nuclear Medicine')
        
        return modalities
    
    def _detect_anatomy(self, text: str) -> List[str]:
        """Detect anatomical structures mentioned"""
        anatomy_mentioned = []
        
        # Check major organ systems
        systems = {
            'cardiovascular': self.anatomy_vocab.cardiovascular,
            'pulmonary': self.anatomy_vocab.pulmonary,
            'gastrointestinal': self.anatomy_vocab.gastrointestinal,
            'genitourinary': self.anatomy_vocab.genitourinary,
            'musculoskeletal': self.anatomy_vocab.musculoskeletal,
            'neurological': self.anatomy_vocab.neurological
        }
        
        for system_name, system_terms in systems.items():
            for category_terms in system_terms.values():
                for term in category_terms:
                    if term.lower() in text.lower():
                        if system_name.capitalize() not in anatomy_mentioned:
                            anatomy_mentioned.append(system_name.capitalize())
                        break
                if system_name.capitalize() in anatomy_mentioned:
                    break
        
        return anatomy_mentioned
    
    def _detect_pathology(self, text: str) -> List[str]:
        """Detect pathological terms"""
        pathology_terms = []
        
        # Check for enhancement patterns
        enhancement_terms = self.pathology_vocab.enhancement_patterns
        for category_terms in enhancement_terms.values():
            for term in category_terms:
                if term.lower() in text.lower():
                    pathology_terms.append(term)
        
        # Check for morphology terms
        morphology_terms = self.pathology_vocab.morphology_terms
        for category_terms in morphology_terms.values():
            for term in category_terms:
                if term.lower() in text.lower():
                    pathology_terms.append(term)
        
        # Remove duplicates and limit to top 5
        return list(set(pathology_terms))[:5]
    
    def _final_formatting(self, text: str) -> str:
        """Final text formatting and capitalization"""
        # Capitalize first letter of sentences
        sentences = re.split(r'([.!?]+)', text)
        formatted_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i % 2 == 0 and sentence.strip():  # Actual sentence (not punctuation)
                sentence = sentence.strip().capitalize()
            formatted_sentences.append(sentence)
        
        return ''.join(formatted_sentences)
    
    def get_vocabulary_stats(self) -> Dict:
        """Get comprehensive vocabulary statistics"""
        imaging_stats = self.imaging_vocab.get_vocabulary_stats()
        anatomy_stats = self.anatomy_vocab.get_anatomy_stats()
        pathology_stats = self.pathology_vocab.get_pathology_stats()
        measurement_stats = self.measurement_processor.get_measurement_stats()
        command_stats = self.command_processor.get_command_stats()
        
        return {
            **imaging_stats,
            **anatomy_stats,
            **pathology_stats,
            **measurement_stats,
            **command_stats,
            'total_medical_terms': len(self.all_medical_terms),
            'total_corrections': len(self.all_corrections),
            **self.processing_stats
        }

class EnhancedRadiologyTranscriber:
    """Enhanced radiology transcription system with fixed audio processing"""
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.sample_rate = 16000
        
        # Initialize components
        self.whisper_model = None
        self.medical_processor = EnhancedMedicalTermProcessor()
        self.audio_processor = AudioProcessor()
        
        # Statistics
        self.stats = {
            'sessions_started': 0,
            'chunks_processed': 0,
            'total_processing_time': 0,
            'transcriptions': 0,
            'commands_processed': 0,
            'terms_corrected': 0,
            'avg_processing_time': 0.0,
            'audio_conversion_errors': 0
        }
        
        # Load model
        self.load_model()
    
    def load_model(self):
        """Load the Whisper model"""
        logger.info(f"Loading Whisper model '{self.model_size}'...")
        try:
            self.whisper_model = whisper.load_model(self.model_size)
            logger.info("Model loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def transcribe_webm_file(self, webm_filename: str) -> Dict:
        """Transcribe WebM audio file with enhanced processing and error handling"""
        try:
            start_time = time.time()
            
            # Check file exists and has minimum size
            if not os.path.exists(webm_filename):
                return {
                    'success': False,
                    'error': 'Audio file not found',
                    'timestamp': datetime.now().isoformat()
                }
            
            file_size = os.path.getsize(webm_filename)
            if file_size < 100:  # Very small files are likely corrupted
                return {
                    'success': False,
                    'error': 'Audio file too small (likely corrupted)',
                    'timestamp': datetime.now().isoformat()
                }
            
            logger.info(f"Processing WebM file: {webm_filename}, size: {file_size} bytes")
            
            # Validate WebM file first
            if not self.audio_processor.validate_webm_file(webm_filename):
                logger.error(f"Invalid WebM file: {webm_filename}")
                self.stats['audio_conversion_errors'] += 1
                return {
                    'success': False,
                    'error': 'Invalid or corrupted WebM audio file',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Create temporary WAV file for conversion
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
                wav_filename = temp_wav.name
            
            try:
                # Convert WebM to WAV using FFmpeg
                if not self.audio_processor.convert_webm_to_wav(webm_filename, wav_filename):
                    self.stats['audio_conversion_errors'] += 1
                    return {
                        'success': False,
                        'error': 'Failed to convert audio format',
                        'timestamp': datetime.now().isoformat()
                    }
                
                # Transcribe the converted WAV file
                result = self.whisper_model.transcribe(
                    wav_filename,
                    language="en",
                    task="transcribe",
                    fp16=False,
                    verbose=False,
                    temperature=0.2,
                    no_speech_threshold=0.6,
                    condition_on_previous_text=False  # Avoid context errors
                )
                
                logger.info(f"Whisper transcription result: '{result['text']}'")
                
                # Process with enhanced medical terminology
                processed_result = self.medical_processor.process_text(result["text"])
                
                # Calculate processing time
                processing_time = time.time() - start_time
                
                # Update statistics
                self.stats['chunks_processed'] += 1
                self.stats['total_processing_time'] += processing_time
                self.stats['transcriptions'] += 1
                
                if processed_result['commands']:
                    self.stats['commands_processed'] += len(processed_result['commands'])
                
                if processed_result['enhancements']:
                    self.stats['terms_corrected'] += len(processed_result['enhancements'])
                
                self.stats['avg_processing_time'] = (
                    self.stats['total_processing_time'] / self.stats['chunks_processed']
                    if self.stats['chunks_processed'] > 0 else 0
                )
                
                return {
                    'success': True,
                    'text': processed_result['processed_text'],
                    'raw_text': processed_result['raw_text'],
                    'processing_time': processing_time,
                    'timestamp': datetime.now().isoformat(),
                    'terminology_applied': processed_result['enhancements'],
                    'measurements_found': processed_result['measurements'],
                    'commands': processed_result['commands'],
                    'modalities_detected': processed_result['modalities_detected'],
                    'anatomy_mentioned': processed_result['anatomy_mentioned'],
                    'pathology_found': processed_result['pathology_found'],
                    'file_size': file_size,
                    'segments': len(result.get('segments', [])),
                    'language': result.get('language', 'unknown'),
                    'conversion_successful': True
                }
            
            finally:
                # Clean up temporary WAV file
                try:
                    if os.path.exists(wav_filename):
                        os.remove(wav_filename)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup WAV file: {cleanup_error}")
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        return self.stats
    
    def get_vocabulary_info(self) -> Dict:
        """Get vocabulary information"""
        return self.medical_processor.get_vocabulary_stats()

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'enhanced-medical-speech-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize enhanced transcriber
transcriber = EnhancedRadiologyTranscriber(model_size="base")

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/option2')
def option():
    """Serve the main page"""
    return render_template('index1.html')

@app.route('/stats')
def stats():
    """Get current statistics"""
    return jsonify(transcriber.get_stats())

@app.route('/vocabulary')
def vocabulary():
    """Get vocabulary information"""
    return jsonify(transcriber.get_vocabulary_info())

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("Client connected")
    transcriber.stats['sessions_started'] += 1
    vocab_stats = transcriber.get_vocabulary_info()
    emit('status', {
        'message': 'Connected to enhanced radiology transcription service',
        'type': 'success',
        'vocabulary_size': vocab_stats.get('total_medical_terms', 0)
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("Client disconnected")

@socketio.on('audio_data')
def handle_audio_data(data):
    """Handle incoming audio data with enhanced processing and error handling"""
    try:
        audio_base64 = data.get('audio', '')
        original_size = data.get('originalSize', 0)
        base64_length = data.get('base64Length', len(audio_base64))
        mime_type = data.get('mimeType', 'audio/webm')
        
        logger.info(f"Received audio: {len(audio_base64)} base64 chars, expected original size: {original_size} bytes, base64 length: {base64_length}")
        
        if len(audio_base64) < 100:  # Very short base64 indicates empty audio
            emit('transcription_result', {
                'success': False,
                'error': 'Audio data too short',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        # Decode audio data with better error handling and validation
        try:
            # Ensure base64 string has proper padding
            missing_padding = len(audio_base64) % 4
            if missing_padding:
                audio_base64 += '=' * (4 - missing_padding)
            
            audio_bytes = base64.b64decode(audio_base64, validate=True)
            logger.info(f"Successfully decoded {len(audio_bytes)} bytes from {len(audio_base64)} base64 characters")
            
        except Exception as decode_error:
            logger.error(f"Base64 decode error: {decode_error}")
            logger.error(f"Base64 string preview (first 100 chars): {audio_base64[:100]}")
            emit('transcription_result', {
                'success': False,
                'error': f'Failed to decode audio data: {str(decode_error)}',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        # Validate decoded size matches expectations
        size_difference = abs(len(audio_bytes) - original_size)
        if size_difference > 100:  # Allow some variance due to encoding
            logger.warning(f"Size mismatch: decoded {len(audio_bytes)} bytes, expected {original_size} bytes")
        
        if len(audio_bytes) < 1000:  # Minimum viable audio size
            emit('transcription_result', {
                'success': False,
                'error': f'Decoded audio too short: {len(audio_bytes)} bytes',
                'timestamp': datetime.now().isoformat()
            })
            return
        
        # Save as WebM file with unique timestamp
        timestamp = int(time.time() * 1000000)  # More precise timestamp
        temp_webm = f"temp_audio_{timestamp}.webm"
        
        try:
            # Write WebM file
            with open(temp_webm, 'wb') as f:
                bytes_written = f.write(audio_bytes)
            
            actual_file_size = os.path.getsize(temp_webm)
            logger.info(f"Saved WebM file: {temp_webm}")
            logger.info(f"  - Bytes written: {bytes_written}")
            logger.info(f"  - Actual file size: {actual_file_size}")
            logger.info(f"  - Expected size: {len(audio_bytes)}")
            
            if bytes_written != len(audio_bytes) or actual_file_size != len(audio_bytes):
                logger.error("File write size mismatch!")
                emit('transcription_result', {
                    'success': False,
                    'error': 'File write error - size mismatch',
                    'timestamp': datetime.now().isoformat()
                })
                return
            
            # Process with enhanced transcriber
            result = transcriber.transcribe_webm_file(temp_webm)
            
            # Add debugging info to result
            result['debug_info'] = {
                'original_size': original_size,
                'decoded_size': len(audio_bytes),
                'file_size': actual_file_size,
                'base64_length': len(audio_base64)
            }
            
            # Send enhanced result to client
            emit('transcription_result', result)
            
        finally:
            # Clean up temp file
            try:
                if os.path.exists(temp_webm):
                    os.remove(temp_webm)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
        
    except Exception as e:
        logger.error(f"Error processing audio data: {e}")
        emit('transcription_result', {
            'success': False,
            'error': f"Processing error: {str(e)}",
            'timestamp': datetime.now().isoformat()
        })

@socketio.on('get_stats')
def handle_get_stats():
    """Send current statistics"""
    stats = transcriber.get_stats()
    emit('stats_update', stats)

@app.route('/process_text', methods=['POST'])
def process_text():
    """Process text without audio - for Web Speech API integration"""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'})
    
    # Use your existing medical processor
    result = transcriber.medical_processor.process_text(text)
    
    return jsonify({
        'success': True,
        'processed_text': result['processed_text'],
        'raw_text': result['raw_text'],
        'enhancements': result['enhancements'],
        'commands': result['commands'],
        'measurements': result['measurements'],
        'modalities_detected': result['modalities_detected'],
        'anatomy_mentioned': result['anatomy_mentioned'],
        'pathology_found': result['pathology_found']
    })

@socketio.on('get_vocabulary')
def handle_get_vocabulary():
    """Send vocabulary information"""
    vocab_info = transcriber.get_vocabulary_info()
    emit('vocabulary_info', vocab_info)

if __name__ == '__main__':
    logger.info("Starting Enhanced Radiology Speech-to-Text Application...")
    logger.info(f"Model loaded: {transcriber.model_size}")
    logger.info("Enhanced features: Imaging modalities, Anatomy, Measurements, Pathology, Voice commands")
    logger.info("Fixed audio processing with WebM validation and conversion")
    logger.info("Access the application at http://localhost:5000")
    
    # Create directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('medical/vocabularies', exist_ok=True)
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
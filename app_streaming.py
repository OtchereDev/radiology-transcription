#!/usr/bin/env python3
"""
Production Medical Speech-to-Text with Streaming Support
Faster-Whisper + Silero VAD for low-latency transcription
"""

import os
import logging
from datetime import datetime
from pathlib import Path
import signal
import sys

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import torch

from streaming.manager import StreamingManager

# Import medical processing (your existing code)
try:
    from medical.vocabularies.imaging_modalities import ImagingVocabularies
    from medical.vocabularies.anatomy import AnatomyVocabularies
    from medical.vocabularies.measurements import MeasurementProcessor
    from medical.vocabularies.pathology import PathologyVocabularies
    from medical.commands import VoiceCommandProcessor
    
    MEDICAL_MODULES_AVAILABLE = True
except ImportError:
    MEDICAL_MODULES_AVAILABLE = False
    logging.warning("Medical vocabulary modules not available")

# Configure logging
def setup_logging():
    log_dir = Path('/app/logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'streaming_dictation.log'),
            logging.StreamHandler()
        ]
    )
    
    # Reduce noise from libraries
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('socketio').setLevel(logging.WARNING)
    logging.getLogger('engineio').setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger(__name__)


class MedicalProcessor:
    """Medical text processing wrapper"""
    
    def __init__(self):
        if MEDICAL_MODULES_AVAILABLE:
            self.imaging_vocab = ImagingVocabularies()
            self.anatomy_vocab = AnatomyVocabularies()
            self.measurement_processor = MeasurementProcessor()
            self.pathology_vocab = PathologyVocabularies()
            self.command_processor = VoiceCommandProcessor()
        else:
            self.imaging_vocab = None
    
    def process_text(self, text: str) -> dict:
        """Process transcribed text with medical enhancements"""
        if not MEDICAL_MODULES_AVAILABLE or not text.strip():
            return {
                'processed_text': text,
                'raw_text': text,
                'enhancements': [],
                'measurements': [],
                'commands': []
            }
        
        # Check for voice commands
        command_result = self.command_processor.process_command(text)
        if command_result.get('command_found'):
            return {
                'processed_text': text,
                'raw_text': text,
                'enhancements': [],
                'measurements': [],
                'commands': [command_result]
            }
        
        # Process measurements
        processed_text, measurements = self.measurement_processor.process_measurements(text)
        
        # Basic medical term enhancement
        enhancements = []
        # Add your existing enhancement logic here
        
        return {
            'processed_text': processed_text,
            'raw_text': text,
            'enhancements': enhancements,
            'measurements': measurements,
            'commands': []
        }
    
    def get_stats(self) -> dict:
        """Get vocabulary statistics"""
        if not MEDICAL_MODULES_AVAILABLE:
            return {'total_medical_terms': 0}
        
        return {
            'total_medical_terms': 1000,  # Placeholder
            'ct_terms': 100,
            'mri_terms': 100,
            'anatomy_terms': 200
        }


# Initialize Flask app
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'streaming-medical-speech-key'),
    MAX_CONTENT_LENGTH=50 * 1024 * 1024,  # 50MB limit
    JSON_SORT_KEYS=False
)

# Initialize SocketIO with streaming optimizations
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    logger=False,
    engineio_logger=False,
    ping_timeout=120,
    ping_interval=25,
    max_http_buffer_size=10 * 1024 * 1024  # 10MB for audio chunks
)

# Initialize streaming manager
logger.info("Initializing Streaming Manager...")
streaming_manager = StreamingManager(
    model_size=os.getenv('WHISPER_MODEL_SIZE', 'large-v3'),
    device="cuda" if torch.cuda.is_available() else "cpu",
    max_concurrent_sessions=int(os.getenv('MAX_CONCURRENT_SESSIONS', '10'))
)

# Initialize medical processor
medical_processor = MedicalProcessor()

# Session mapping: socket_id -> session_id
active_sessions = {}

# Graceful shutdown
def signal_handler(sig, frame):
    logger.info('Received shutdown signal. Cleaning up...')
    streaming_manager.shutdown()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# Routes
@app.route('/')
def index():
    """Serve main application"""
    return render_template('index_streaming.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'gpu_available': torch.cuda.is_available(),
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0-streaming',
        'active_sessions': len(active_sessions)
    })

@app.route('/stats')
def stats():
    """System statistics endpoint"""
    return jsonify(streaming_manager.get_stats())

@app.route('/vocabulary')
def vocabulary():
    """Vocabulary information endpoint"""
    return jsonify(medical_processor.get_stats())


# SocketIO Event Handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    
    emit('status', {
        'message': 'Connected to streaming medical transcription service',
        'type': 'success',
        'gpu_accelerated': torch.cuda.is_available(),
        'streaming_enabled': True
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")
    
    # Cleanup session if exists
    if request.sid in active_sessions:
        session_id = active_sessions[request.sid]
        streaming_manager.remove_session(session_id)
        del active_sessions[request.sid]

@socketio.on('start_streaming')
def handle_start_streaming():
    """Start streaming session"""
    try:
        session_id = f"session_{request.sid}_{int(datetime.now().timestamp())}"
        
        # Callback for transcription results
        def on_transcription(result):
            """Send transcription result to client"""
            try:
                # Process with medical enhancements
                if result['success']:
                    enhanced = medical_processor.process_text(result['text'])
                    result.update(enhanced)
                
                # Emit to client
                emit('transcription_result', result, room=request.sid)
                
            except Exception as e:
                logger.error(f"Error in transcription callback: {e}")
                emit('transcription_error', {'error': str(e)}, room=request.sid)
        
        # Create session
        session = streaming_manager.create_session(session_id, on_transcription)
        session.start()
        
        # Store session mapping
        active_sessions[request.sid] = session_id
        
        logger.info(f"Streaming started: {session_id}")
        
        emit('streaming_started', {
            'session_id': session_id,
            'status': 'active',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error starting streaming: {e}")
        emit('streaming_error', {'error': str(e)})

@socketio.on('stop_streaming')
def handle_stop_streaming():
    """Stop streaming session"""
    try:
        if request.sid in active_sessions:
            session_id = active_sessions[request.sid]
            session = streaming_manager.get_session(session_id)
            
            if session:
                session.stop()
                stats = session.get_stats()
                
                emit('streaming_stopped', {
                    'session_id': session_id,
                    'stats': stats,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Cleanup
                streaming_manager.remove_session(session_id)
                del active_sessions[request.sid]
                
                logger.info(f"Streaming stopped: {session_id}")
        
    except Exception as e:
        logger.error(f"Error stopping streaming: {e}")
        emit('streaming_error', {'error': str(e)})

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """Handle streaming audio chunk"""
    try:
        if request.sid not in active_sessions:
            emit('streaming_error', {'error': 'No active session'})
            return
        
        session_id = active_sessions[request.sid]
        session = streaming_manager.get_session(session_id)
        
        if not session:
            emit('streaming_error', {'error': 'Session not found'})
            return
        
        # Extract audio data
        audio_data = data.get('audio')
        if not audio_data:
            return
        
        # Process audio chunk
        session.process_audio_chunk(audio_data, encoding='base64')
        
    except Exception as e:
        logger.error(f"Error processing audio chunk: {e}")
        emit('streaming_error', {'error': str(e)})

@socketio.on('get_stats')
def handle_get_stats():
    """Send current statistics"""
    emit('stats_update', streaming_manager.get_stats())

@socketio.on('get_vocabulary')
def handle_get_vocabulary():
    """Send vocabulary information"""
    emit('vocabulary_info', medical_processor.get_stats())


# Periodic cleanup task
def cleanup_inactive_sessions():
    """Periodically cleanup inactive sessions"""
    while True:
        socketio.sleep(60)  # Run every minute
        try:
            cleaned = streaming_manager.cleanup_inactive_sessions(timeout_seconds=300)
            if cleaned > 0:
                logger.info(f"Cleaned up {cleaned} inactive sessions")
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")


# Start cleanup task
socketio.start_background_task(cleanup_inactive_sessions)


# Production startup
if __name__ == '__main__':
    logger.info("=== Starting Streaming Medical Dictation Service ===")
    logger.info(f"GPU Available: {torch.cuda.is_available()}")
    logger.info(f"Model: {os.getenv('WHISPER_MODEL_SIZE', 'large-v3')}")
    logger.info(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    
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
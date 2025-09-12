#!/bin/bash
set -e

# Wait for GPU to be available
echo "Checking GPU availability..."
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
python -c "import torch; print(f'GPU count: {torch.cuda.device_count()}')" || true

# Pre-warm the model
echo "Pre-warming Whisper model..."
python -c "
import whisper
import os
model_size = os.getenv('WHISPER_MODEL_SIZE', 'large-v3')
print(f'Loading {model_size} model...')
model = whisper.load_model(model_size)
print('Model loaded successfully')
"

# Start the application
echo "Starting Medical Dictation Service..."
exec "$@"
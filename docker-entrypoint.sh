#!/bin/bash
set -e

echo "=========================================="
echo "Medical Dictation Streaming Service"
echo "=========================================="

# Check GPU availability
echo "Checking GPU availability..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
    python -c "import torch; print(f'PyTorch CUDA available: {torch.cuda.is_available()}')"
    python -c "import torch; print(f'CUDA device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
else
    echo "⚠️  GPU not available, will run on CPU"
fi

# Pre-warm models
echo ""
echo "Pre-warming models..."
python -c "
import torch
from faster_whisper import WhisperModel
import os

model_size = os.getenv('WHISPER_MODEL_SIZE', 'large-v3')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
compute_type = 'float16' if device == 'cuda' else 'int8'

print(f'Loading Faster-Whisper {model_size} on {device}...')
model = WhisperModel(model_size, device=device, compute_type=compute_type)
print('✓ Faster-Whisper loaded')

print('Loading Silero VAD...')
vad_model, utils = torch.hub.load('snakers4/silero-vad', 'silero_vad', force_reload=False)
print('✓ Silero VAD loaded')

print('')
print('All models loaded successfully!')
"

# Start the application
echo ""
echo "Starting Medical Dictation Streaming Service..."
echo "=========================================="
echo ""

exec "$@"
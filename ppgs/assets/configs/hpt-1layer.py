CONFIG = 'hpt-1layer'
MODULE = 'ppgs'

INPUT_CHANNELS = 768 #dimensionality of wav2vec2 latents
REPRESENTATION = 'w2v2fb'
MODEL = 'transformer'
NUM_WORKERS=4
EVALUATION_BATCHES = 16

NUM_HIDDEN_LAYERS = 1
MAX_FRAMES = 600000
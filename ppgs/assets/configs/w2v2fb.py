CONFIG = 'w2v2fb'
MODULE = 'ppgs'

INPUT_CHANNELS = 768 #dimensionality of wav2vec2 latents
REPRESENTATION = 'w2v2fb'
MODEL = 'transformer'
NUM_WORKERS=6
EVALUATION_BATCHES = 16

NUM_HIDDEN_LAYERS = 5
MAX_FRAMES = 100000
HIDDEN_CHANNELS = 512
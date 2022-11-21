import functools
import torch
import torchaudio

import ppgs


###############################################################################
# API
###############################################################################

#TODO add from_features
def from_audio(
    audio,
    sample_rate,
    model=None,
    checkpoint=ppgs.DEFAULT_CHECKPOINT,
    representation=ppgs.REPRESENTATION,
    gpu=None):
    """Compute phonetic posteriorgram features from audio"""
    with torch.no_grad():
        if model is None:
            model = ppgs.MODEL

        # Cache model on first call; update when GPU or checkpoint changes
        if (not hasattr(from_audio, 'model') or
            from_audio.checkpoint != checkpoint or
            from_audio.gpu != gpu):
            # model = ppgs.model.BaselineModel()
            state_dict = torch.load(checkpoint, map_location='cpu')['model']
            try:
                model.load_state_dict(state_dict)
            except RuntimeError:
                print('Failed to load model, trying again with assumption that model was trained using ddp')
                state_dict = ppgs.load.ddp_to_single_state_dict(state_dict)
                model.load_state_dict(state_dict)
            device = torch.device('cpu' if gpu is None else f'cuda:{gpu}')
            from_audio.model = model.to(device)
            from_audio.checkpoint = checkpoint
            from_audio.gpu = gpu

        # Preprocess audio
        #TODO investigate unsqueeze on dim 0
        features = ppgs.preprocess.from_audio(audio, representation=representation, sample_rate=sample_rate, gpu=gpu)

        # Compute PPGs
        return from_audio.model(features)


def from_file(file, checkpoint=ppgs.DEFAULT_CHECKPOINT, gpu=None):
    """Compute phonetic posteriorgram features from audio file"""
    # Load audio
    audio = ppgs.load.audio(file)
    print(audio.shape)

    # Compute PPGs
    return from_audio(audio, sample_rate=ppgs.SAMPLE_RATE, checkpoint=checkpoint, gpu=gpu)


def from_file_to_file(
    audio_file,
    output_file,
    checkpoint=ppgs.DEFAULT_CHECKPOINT,
    gpu=None):
    """Compute phonetic posteriorgram and save as torch tensor"""
    # Compute PPGs
    result = from_file(audio_file, checkpoint, gpu).detach().cpu()

    # Save to disk
    torch.save(result, output_file)


def from_files_to_files(
    audio_files,
    output_files=None,
    checkpoint=ppgs.DEFAULT_CHECKPOINT,
    gpu=None):
    """Compute phonetic posteriorgrams and save as torch tensors"""
    # Default output files are audio paths with ".pt" extension
    if output_files is None:
        output_files = [file.with_suffix('.pt') for file in audio_files]

    # Bind common parameters
    ppg_fn = functools.partial(
        from_file_to_file,
        checkpoint=checkpoint,
        gpu=gpu)

    # Compute PPGs
    for (audio_file, output_file) in zip(audio_files, output_files):
        ppg_fn(audio_file, output_file)


###############################################################################
# Utilities
###############################################################################


def resample(audio, sample_rate, target_rate=ppgs.SAMPLE_RATE):
    """Perform audio resampling"""
    if sample_rate == target_rate:
        return audio
    resampler = torchaudio.transforms.Resample(sample_rate, target_rate)
    resampler = resampler.to(audio.device)
    return resampler(audio)

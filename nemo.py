from pyannote.audio import Pipeline
import torch

# Replace 'HUGGINGFACE_ACCESS_TOKEN_GOES_HERE' with your actual Hugging Face access token
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token="")

# Send pipeline to GPU if available
pipeline.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))

# Apply pretrained pipeline on an audio file
diarization = pipeline("audio.wav")

# Print the diarization results
for turn, _, speaker in diarization.itertracks(yield_label=True):
    print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")

# backend/test_whisper_small.py
import whisper

audio_path = r"C:\Users\anusu\Downloads\dy_dx னா இவ்வளவு தானா_ _ Basics of Calculus _ LMES [YFwDVViULiA].mp3"

print("Loading Whisper 'small' model...")
model = whisper.load_model("large")  # Better than base

print("Transcribing with Tamil language...")
result = model.transcribe(
    audio_path,
    language="ta",
    task="transcribe",
    temperature=0.0,  # More deterministic
    verbose=True  # Show progress
)

print("\n" + "="*60)
print("TRANSCRIPTION RESULT:")
print("="*60)
print(result['text'])
print("="*60)
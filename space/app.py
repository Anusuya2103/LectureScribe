import gradio as gr
from backend.app.services.transcriber import WhisperTranscriber
from backend.app.services.summarizer import LectureSummarizer

def process_audio(audio_file):
    # Transcribe
    transcriber = WhisperTranscriber()
    result = transcriber.transcribe_audio(audio_file)
    
    # Summarize
    summarizer = LectureSummarizer("huggingface")
    summary = summarizer.generate_minutes(result['text'])
    
    return result['text'], summary['summary']

interface = gr.Interface(
    fn=process_audio,
    inputs=gr.Audio(type="filepath"),
    outputs=[gr.Textbox(label="Transcript"), gr.Textbox(label="Minutes")],
    title="Classroom Minutes Generator"
)

interface.launch()
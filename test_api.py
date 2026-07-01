import requests
import os

# Test upload
url = "http://localhost:8000/api/upload"
files = {'file': ('sample.mp3', open('sample.mp3', 'rb'), 'audio/mpeg')}
response = requests.post(url, files=files)
print("Upload:", response.json())

# Test transcription
if response.status_code == 200:
    data = response.json()
    transcribe_url = "http://localhost:8000/api/transcribe"
    payload = {
        "file_path": data['path'],
        "language": "en"
    }
    trans_response = requests.post(transcribe_url, json=payload)
    print("Transcription:", trans_response.json())
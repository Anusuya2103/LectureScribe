"""
Audio processing service using HuggingFace models.
"""
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import librosa
import numpy as np
from scipy import signal

from ..config import config
from .utils import detect_tamil

class AudioProcessor:
    def __init__(self):
        self.sample_rate = 16000
    
    def load_audio(self, audio_path: str) -> Tuple[np.ndarray, int]:
        try:
            audio, sr = librosa.load(audio_path, sr=self.sample_rate, mono=True)
            return audio, sr
        except Exception as e:
            raise ValueError(f"Error loading audio: {str(e)}")
    
    def save_audio(self, audio: np.ndarray, output_path: str, sr: int = None) -> str:
        sr = sr or self.sample_rate
        import soundfile as sf
        sf.write(output_path, audio, sr)
        return output_path
    
    def denoise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        noise_sample = audio[:int(0.5 * sr)]
        noise_psd = np.mean(np.abs(np.fft.fft(noise_sample))**2)
        n_fft = 2048
        hop_length = 512
        f, t, Zxx = signal.stft(audio, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length)
        Zxx_denoised = Zxx * np.maximum(0, 1 - noise_psd / (np.abs(Zxx)**2 + 1e-10))
        denoised = signal.istft(Zxx_denoised, fs=sr, nperseg=n_fft, noverlap=n_fft - hop_length)[1]
        return denoised
    
    def normalize_volume(self, audio: np.ndarray, target_db: float = -20) -> np.ndarray:
        rms = np.sqrt(np.mean(audio**2))
        if rms > 0:
            gain = 10 ** (target_db / 20) / (rms + 1e-10)
            audio = audio * gain
        return audio
    
    def vad(self, audio: np.ndarray, sr: int, threshold: float = 0.3) -> List[Tuple[float, float]]:
        frame_length = int(0.025 * sr)
        hop_length = int(0.010 * sr)
        energy = []
        for i in range(0, len(audio) - frame_length, hop_length):
            frame = audio[i:i + frame_length]
            energy.append(np.sqrt(np.mean(frame**2)))
        energy = np.array(energy)
        if len(energy) > 0:
            energy = energy / (np.max(energy) + 1e-10)
        is_speech = energy > threshold
        segments = []
        start = None
        for i, speech in enumerate(is_speech):
            if speech and start is None:
                start = i * hop_length / sr
            elif not speech and start is not None:
                end = i * hop_length / sr
                if end - start > 0.5:
                    segments.append((start, end))
                start = None
        if start is not None:
            end = len(audio) / sr
            if end - start > 0.5:
                segments.append((start, end))
        return segments
    
    def split_on_silence(self, audio: np.ndarray, sr: int,
                         min_silence_len: float = 0.5,
                         min_segment_len: float = 2.0) -> List[np.ndarray]:
        segments = self.vad(audio, sr, threshold=0.3)
        if not segments:
            return [audio]
        audio_segments = []
        for start, end in segments:
            if end - start >= min_segment_len:
                start_idx = int(start * sr)
                end_idx = int(end * sr)
                audio_segments.append(audio[start_idx:end_idx])
        return audio_segments
    
    def convert_to_whisper_format(self, audio_path: str) -> str:
        audio, sr = self.load_audio(audio_path)
        audio = self.normalize_volume(audio)
        audio = self.denoise(audio, sr)
        temp_dir = config.temp_dir
        temp_file = temp_dir / f"{Path(audio_path).stem}_processed.wav"
        self.save_audio(audio, str(temp_file))
        return str(temp_file)

class AudioUtils:
    @staticmethod
    def get_audio_duration(audio_path: str) -> float:
        try:
            duration = librosa.get_duration(path=audio_path)
            return duration
        except:
            return 0.0
    
    @staticmethod
    def get_audio_info(audio_path: str) -> Dict[str, Any]:
        try:
            audio, sr = librosa.load(audio_path, sr=None)
            return {
                'duration': len(audio) / sr,
                'sample_rate': sr,
                'samples': len(audio),
                'channels': 1
            }
        except Exception as e:
            return {'error': str(e)}
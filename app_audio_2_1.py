# === Настройка FFmpeg из локальной папки (обязательно в начале!) ===
import os
from pydub import AudioSegment

# Определяем путь к ffmpeg и ffprobe относительно текущего файла
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# FFMPEG_BIN = os.path.join(SCRIPT_DIR, "ffmpeg", "bin")
# FFMPEG_PATH = os.path.join(FFMPEG_BIN, "ffmpeg.exe")
# FFPROBE_PATH = os.path.join(FFMPEG_BIN, "ffprobe.exe")

FFMPEG_PATH = r"C:\\ffmpeg\\bin\\ffmpeg.exe"
FFPROBE_PATH = r"C:\\ffmpeg\\bin\\ffprobe.exe"

# Проверяем, что файлы существуют
if not os.path.exists(FFMPEG_PATH):
    raise FileNotFoundError(f"ffmpeg.exe не найден: {FFMPEG_PATH}")
if not os.path.exists(FFPROBE_PATH):
    raise FileNotFoundError(f"ffprobe.exe не найден: {FFPROBE_PATH}")

# Явно указываем pydub, где искать ffmpeg и ffprobe
AudioSegment.converter = FFMPEG_PATH
AudioSegment.ffprobe = FFPROBE_PATH
# ===================================================================

# === Основной Streamlit-код ===
import streamlit as st
from audiorecorder import audiorecorder
import groq
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
st.title("Запись голоса и распознавание текста")

api_key = os.environ.get("GROQ_API_KEY")

# Запись аудио (возвращает pydub.AudioSegment)
audio = audiorecorder("Начать запись", "Остановить запись", key="audio")

if len(audio) > 0:
    # Воспроизведение в браузере
    st.audio(audio.export().read(), format="audio/wav")
    
    if st.button("Распознать текст"):
        if not api_key:
            st.error("❌ Пожалуйста, добавьте GROQ_API_KEY в файл .env")
        else:
            try:
                # Экспорт в байты формата WAV
                audio_bytes = BytesIO()
                audio.export(audio_bytes, format="wav")
                audio_bytes.seek(0)
                
                # Отправка в Groq
                client = groq.Groq(api_key=api_key)
                transcription = client.audio.transcriptions.create(
                    model="whisper-large-v3-turbo",
                    file=("recording.wav", audio_bytes, "audio/wav")
                )
                
                st.success("✅ Текст успешно распознан!")
                st.write("**Распознанный текст:**")
                st.write(transcription.text)
                
            except Exception as e:
                st.error(f"❌ Ошибка при распознавании: {e}")
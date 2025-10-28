# # -*- coding: utf-8 -*-
# import os
# import sys
# import queue
# import sounddevice as sd
# import vosk
# import json
# import threading
# import numpy as np
# import tempfile
# import time
# from gtts import gTTS
# import pygame
# from transformers import pipeline

# # -----------------------------
# # Configuration
# # -----------------------------
# VOSK_MODEL_PATH = r"vosk-model-small-en-us-0.15"
# FLAN_MODEL_PATH = r"D:\Bot\deep-medicare\flan-t5-small"

# # -----------------------------
# # Queues and State
# # -----------------------------
# tts_queue = queue.Queue()
# listening = True
# stop_flag = threading.Event()
# call_stage = "greeting"
# user_data = {}

# # -----------------------------
# # Detect system audio sample rate
# # -----------------------------
# try:
#     device_info = sd.query_devices(sd.default.device["output"], "output")
#     SYSTEM_SAMPLE_RATE = int(device_info["default_samplerate"])
# except Exception:
#     SYSTEM_SAMPLE_RATE = 44100
# print(f"🎚 System playback sample rate detected: {SYSTEM_SAMPLE_RATE} Hz")

# # -----------------------------
# # Initialize pygame mixer
# # -----------------------------
# pygame.mixer.init(frequency=SYSTEM_SAMPLE_RATE)

# # -----------------------------
# # Load AI model
# # -----------------------------
# print("🧠 Loading AI model (Flan-T5)...")
# generator = pipeline("text2text-generation", model=FLAN_MODEL_PATH)
# print("✅ Flan-T5 loaded successfully")

# # -----------------------------
# # Google Text-to-Speech Worker
# # -----------------------------
# def gtts_tts_worker():
#     """Speak queued text using Google TTS with Irish accent."""
#     global listening
#     while not stop_flag.is_set():
#         text = tts_queue.get()
#         if text is None:
#             break

#         try:
#             print(f"🤖 Bot: {text}")
#             listening = False
#             tts = gTTS(text=text, lang='en', tld='ie')
#             temp_path = os.path.join(tempfile.gettempdir(), f"tts_{int(time.time()*1000)}.mp3")
#             tts.save(temp_path)
#             pygame.mixer.music.load(temp_path)
#             pygame.mixer.music.play()
#             while pygame.mixer.music.get_busy():
#                 time.sleep(0.1)
#             if os.path.exists(temp_path):
#                 os.remove(temp_path)
#         except Exception as e:
#             print(f"⚠️ gTTS error: {e}")
#         finally:
#             listening = True

# threading.Thread(target=gtts_tts_worker, daemon=True).start()

# # -----------------------------
# # Medicare AI Logic
# # -----------------------------
# def medicare_logic(user_text):
#     global call_stage, user_data

#     user_text = user_text.lower()

#     # Greeting Stage
#     if call_stage == "greeting":
#         call_stage = "ask_age"
#         return "Hi, this is Mary from American Benefits. How are you today?"

#     # Ask age
#     elif call_stage == "ask_age":
#         call_stage = "age_response"
#         return "How young are you?"

#     # Parse age response
#     elif call_stage == "age_response":
#         age = None
#         for word in user_text.split():
#             if word.isdigit():
#                 age = int(word)
#                 break
#         if not age:
#             call_stage = "end"
#             return "Sorry, I didn’t catch your age. Thank you for your time, have a nice day."
#         user_data["age"] = age

#         if 40 <= age <= 60:
#             call_stage = "medicare_question"
#             return "Do you currently have Medicare Part A and B active?"
#         else:
#             call_stage = "end"
#             return "Thank you for your time, have a nice day!"

#     # Medicare Part A/B check
#     elif call_stage == "medicare_question":
#         if any(word in user_text for word in ["yes", "active", "i do", "yeah"]):
#             call_stage = "transfer"
#             return "Perfect! I am transferring your call to my senior supervisor now. Thank you for your time."
#         else:
#             call_stage = "end"
#             return "Alright, thank you for your time. Have a great day!"

#     elif call_stage in ["end", "transfer"]:
#         stop_flag.set()
#         return "Goodbye!"

#     return "I'm sorry, could you please repeat that?"

# # -----------------------------
# # Generate natural AI tone
# # -----------------------------
# def ai_reply(prompt, user_input=""):
#     full_prompt = f"You are Mary from American Benefits, a polite Medicare agent. {prompt} Customer said: {user_input}. Respond naturally in one short sentence."
#     reply = generator(full_prompt, max_length=50)[0]['generated_text']
#     return reply.strip()

# # -----------------------------
# # Speech Recognition
# # -----------------------------
# def recognize_speech():
#     global listening
#     model = vosk.Model(VOSK_MODEL_PATH)
#     q = queue.Queue()

#     def callback(indata, frames, time_, status):
#         if listening:
#             q.put(bytes(indata))

#     with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
#                            channels=1, callback=callback):
#         rec = vosk.KaldiRecognizer(model, 16000)
#         print("\n🎤 Bot is live! Say 'quit' to stop.\n")

#         # Start with greeting
#         tts_queue.put(medicare_logic("start"))

#         while not stop_flag.is_set():
#             try:
#                 data = q.get(timeout=1)
#             except queue.Empty:
#                 continue

#             if rec.AcceptWaveform(data):
#                 result = json.loads(rec.Result())
#                 text = result.get("text", "")
#                 if text:
#                     print(f"🗣 You said: {text}")
#                     if text.lower() in ["quit", "exit", "stop"]:
#                         stop_flag.set()
#                         tts_queue.put(None)
#                         break

#                     # Pass to Medicare logic and AI tone
#                     logic_response = medicare_logic(text)
#                     ai_response = ai_reply(logic_response, text)
#                     tts_queue.put(ai_response)

# # -----------------------------
# # Main
# # -----------------------------
# if __name__ == "__main__":
#     print("🚀 Medicare AI Voice Bot started!")
#     print("🧠 Logic: AI agent acts as 'Mary' and follows Medicare qualification steps.\n")

#     try:
#         recognize_speech()
#     except KeyboardInterrupt:
#         print("\n👋 Exiting gracefully...")
#         stop_flag.set()
#         tts_queue.put(None)
#         sys.exit(0)
# #

# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# import os
# import json
# import queue
# import sounddevice as sd
# import vosk
# import threading
# import numpy as np
# import tempfile
# import time
# from gtts import gTTS
# import pygame
# from word2number import w2n  # Converts "forty five" → 45

# # -----------------------------
# # Configuration
# # -----------------------------
# VOSK_MODEL_PATH = r"vosk-model-small-en-us-0.15"

# # -----------------------------
# # Setup Audio and Queues
# # -----------------------------
# tts_queue = queue.Queue()
# stop_flag = threading.Event()
# listening = True

# # Detect system output rate
# try:
#     device_info = sd.query_devices(sd.default.device["output"], "output")
#     SYSTEM_SAMPLE_RATE = int(device_info["default_samplerate"])
# except Exception:
#     SYSTEM_SAMPLE_RATE = 44100

# pygame.mixer.init(frequency=SYSTEM_SAMPLE_RATE)
# print(f"🎚 Playback rate: {SYSTEM_SAMPLE_RATE} Hz")

# # -----------------------------
# # TTS Worker
# # -----------------------------
# def gtts_tts_worker():
#     global listening
#     while not stop_flag.is_set():
#         text = tts_queue.get()
#         if text is None:
#             break
#         try:
#             print(f"🤖 Bot: {text}")
#             listening = False
#             tts = gTTS(text=text, lang='en', tld='com')
#             temp_path = os.path.join(tempfile.gettempdir(), f"tts_{int(time.time()*1000)}.mp3")
#             tts.save(temp_path)
#             pygame.mixer.music.load(temp_path)
#             pygame.mixer.music.play()
#             while pygame.mixer.music.get_busy():
#                 time.sleep(0.1)
#             os.remove(temp_path)
#         except Exception as e:
#             print(f"⚠️ TTS Error: {e}")
#         finally:
#             listening = True

# threading.Thread(target=gtts_tts_worker, daemon=True).start()

# # -----------------------------
# # Conversation Logic
# # -----------------------------
# def get_age_from_text(text):
#     """Extract numeric or word-based ages from text"""
#     text = text.lower()
#     try:
#         for word in text.split():
#             if word.isdigit():
#                 return int(word)
#         return w2n.word_to_num(text)
#     except Exception:
#         return None

# def process_response(user_input):
#     user_input = user_input.lower()

#     # Greetings
#     if "hi" in user_input or "hello" in user_input:
#         return "Hi, this is Mary from American Benefits. How are you doing today?"

#     # Mood-based responses
#     if "fine" in user_input or "good" in user_input or "okay" in user_input:
#         return "That sounds good! May I know how young you are?"
#     elif "not well" in user_input or "bad" in user_input or "sick" in user_input:
#         return "Sad to hear that. I hope you feel better soon. May I know your age?"

#     # Detect Age
#     age = get_age_from_text(user_input)
#     if age:
#         print(f"🧩 Detected Age: {age}")
#         if 40 <= age <= 60:
#             return "Do you have Medicare Part A and B active?"
#         else:
#             return "Thank you for your time. Have a nice day!"

#     # Medicare question handling
#     if "yes" in user_input and ("part a" in user_input or "part b" in user_input):
#         return "Alright, I'm transferring your call to my senior supervisor."
#     elif "no" in user_input and ("part a" in user_input or "part b" in user_input):
#         return "Okay, thank you for your time. Have a nice day!"

#     # Default
#     return "Could you please tell me how old you are?"

# # -----------------------------
# # Speech Recognition
# # -----------------------------
# print("🔊 Loading Vosk model...")
# model = vosk.Model(VOSK_MODEL_PATH)
# recognizer = vosk.KaldiRecognizer(model, 16000)
# audio_queue = queue.Queue()
# print("Speech model ready ✅")

# def callback(indata, frames, time_, status):
#     if listening:
#         audio_queue.put(bytes(indata))

# def recognize_worker():
#     while not stop_flag.is_set():
#         data = audio_queue.get()
#         if recognizer.AcceptWaveform(data):
#             result = json.loads(recognizer.Result())
#             text = result.get("text", "").strip()
#             if text:
#                 print(f"🧠 Heard: {text}")
#                 reply = process_response(text)
#                 tts_queue.put(reply)

# threading.Thread(target=recognize_worker, daemon=True).start()

# # -----------------------------
# # Start Listening
# # -----------------------------
# print("🎤 Listening...")
# with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
#     try:
#         while True:
#             time.sleep(0.1)
#     except KeyboardInterrupt:
#         stop_flag.set()
#         tts_queue.put(None)
#         print("\n👋 Exiting gracefully...")


import os
import json
import queue
import sounddevice as sd
import vosk
import threading
import numpy as np
import tempfile
import time
from gtts import gTTS
import pygame
from word2number import w2n
from call_logic import process_response  # 👈 Import dialogue logic

# -----------------------------
# Configuration
# -----------------------------
VOSK_MODEL_PATH = r"vosk-model-small-en-us-0.15"

# -----------------------------
# Setup Audio and Queues
# -----------------------------
tts_queue = queue.Queue()
stop_flag = threading.Event()
listening = True

# Detect system output rate
try:
    device_info = sd.query_devices(sd.default.device["output"], "output")
    SYSTEM_SAMPLE_RATE = int(device_info["default_samplerate"])
except Exception:
    SYSTEM_SAMPLE_RATE = 44100

pygame.mixer.init(frequency=SYSTEM_SAMPLE_RATE)
print(f"🎚 Playback rate: {SYSTEM_SAMPLE_RATE} Hz")

# -----------------------------
# TTS Worker
# -----------------------------
def gtts_tts_worker():
    global listening
    while not stop_flag.is_set():
        text = tts_queue.get()
        if text is None:
            break
        try:
            print(f"🤖 Bot: {text}")
            listening = False
            tts = gTTS(text=text, lang='en', tld='com')
            temp_path = os.path.join(tempfile.gettempdir(), f"tts_{int(time.time()*1000)}.mp3")
            tts.save(temp_path)
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            os.remove(temp_path)
        except Exception as e:
            print(f"⚠️ TTS Error: {e}")
        finally:
            listening = True

threading.Thread(target=gtts_tts_worker, daemon=True).start()

# -----------------------------
# Speech Recognition
# -----------------------------
print("🔊 Loading Vosk model...")
model = vosk.Model(VOSK_MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, 16000)
audio_queue = queue.Queue()
print("Speech model ready ✅")

def callback(indata, frames, time_, status):
    if listening:
        audio_queue.put(bytes(indata))

def recognize_worker():
    while not stop_flag.is_set():
        data = audio_queue.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                print(f"🧠 Heard: {text}")
                reply = process_response(text)  # 👈 Logic handled externally
                tts_queue.put(reply)

threading.Thread(target=recognize_worker, daemon=True).start()

# -----------------------------
# Start Listening
# -----------------------------
print("🎤 Listening...")
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_flag.set()
        tts_queue.put(None)
        print("\n👋 Exiting gracefully...")

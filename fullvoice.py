
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


# import os
# import time
# import threading
# import tempfile
# import queue
# import json
# from gtts import gTTS
# import pjsua as pj
# import vosk
# import numpy as np
# from call_logic import process_response

# # -----------------------------
# # Configuration
# # -----------------------------
# SIP_DOMAIN = "your.vicidial.server.ip"   # ← change this
# SIP_USER = "9999"                        # ← your SIP extension
# SIP_PASS = "yourpassword"                # ← SIP password
# VOSK_MODEL_PATH = r"vosk-model-small-en-us-0.15"

# # -----------------------------
# # Initialize queues
# # -----------------------------
# audio_queue = queue.Queue()
# tts_queue = queue.Queue()
# stop_flag = threading.Event()

# # -----------------------------
# # Load Vosk model
# # -----------------------------
# print("🔊 Loading Vosk model...")
# model = vosk.Model(VOSK_MODEL_PATH)
# recognizer = vosk.KaldiRecognizer(model, 8000)
# print("Speech model ready ✅")

# # -----------------------------
# # Speech Recognition Worker
# # -----------------------------
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
# # TTS Worker
# # -----------------------------
# def gtts_tts_worker(call):
#     """Convert text to speech and play over RTP"""
#     while not stop_flag.is_set():
#         text = tts_queue.get()
#         if text is None:
#             break
#         try:
#             print(f"🤖 Bot: {text}")
#             tts = gTTS(text=text, lang='en', tld='com')
#             temp_path = os.path.join(tempfile.gettempdir(), f"tts_{int(time.time()*1000)}.wav")
#             tts.save(temp_path)
#             player = pj.AudioMediaPlayer()
#             player.create_player(temp_path, pj.PJMEDIA_FILE_NO_LOOP)
#             player.start_transmit(call._get_conf_slot_media())
#             while player.is_active():
#                 time.sleep(0.1)
#             player.stop_transmit(call._get_conf_slot_media())
#             player = None
#             os.remove(temp_path)
#         except Exception as e:
#             print(f"⚠️ TTS Error: {e}")

# # -----------------------------
# # PJSUA Setup
# # -----------------------------
# class MyCallCallback(pj.CallCallback):
#     def __init__(self, call=None):
#         pj.CallCallback.__init__(self, call)
#         self.call = call
#         self.play_thread = None

#     def on_state(self):
#         print("📞 Call state:", self.call.info().state_text)
#         if self.call.info().state == pj.CallState.DISCONNECTED:
#             print("🔚 Call ended")
#             stop_flag.set()
#             tts_queue.put(None)

#     def on_media_state(self):
#         if self.call.info().media_state == pj.MediaState.ACTIVE:
#             print("🎧 Media active — starting Vosk listener")
#             call_slot = self.call.info().conf_slot
#             # Connect call media to sound device
#             lib.conf_connect(call_slot, 0)
#             lib.conf_connect(0, call_slot)
#             # Start a thread to stream audio to recognizer
#             threading.Thread(target=self.capture_audio, daemon=True).start()
#             # Start TTS playback thread
#             threading.Thread(target=gtts_tts_worker, args=(self.call,), daemon=True).start()

#             # Start the conversation
#             greeting = process_response("")  # Start with greeting
#             tts_queue.put(greeting)

#     def capture_audio(self):
#         """Capture audio frames from the RTP stream"""
#         # NOTE: direct access to RTP frames is complex in PJSUA Python binding.
#         # This is a simplified example assuming lib.conf_connect( ) sends audio to device 0,
#         # and you can intercept system loopback if needed.
#         pass  # Implementation depends on your audio routing

# class MyAccountCallback(pj.AccountCallback):
#     def on_incoming_call(self, call):
#         print("📲 Incoming call!")
#         call_cb = MyCallCallback(call)
#         call.set_callback(call_cb)
#         call.answer(200)
#         print("✅ Call answered")

# # -----------------------------
# # Start PJSUA
# # -----------------------------
# lib = pj.Lib()
# lib.init(log_cfg=pj.LogConfig(level=3, callback=None))
# transport = lib.create_transport(pj.TransportType.UDP, pj.TransportConfig(5060))
# lib.start()

# acc = lib.create_account(pj.AccountConfig(SIP_DOMAIN, SIP_USER, SIP_PASS))
# acc_cb = MyAccountCallback(acc)
# acc.set_callback(acc_cb)

# print(f"🤖 SIP bot registered as {SIP_USER}@{SIP_DOMAIN}")
# print("Waiting for calls... (Ctrl+C to stop)")

# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     print("Exiting...")
#     stop_flag.set()
#     lib.destroy()
#     lib = None



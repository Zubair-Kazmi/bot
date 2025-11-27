import os
import queue
import sounddevice as sd
import soundfile as sf
import vosk
import threading
import json
import sys
import subprocess
import time
from call_logic import process_response, reset_state, TRANSFER_EXTENSION

# -----------------------------
# Configuration
# -----------------------------
VOSK_MODEL_PATH = "vosk-model-small-en-us-0.15" # Ensure this folder name matches exactly
RECORDINGS_PATH = "recordings" # Ensure wav files are here
MAX_CALL_DURATION = 50       # Seconds (Hard limit)
MAX_SILENCE_DURATION = 10    # Seconds (Hangup if user says nothing)
VICIDIAL_TRANSFER_CODE = "#" # Standard Asterisk Blind Transfer Code

# -----------------------------
# Audio Setup (Loopback Device)
# -----------------------------
# IMPORTANT: Adjust 'device' index if needed based on 'python3 -m sounddevice'
# Since Baresip is on hw:1,0, we usually need the index for hw:1,1
# On many AWS setups with Loopback as Card 1, this is index 2 or 3.
INPUT_DEVICE_INDEX = 2  
OUTPUT_DEVICE_INDEX = 2 

# -----------------------------
# State & Queues
# -----------------------------
tts_queue = queue.Queue()
audio_queue = queue.Queue()
stop_flag = threading.Event()

# Call Status Object
call_status = {
    "active": False,
    "start_time": 0,
    "last_speech_time": 0
}

# -----------------------------
# 1. Baresip Controller
# -----------------------------
# Runs Baresip in background and allows sending commands to it
baresip_process = subprocess.Popen(
    ["baresip", "-f", "/home/ubuntu/.baresip"], 
    stdout=subprocess.PIPE, 
    stdin=subprocess.PIPE,  # Enable sending commands (DTMF/Hangup)
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1
)

def send_baresip_cmd(cmd):
    """Sends a command or DTMF tones to Baresip."""
    if baresip_process.stdin:
        print(f"📡 Sending Command: {cmd.strip()}")
        baresip_process.stdin.write(cmd + "\n")
        baresip_process.stdin.flush()

def perform_hangup():
    """Disposes the call as Hangup."""
    print("🔴 Executing HANGUP...")
    send_baresip_cmd("/hangup") 
    call_status["active"] = False

def perform_transfer():
    """
    Disposes the call as Transfer.
    Method: Sends DTMF '#' then the extension.
    """
    print(f"🟢 Executing TRANSFER to {TRANSFER_EXTENSION}...")
    
    # 1. Send Blind Transfer Code
    send_baresip_cmd(VICIDIAL_TRANSFER_CODE)
    time.sleep(0.5) 
    
    # 2. Send Extension Digits one by one
    for digit in TRANSFER_EXTENSION:
        send_baresip_cmd(digit)
        time.sleep(0.2)
    
    print("✅ Transfer sequence sent. Disconnecting bot...")
    time.sleep(2) 
    perform_hangup()

# -----------------------------
# 2. Watchdog (Duration & Silence)
# -----------------------------
def watchdog_worker():
    while not stop_flag.is_set():
        time.sleep(1)
        
        if call_status["active"]:
            now = time.time()
            
            # Check 1: Hard Duration Limit
            duration = now - call_status["start_time"]
            if duration > MAX_CALL_DURATION:
                print(f"⏱️ Limit Reached ({int(duration)}s). Ending Call.")
                perform_hangup()
                continue

            # Check 2: Silence Timeout
            silence_time = now - call_status["last_speech_time"]
            if silence_time > MAX_SILENCE_DURATION:
                print(f"🔇 Silence Timeout ({int(silence_time)}s). Hanging up.")
                perform_hangup()

threading.Thread(target=watchdog_worker, daemon=True).start()

# -----------------------------
# 3. Baresip Monitor (Listener)
# -----------------------------
def baresip_monitor():
    print("📞 SIP Monitor Started...")
    while not stop_flag.is_set():
        line = baresip_process.stdout.readline()
        if not line: break
        
        line = line.strip()
        if line:
            # print(f"[SIP] {line}") # Uncomment for full debug logs

            # Detect Call Start
            if "Call established" in line or "answered" in line:
                print("\n🔔 CALL CONNECTED")
                reset_state()
                call_status["active"] = True
                call_status["start_time"] = time.time()
                call_status["last_speech_time"] = time.time()
                
                # Trigger Initial Greeting
                reply_action, reply_data = process_response("")
                if reply_action == "SPEAK":
                    tts_queue.put(reply_data)

            # Detect Call End
            if "terminated" in line or "Connection reset" in line:
                if call_status["active"]:
                    print("❌ Call Terminated by remote.")
                    call_status["active"] = False
                with audio_queue.mutex:
                    audio_queue.queue.clear()

threading.Thread(target=baresip_monitor, daemon=True).start()

# -----------------------------
# 4. TTS Player
# -----------------------------
def tts_player_worker():
    # Map text responses to your wav filenames
    audio_map = {
        "hi, this is mary": "greeting.wav",
        "how old are you": "ask_age.wav",
        "medicare part a": "ask_medicare.wav",
        "connect you with": "connect_specialist.wav",
        "thank you": "end_call.wav",
        "sorry, you do not": "end_call.wav",
        "sorry, could you": "ask_age_again.wav" 
    }
    
    while not stop_flag.is_set():
        text = tts_queue.get()
        if text is None: break
        
        try:
            print(f"🤖 Bot Saying: {text}")
            
            # Simple fuzzy match to find filename
            key = text.lower()[:15] 
            filename = None
            for k, v in audio_map.items():
                if k in key or key in k:
                    filename = v
                    break
            
            # Reset silence timer so we don't hangup on ourselves
            call_status["last_speech_time"] = time.time() + 5 
            
            if filename:
                filepath = os.path.join(RECORDINGS_PATH, filename)
                if os.path.exists(filepath):
                    data, fs = sf.read(filepath, dtype='float32')
                    # Play to Loopback Output (Baresip Input)
                    sd.play(data, fs, device=OUTPUT_DEVICE_INDEX)
                    sd.wait()
                else:
                    print(f"⚠️ Missing File: {filename}")
            
        except Exception as e:
            print(f"TTS Error: {e}")

threading.Thread(target=tts_player_worker, daemon=True).start()

# -----------------------------
# 5. Speech Recognition
# -----------------------------
if not os.path.exists(VOSK_MODEL_PATH):
    print("❌ Model not found! Please check VOSK_MODEL_PATH.")
    sys.exit(1)

model = vosk.Model(VOSK_MODEL_PATH)
recognizer = vosk.KaldiRecognizer(model, 16000)

def audio_callback(indata, frames, time, status):
    if call_status["active"]:
        audio_queue.put(bytes(indata))

def recognize_worker():
    while not stop_flag.is_set():
        data = audio_queue.get()
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            
            if text and call_status["active"]:
                print(f"🗣️ Customer: {text}")
                
                # Reset Silence Timer
                call_status["last_speech_time"] = time.time()
                
                # Get Decision from Logic
                action, data = process_response(text)
                
                if action == "SPEAK":
                    tts_queue.put(data)
                elif action == "HANGUP":
                    # Speak goodbye then hangup
                    if data: tts_queue.put(data) 
                    time.sleep(3) 
                    perform_hangup()
                elif action == "TRANSFER":
                    tts_queue.put(data) 
                    time.sleep(4) 
                    perform_transfer()

threading.Thread(target=recognize_worker, daemon=True).start()

# -----------------------------
# Main Loop
# -----------------------------
print(f"🚀 Bot System Live on Device Index {INPUT_DEVICE_INDEX}")

# Open InputStream on the Loopback device
with sd.RawInputStream(samplerate=16000, blocksize=8000, device=INPUT_DEVICE_INDEX, 
                       dtype='int16', channels=1, callback=audio_callback):
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_flag.set()
        baresip_process.terminate()
        print("\nShutdown.")
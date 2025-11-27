import asyncio
import aiofiles
import time
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from word2number import w2n
import re

# -----------------------------
# Configuration
# -----------------------------
# The extension ViciDial uses to send calls to a closer/survey
TRANSFER_EXTENSION = "9000"  

# Initialize Model (Loads automatically on start)
print("Loading FLAN-T5-small...")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print(f"Model ready on {device}")

questions = [
    "Hi, this is Mary from American Benefits. How are you doing today?",
    "Sound's good! May I know how old are you?",
    "Ok! Do you currently have Medicare Part A and B active?",
    "Alright! I’ll connect you with a Medicare specialist. Please hold a moment."
]

conversation_state = {"step": 0, "awaiting_reply": False}

async def log_conversation(role, text):
    """Async logger to save text without blocking audio."""
    try:
        async with aiofiles.open("call_logs.txt", mode='a') as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            await f.write(f"[{timestamp}] {role}: {text}\n")
    except Exception as e:
        print(f"Log Error: {e}")

def analyze_sentiment(question, answer):
    prompt = (
        f"Classify sentiment as Positive, Negative, or Neutral.\n"
        f"Question: {question}\nCustomer: {answer}\nSentiment:"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=10)
    return tokenizer.decode(outputs[0], skip_special_tokens=True).strip()

def process_response(user_text):
    """
    Returns tuple: (ACTION, DATA)
    ACTIONS: 'SPEAK', 'HANGUP', 'TRANSFER'
    """
    step = conversation_state["step"]
    
    # --- Step 0: Initial Greeting ---
    if step == 0 and not conversation_state["awaiting_reply"]:
        conversation_state["awaiting_reply"] = True
        return ("SPEAK", questions[0])
        
    # --- Step 1: Analyze Greeting Reply ---
    if step == 0:
        sentiment = analyze_sentiment(questions[0], user_text)
        print(f"Sentiment: {sentiment}")
        
        if "negative" in sentiment.lower() or "stop" in user_text.lower():
            return ("HANGUP", None)
            
        if "positive" in sentiment.lower() or "neutral" in sentiment.lower():
            conversation_state["step"] = 1
            conversation_state["awaiting_reply"] = False
            return ("SPEAK", questions[1])
        
        # If unsure, just hangup or ask again (Here we hangup to be safe)
        return ("HANGUP", None)

    # --- Step 2: Analyze Age Reply ---
    if step == 1:
        age = None
        age_match = re.search(r'\b(\d{2})\b', user_text)
        if age_match:
            age = int(age_match.group(1))
        else:
            try:
                age = w2n.word_to_num(user_text)
            except:
                pass
        
        # Logic: If age is eligible (40-85) -> Continue. If not -> Hangup.
        if age and 40 <= age <= 85:
            conversation_state["step"] = 2
            return ("SPEAK", questions[2])
        elif age:
            print("Age not eligible.")
            return ("HANGUP", "Sorry, you do not qualify. Have a nice day.")
        else:
            return ("SPEAK", "Sorry, could you please tell me your age again?")

    # --- Step 3: Medicare & Transfer ---
    if step == 2:
        sentiment = analyze_sentiment(questions[2], user_text)
        if "positive" in sentiment.lower() or "yes" in user_text.lower():
            # POSITIVE SCENARIO -> TRANSFER
            conversation_state["step"] = 3
            # We speak the transfer message first, then system triggers transfer
            return ("TRANSFER", questions[3]) 
        
        return ("HANGUP", "Okay, thank you for your time.")

    return ("HANGUP", None)

def reset_state():
    conversation_state["step"] = 0
    conversation_state["awaiting_reply"] = False
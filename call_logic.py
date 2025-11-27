# call_logic.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

print("Loading FLAN-T5-small for Medicare intent/sentiment understanding...")
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
print(f" FLAN-T5-small model ready on {device}")

questions = [
    "Hi, this is Mary from American Benefits. How are you doing today?",
    "sound's good! May I know how old are you?",
    "ok! Do you currently have Medicare Part A and B active?",
    "Alright! I’ll connect you with Medicare specialist. Please hold a moment."
]

conversation_state = {
    "step": 0,
    "awaiting_reply": False,
    # new: 'action' will be None, 'transfer', or 'hangup'
    "action": None
}

def analyze_sentiment(question, answer):
    prompt = (
        f"You are a Medicare agent. Based on the question and customer's answer if answer have things like why you are calling me again and again, dont call me or use any abusive language direct use it negative, "
        f"classify the customer's sentiment as Positive, Negative, or Neutral.\n\n"
        f"Question: {question}\nCustomer: {answer}\n\nSentiment:"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=10)
    sentiment = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    return sentiment

def step_1_greeting():
    conversation_state["step"] = 0
    conversation_state["awaiting_reply"] = True
    conversation_state["action"] = None
    return questions[0]

def step_2_analyze_greeting_reply(user_text):
    sentiment = analyze_sentiment(questions[0], user_text)
    print(f"🧭 Sentiment detected: {sentiment}")

    if "positive" in sentiment.lower():
        conversation_state["step"] = 1
        conversation_state["awaiting_reply"] = False
        return questions[1]
    else:
        return end_call()

def step_3_analyze_age_reply(user_text):
    from word2number import w2n
    import re

    sentiment = analyze_sentiment(questions[1], user_text)
    print(f" Sentiment detected: {sentiment}")

    age = None
    age_match = re.search(r'\b(\d{2})\b', user_text)
    if age_match:
        age = int(age_match.group(1))
        print(f" Detected numeric age: {age}")
    else:
        try:
            age = w2n.word_to_num(user_text)
            print(f" Detected written age: {age}")
        except Exception:
            age = None

    if age is not None:
        if 40 <= age <= 60:
            print(" Age within eligible range (40–60). Continuing...")
            conversation_state["step"] = 2
            conversation_state["awaiting_reply"] = False
            return questions[2]
        else:
            print(" Age outside eligible range. Ending call.")
            return end_call()
    else:
        print("⚠️ Could not detect age. Asking again or ending call.")
        return "Sorry, could you please tell me your age again?"

def step_4_analyze_medicare_reply(user_text):
    sentiment = analyze_sentiment(questions[2], user_text)
    print(f" Sentiment detected: {sentiment}")

    # if positive we want to transfer to agent
    if "positive" in sentiment.lower():
        conversation_state["step"] = 3
        conversation_state["awaiting_reply"] = False
        # important: set action to transfer so the audio/control layer will send a transfer to Vicidial
        conversation_state["action"] = "transfer"
        return questions[3]
    else:
        return end_call()

def end_call():
    conversation_state["step"] = 0
    conversation_state["awaiting_reply"] = False
    # mark that the call should be hung up
    conversation_state["action"] = "hangup"
    return "Thank you for your time. Have a great day!"

def process_response(user_text):
    """
    This function controls conversation flow.
    fullvoice.py sends recognized text here.
    """
    step = conversation_state["step"]
    awaiting = conversation_state["awaiting_reply"]

    if step == 0 and not awaiting:
        return step_1_greeting()
    elif step == 0 and awaiting:
        return step_2_analyze_greeting_reply(user_text)
    elif step == 1:
        return step_3_analyze_age_reply(user_text)
    elif step == 2:
        return step_4_analyze_medicare_reply(user_text)
    else:
        return end_call()

def get_and_clear_action():
    """Called by the audio layer to fetch the next call action (transfer/hangup) if any.
       Returns action string or None. Clears the action after read.
    """
    act = conversation_state.get("action")
    conversation_state["action"] = None
    return act

def reset_conversation():
    conversation_state["step"] = 0
    conversation_state["awaiting_reply"] = False
    conversation_state["action"] = None
    return step_1_greeting()

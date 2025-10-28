# # # # from word2number import w2n

# # # # def get_age_from_text(text):
# # # #     """Extract numeric or word-based ages from text"""
# # # #     text = text.lower()
# # # #     try:
# # # #         for word in text.split():
# # # #             if word.isdigit():
# # # #                 return int(word)
# # # #         return w2n.word_to_num(text)
# # # #     except Exception:
# # # #         return None


# # # # def process_response(user_input):
# # # #     """
# # # #     This function defines the dialogue logic for the call.
# # # #     You can modify or add new conversational rules here easily.
# # # #     """
# # # #     user_input = user_input.lower()

# # # #     # -----------------------------
# # # #     # Greeting Phase
# # # #     # -----------------------------
# # # #     if "hi" in user_input or "hello" in user_input:
# # # #         return "Hi, this is Mary from American Benefits. How are you doing today?"

# # # #     # -----------------------------
# # # #     # Mood Response Phase
# # # #     # -----------------------------
# # # #     if any(word in user_input for word in ["fine", "good", "okay"]):
# # # #         return "That sounds good! May I know how young you are?"
# # # #     elif any(word in user_input for word in ["not well", "bad", "sick"]):
# # # #         return "Sad to hear that. I hope you feel better soon. May I know your age?"

# # # #     # -----------------------------
# # # #     # Age Detection Phase
# # # #     # -----------------------------
# # # #     age = get_age_from_text(user_input)
# # # #     if age:
# # # #         print(f"🧩 Detected Age: {age}")
# # # #         if 40 <= age <= 60:
# # # #             return "Do you have Medicare Part A and B active?"
# # # #         else:
# # # #             return "Thank you for your time. Have a nice day!"

# # # #     # -----------------------------
# # # #     # Medicare Question Phase
# # # #     # -----------------------------
# # # #     if "yes" in user_input and ("part a" in user_input or "part b" in user_input):
# # # #         return "Alright, I'm transferring your call to my senior supervisor."
# # # #     elif "no" in user_input and ("part a" in user_input or "part b" in user_input):
# # # #         return "Okay, thank you for your time. Have a nice day!"

# # # #     # -----------------------------
# # # #     # Default Catch-All
# # # #     # -----------------------------
# # # #     # return "Could you please tell me how old you are?"

# # # from word2number import w2n
# # # from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# # # # -----------------------------
# # # # Initialize the T5 model
# # # # -----------------------------
# # # print("🔍 Loading T5-small for Medicare sentiment analysis...")
# # # tokenizer = AutoTokenizer.from_pretrained("t5-small")
# # # model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")
# # # print("✅ T5-small model loaded successfully!")

# # # # -----------------------------
# # # # Helper Functions
# # # # -----------------------------
# # # def judge_response_with_t5(question, customer_reply):
# # #     """
# # #     Use T5-small to determine if the customer's reply is positive, negative, or neutral.
# # #     The context is that the agent is a Medicare representative.
# # #     """
# # #     try:
# # #         prompt = (
# # #             f"You are a Medicare agent analyzing a phone call.\n"
# # #             f"Agent asked: '{question}'\n"
# # #             f"Customer replied: '{customer_reply}'\n"
# # #             f"Based on the reply, respond with only one word: positive, negative, or neutral."
# # #         )
# # #         inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
# # #         outputs = model.generate(**inputs, max_length=10)
# # #         result = tokenizer.decode(outputs[0], skip_special_tokens=True).strip().lower()
# # #         if "positive" in result:
# # #             return "positive"
# # #         elif "negative" in result:
# # #             return "negative"
# # #         else:
# # #             return "neutral"
# # #     except Exception as e:
# # #         print(f"⚠️ AI judgment error: {e}")
# # #         return "neutral"


# # # def get_age_from_text(text):
# # #     """Extract numeric or word-based ages from text"""
# # #     text = text.lower()
# # #     try:
# # #         for word in text.split():
# # #             if word.isdigit():
# # #                 return int(word)
# # #         return w2n.word_to_num(text)
# # #     except Exception:
# # #         return None


# # # def process_response(user_input, last_question=None):
# # #     """
# # #     Main dialog logic for the Medicare call.
# # #     The T5 model judges whether the customer response is positive or negative.
# # #     """
# # #     user_input = user_input.lower()

# # #     # -----------------------------
# # #     # Step 1: If there's a last question, judge user's sentiment
# # #     # -----------------------------
# # #     sentiment = "neutral"
# # #     if last_question:
# # #         sentiment = judge_response_with_t5(last_question, user_input)
# # #         print(f"🧠 Sentiment detected by AI: {sentiment}")

# # #     # -----------------------------
# # #     # Step 2: Standard call logic
# # #     # -----------------------------
# # #     if "hi" in user_input or "hello" in user_input:
# # #         return "Hi, this is Mary from American Benefits. How are you doing today?", "greeting"

# # #     if any(word in user_input for word in ["fine", "good", "okay"]):
# # #         if sentiment == "positive":
# # #             return "That sounds good! May I know how young you are?", "ask_age"
# # #         else:
# # #             return "I'm glad to hear that. Could you please tell me your age?", "ask_age"

# # #     elif any(word in user_input for word in ["not well", "bad", "sick"]):
# # #         return "I'm sorry to hear that. I hope you feel better soon. May I know your age?", "ask_age"

# # #     age = get_age_from_text(user_input)
# # #     if age:
# # #         print(f"🧩 Detected Age: {age}")
# # #         if 40 <= age <= 60:
# # #             return "Do you have Medicare Part A and B active?", "medicare_question"
# # #         else:
# # #             return "Thank you for your time. Have a nice day!", "end"

# # #     if "yes" in user_input and ("part a" in user_input or "part b" in user_input):
# # #         if sentiment == "positive":
# # #             return "Alright, I'm transferring your call to my senior supervisor.", "transfer"
# # #         else:
# # #             return "Okay, could you confirm again if both parts are active?", "confirmation"

# # #     elif "no" in user_input and ("part a" in user_input or "part b" in user_input):
# # #         if sentiment == "negative":
# # #             return "Okay, thank you for your time. Have a nice day!", "end"
# # #         else:
# # #             return "Alright, no problem. Have a great day!", "end"

# # #     return "Could you please tell me how old you are?", "ask_age"


# # from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
# # import torch

# # # ------------------------------------------------
# # # Load FLAN-T5 model for intent/sentiment analysis
# # # ------------------------------------------------
# # print("🔍 Loading FLAN-T5-small for Medicare intent/sentiment understanding...")
# # tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
# # model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
# # device = "cuda" if torch.cuda.is_available() else "cpu"
# # model.to(device)
# # print(f"✅ FLAN-T5-small model ready on {device}")

# # # ------------------------------------------------
# # # Medicare Question Flow
# # # ------------------------------------------------
# # questions = [
# #     "Hi, this is Mary from American Benefits. How are you doing today?",
# #     "Great! I’m calling to help you review your Medicare benefits. Do you currently have Medicare Part A and B active?",
# #     "Perfect. Are you paying any premiums for supplemental coverage?",
# #     "Got it. Are you interested in exploring plans that might lower your out-of-pocket costs?",
# #     "Alright! I’ll connect you with a licensed Medicare specialist who can go over your options. Please hold a moment."
# # ]

# # # State tracking
# # conversation_state = {"step": 0}


# # # ------------------------------------------------
# # # Analyze sentiment using FLAN-T5
# # # ------------------------------------------------
# # def analyze_sentiment(question, answer):
# #     prompt = (
# #         f"You are a Medicare agent. Based on the question and customer's answer, "
# #         f"classify the customer's sentiment as Positive, Negative, or Neutral.\n\n"
# #         f"Question: {question}\n"
# #         f"Customer: {answer}\n\n"
# #         f"Sentiment:"
# #     )

# #     inputs = tokenizer(prompt, return_tensors="pt").to(device)
# #     outputs = model.generate(**inputs, max_new_tokens=10)
# #     sentiment = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
# #     return sentiment


# # # ------------------------------------------------
# # # Process each customer response and pick next question
# # # ------------------------------------------------
# # def process_response(user_text):
# #     global conversation_state
# #     step = conversation_state["step"]

# #     # Current question asked
# #     current_question = questions[step] if step < len(questions) else None
# #     if not current_question:
# #         return "Thank you for your time. Goodbye!"

# #     # Analyze using FLAN-T5
# #     sentiment = analyze_sentiment(current_question, user_text)
# #     print(f"🧭 Sentiment detected: {sentiment}")

# #     # Logic for progression
# #     if "positive" in sentiment.lower():
# #         step += 1
# #         if step < len(questions):
# #             conversation_state["step"] = step
# #             next_question = questions[step]
# #             print(f"➡️ Moving to question {step+1}")
# #             return next_question
# #         else:
# #             return "Thank you for confirming! I’ll connect you with a licensed specialist now."
# #     elif "negative" in sentiment.lower():
# #         return "No worries. I understand. Thank you for your time!"
# #     else:
# #         return "Could you please repeat that? I just want to make sure I understood correctly."


# # # ------------------------------------------------
# # # Reset conversation when needed
# # # ------------------------------------------------
# # def reset_conversation():
# #     global conversation_state
# #     conversation_state["step"] = 0
# #     return "Hi, this is Mary from American Benefits. How are you doing today?"


# import torch
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# # ============================================================
# # Load FLAN-T5 model locally
# # ============================================================
# print("🔍 Loading FLAN-T5-small model for Medicare conversation logic...")
# tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
# model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = model.to(device)
# print(f"✅ FLAN-T5-small model loaded successfully on {device}")

# # ============================================================
# # AI Sentiment Classifier
# # ============================================================
# def analyze_sentiment(text):
#     """Judge the customer response as positive or negative using local FLAN-T5."""
#     prompt = f"Classify this customer response as positive or negative: {text}"
#     inputs = tokenizer(prompt, return_tensors="pt").to(device)
#     outputs = model.generate(**inputs, max_new_tokens=5)
#     sentiment = tokenizer.decode(outputs[0], skip_special_tokens=True).lower()

#     if "positive" in sentiment:
#         return "positive"
#     elif "negative" in sentiment:
#         return "negative"
#     else:
#         return "neutral"

# # ============================================================
# # Step Functions
# # ============================================================
# def step_greeting():
#     """Bot greets first (no user trigger required)."""
#     question = "Hi, this is Mary from American Benefits. How are you doing today?"
#     return question, "greeting"

# def step_ask_age(user_text):
#     """Handle customer's reply after greeting."""
#     sentiment = analyze_sentiment(user_text)
#     print(f"🧠 Sentiment after greeting: {sentiment}")
#     if sentiment == "positive":
#         return step_ask_medicare_age()
#     else:
#         return step_end_call()

# def step_ask_medicare_age():
#     """Ask for customer's age."""
#     question = "May I know how young you are?"
#     return question, "ask_age"

# def step_check_medicare(user_text):
#     """Handle reply to age question."""
#     sentiment = analyze_sentiment(user_text)
#     print(f"🧠 Sentiment after age question: {sentiment}")
#     if sentiment == "positive":
#         return step_ask_medicare_status()
#     else:
#         return step_end_call()

# def step_ask_medicare_status():
#     """Ask if the customer has Medicare Part A and B."""
#     question = "Do you currently have Medicare Part A and B active?"
#     return question, "ask_medicare"

# def step_transfer_or_end(user_text):
#     """Handle reply to Medicare question."""
#     sentiment = analyze_sentiment(user_text)
#     print(f"🧠 Sentiment after Medicare question: {sentiment}")
#     if sentiment == "positive":
#         return step_transfer_call()
#     else:
#         return step_end_call()

# def step_transfer_call():
#     """Transfer the call to senior agent."""
#     question = "Perfect! Let me transfer your call to a licensed agent for more details."
#     return question, "transfer_call"

# def step_end_call():
#     """End the conversation gracefully."""
#     goodbye = "I understand. Have a nice day!"
#     print(f"🤖 Bot: {goodbye}")
#     return goodbye, "end_call"

# # ============================================================
# # Main Control Function (called by fullvoice.py)
# # ============================================================
# def process_response(user_text, last_question=None):
#     """
#     Keeps compatibility with fullvoice.py
#     Automatically advances to next steps if sentiment is positive.
#     """
#     try:
#         # Step 1 — Greeting (bot starts automatically)
#         if not last_question:
#             return step_greeting()

#         # Step 2 — After greeting
#         elif last_question == "greeting":
#             return step_ask_age(user_text)

#         # Step 3 — After asking age
#         elif last_question == "ask_age":
#             return step_check_medicare(user_text)

#         # Step 4 — After asking Medicare status
#         elif last_question == "ask_medicare":
#             return step_transfer_or_end(user_text)

#         # Step 5 — Anything else
#         else:
#             return step_end_call()

#     except Exception as e:
#         print(f"⚠️ Error in call logic: {e}")
#         return "Something went wrong. Let's end the call. Have a great day!", "end_call"





from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch


# Load T5 model

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
    "awaiting_reply": False  
}


def analyze_sentiment(question, answer):
    prompt = (
        f"You are a Medicare agent. Based on the question and customer's answer if answer have things like why you are calling me again and again, dont call me or use any abusive language direct use it negative  , "
        f"classify the customer's sentiment as Positive, Negative, or Neutral.\n\n"
        f"Question: {question}\nCustomer: {answer}\n\nSentiment:"
    )
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=10)
    sentiment = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
    return sentiment


def step_1_greeting():
    """Mary starts the conversation automatically."""
    conversation_state["step"] = 0
    conversation_state["awaiting_reply"] = True
    return questions[0]



def step_2_analyze_greeting_reply(user_text):
    """Analyze response to greeting."""
    sentiment = analyze_sentiment(questions[0], user_text)
    print(f"🧭 Sentiment detected: {sentiment}")

    if "positive" in sentiment.lower():
        conversation_state["step"] = 1
        conversation_state["awaiting_reply"] = False
        return questions[1]
    else:
        return end_call()



def step_3_analyze_age_reply(user_text):
    """Analyze response to age question and check eligibility based on age."""
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

    
    if "positive" in sentiment.lower():
        conversation_state["step"] = 2
        conversation_state["awaiting_reply"] = False
        return questions[2]
    else:
        return end_call()


def step_4_analyze_medicare_reply(user_text):
    """Analyze response to Medicare question."""
    sentiment = analyze_sentiment(questions[2], user_text)
    print(f" Sentiment detected: {sentiment}")

    if "positive" in sentiment.lower():
        conversation_state["step"] = 3
        conversation_state["awaiting_reply"] = False
        return questions[3]
    else:
        return end_call()


def end_call():
    """End call gracefully."""
    conversation_state["step"] = 0
    conversation_state["awaiting_reply"] = False
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



def reset_conversation():
    conversation_state["step"] = 0
    conversation_state["awaiting_reply"] = False
    return step_1_greeting()

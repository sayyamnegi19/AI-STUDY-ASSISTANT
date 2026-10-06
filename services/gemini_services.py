import google.generativeai as genai
import os
import markdown
import bleach
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ai_model = os.getenv("AI_MODEL")
chat_model_name = os.getenv("CHAT_MODEL", "gemini-flash-lite-latest")
model = genai.GenerativeModel(ai_model)
#Fast model for interactive features (ask doubts, quiz)
chat_model = genai.GenerativeModel(chat_model_name)

def clean_content(content):
    clean_formatted_response = bleach.clean(
        content,
        tags=[
            "p", "strong", "em", "ul", "ol", "li",
            "h1", "h2", "h3", "h4",
            "code", "pre", "blockquote", "br"
        ],
        attributes={
            "a" : ["href","title"]
        },
        strip=True
    )
    return clean_formatted_response

def generate_study_notes(topic):
    prompt = f"""
        Create structured study notes on the topic: {topic}

        Format:
        -Clear Headings
        -Bullet Points
        -Important  Definitions
        -Examples
        -Summary at the end
    """

    response = model.generate_content(prompt)
    return response.text

MAX_CONTEXT_TURNS = 6

def answer_doubt(question, history=None):
    history = history or []

    contents = []

    #Previous turns of the current chat only (old chats are never kept)
    for chat in history[-MAX_CONTEXT_TURNS:]:
        contents.append({
            "role": "user",
            "parts": [chat["question"]]
        })
        contents.append({
            "role": "model",
            "parts": [chat["raw_answer"]]
        })

    prompt = f"""
    You are a helpful AI tutor.

    Answer the following student question clearly and simply.

    Rules:
    - Use simple explanations
    - Use bullet points if needed
    - Avoid unnecessary symbols
    - Be concise but informative

    Question:
    {question}
    """
    contents.append({
        "role": "user",
        "parts": [prompt]
    })

    response = chat_model.generate_content(contents)

    return response.text

def generate_notes_from_pdf(text):
    prompt = f"""
    Convert the following study material into clean structured study notes.

    Rules:
    - Use clear headings
    - Use bullet points
    - Keep explanations concise
    - Remove unnecessary content
    - Format like exam revision notes

    Study Material:
    {text[:12000]} 
    """

    response = model.generate_content(prompt)
    raw_text = response.text if response.text else ""
    clean_response = clean_content(raw_text)

    return clean_response

def generate_quiz(topic):

    prompt = f"""
    Generate 5 multiple choice questions about: {topic}

    Rules:
    - Each question must have 4 options
    - Mark the correct answer clearly
    - Keep questions short and exam style
    - Format as JSON like this:

    [
      {{
        "question": "Question text",
        "options": ["A", "B", "C", "D"],
        "answer": "Correct option text"
      }}
    ]

    Return only valid JSON.
    """

    response = chat_model.generate_content(
        prompt,
        generation_config={
            "response_mime_type": "application/json"
        }
    )

    raw_text = response.candidates[0].content.parts[0].text

    return raw_text
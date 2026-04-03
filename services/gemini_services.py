import google.generativeai as genai
import os
import markdown
import bleach
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ai_model = os.getenv("AI_MODEL")
model = genai.GenerativeModel(ai_model)

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

def answer_doubt(question):
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
    response = model.generate_content(prompt)
    # markdown_response = markdown.markdown(
    #     response.text,
    #     extensions=["codehilite","extra","fenced_code"]
    # )
    # cleaned_response = clean_content(markdown_response)

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

    response = model.generate_content(
        prompt,
        generation_config={
            "response_mime_type": "application/json"
        }
    )

    raw_text = response.candidates[0].content.parts[0].text

    return raw_text
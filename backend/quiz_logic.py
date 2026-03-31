import json
import re
import PyPDF2
import google.generativeai as generativeai

from utils import get_api_key
from decision_tree import AdaptiveDecisionTree

generativeai.configure(api_key=get_api_key())

MODEL_NAME = "gemini-2.5-flash"

tree = AdaptiveDecisionTree()


def get_next_difficulty(score, correct_streak, wrong_streak, attention):
    state = {
        "score": score,
        "correct_streak": correct_streak,
        "wrong_streak": wrong_streak,
        "attention": attention
    }
    return tree.evaluate(state)


def generate_quiz_prompt(pdf_text: str, num_questions: int, difficulty: str) -> str:
    prompt = f"""
Create a {difficulty} level quiz with {num_questions} multiple-choice questions based on the following PDF content.

PDF content:
\"\"\"
{pdf_text[:12000]}
\"\"\"

Rules:
1. Return exactly {num_questions} questions.
2. Each question must have:
   - "text"
   - "options" (exactly 4 options)
   - "correctAnswer" (must be only one uppercase letter: A, B, C, or D)
3. Questions should match the requested difficulty:
   - easy: direct recall, definitions, simple facts
   - medium: understanding and interpretation
   - hard: deeper reasoning, comparison, and trickier concept-based questions
4. Do not include explanations.
5. Return ONLY valid JSON.
6. Do not wrap the JSON in markdown fences.

Return JSON in this exact format:
[
  {{
    "text": "Question here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": "B"
  }}
]
"""
    return prompt


def generate_quiz(pdf_text: str, num_questions: int, difficulty: str):
    try:
        model = generativeai.GenerativeModel(MODEL_NAME)
        prompt = generate_quiz_prompt(pdf_text, num_questions, difficulty)
        response = model.generate_content([prompt])

        quiz_json = response.text.strip() if response.text else ""
        if not quiz_json:
            return None, "Error: Gemini returned an empty response."

        if quiz_json.startswith('\ufeff'):
            quiz_json = quiz_json[1:]

        print(f"Raw Gemini Response (repr): {repr(quiz_json)}")

        quiz_json = re.sub(r"```json\s*|```", "", quiz_json).strip()
        quiz_json = quiz_json.replace("\n", "")

        print(f"Cleaned JSON (repr): {repr(quiz_json)}")

        try:
            quiz_data = json.loads(quiz_json)
            print(f"Parsed JSON Data: {quiz_data}")

            if not isinstance(quiz_data, list):
                return None, "Invalid JSON: response must be a list of questions."

            for question in quiz_data:
                if not all(key in question for key in ("text", "options", "correctAnswer")):
                    return None, "Invalid JSON: each question must contain 'text', 'options', and 'correctAnswer'."

                if not isinstance(question["options"], list) or len(question["options"]) != 4:
                    return None, "Invalid JSON: 'options' must be a list of 4 items."

                if question["correctAnswer"] not in {"A", "B", "C", "D"}:
                    return None, "Invalid JSON: 'correctAnswer' must be one of A, B, C, or D."

            return {"questions": quiz_data, "difficulty": difficulty}, None

        except json.JSONDecodeError as e:
            return None, f"JSON decode error: {e}. Raw JSON: {repr(quiz_json)}"

    except Exception as e:
        return None, f"Error generating quiz: {e}"


def get_pdf_data(filepath):
    try:
        pdf_text = ""
        with open(filepath, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    pdf_text += extracted + "\n"
        return pdf_text
    except Exception as e:
        print(f"Error in get_pdf_data: {e}")
        return None
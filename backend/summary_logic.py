from flask import request, jsonify
import os
import sys
import pathlib
import google.generativeai as generativeai
from utils import get_api_key  
import PyPDF2  
import json

generativeai.configure(api_key=get_api_key())

def answer_prompt(pdf_text: str, user_prompt: str) -> str:  # Changed to accept text
    try:
        model = generativeai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content([user_prompt, pdf_text])  # Send text directly
        return response.text
    except Exception as e:
        print(f"Error in answer_prompt: {e}")
        return "Error generating answer."

def process_pdf_data(filepath):
    try:
        pdf_text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                pdf_text += page.extract_text()
        return pdf_text  # Return the extracted text
    except Exception as e:
        print(f"Error in process_pdf_data: {e}")
        return None

def get_pdf_data(filepath):  # New function to get the processed data
    try:
        pdf_text = ""
        with open(filepath, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                pdf_text += page.extract_text()
        return pdf_text  # Return the extracted text
    except Exception as e:
        print(f"Error in get_pdf_data: {e}")
        return None

def ask_question():
    data = request.get_json()
    question = data.get('question')
    pdf_data = data.get('pdf_data')  # This will now be the extracted text

    if question and pdf_data:
        answer = answer_prompt(pdf_data, question)  # Pass the text to answer_prompt
        return jsonify({'answer': answer})
    else:
        return jsonify({'error': 'Invalid request'}), 400



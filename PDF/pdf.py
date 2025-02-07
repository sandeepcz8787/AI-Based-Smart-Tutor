import os
import fitz  # PyMuPDF
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import google.generativeai as genai

# Configure the Gemini API with your API key
genai.configure(api_key="AIzaSyDzBP8WLUPtJBLycs7_On5sANxueMkTcUE")

# Initialize Flask app
app = Flask(__name__)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text

def summarize_text_with_gemini(text):

    generation_config = {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_output_tokens": 500,  
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",  
        generation_config=generation_config,
    )

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(f"Explain the following text in short with details explanation in points:\n\n{text}")

    return response.text.strip()

@app.route('/')
def index():
    return render_template('pdf.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join("uploads", filename)
        file.save(filepath)
        
        pdf_text = extract_text_from_pdf(filepath)
        summary = summarize_text_with_gemini(pdf_text)
        
        return jsonify({"summary": summary})
    else:
        return jsonify({"error": "Invalid file format. Only PDFs are allowed."})

if __name__ == "__main__":
    app.run(debug=True)

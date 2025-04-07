from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import os
from flask_cors import CORS
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__, template_folder='templates')

CORS(app)
app.secret_key = 'your_secret_key'

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UPLOAD_FOLDER = 'temp_uploads'
EDITS_FOLDER = 'temp_edits'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EDITS_FOLDER'] = EDITS_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    earliest_year = 1887
    current_year = 2025
    years = list(range(earliest_year, current_year + 1))
    return render_template('home.html', years=years, documents=[])

@app.route('/history')
def history():
    viewed_docs_ids = session.get('viewed_documents', [])
    viewed_documents = []  # Fetch from client-side if needed
    return render_template('history.html', documents=viewed_documents)

@app.route('/clear_history')
def clear_history():
    session.pop('viewed_documents', None)
    return redirect(url_for('history'))

@app.route('/remove_from_history/<int:doc_id>')
def remove_from_history(doc_id):
    if 'viewed_documents' in session:
        session['viewed_documents'] = [id for id in session['viewed_documents'] if id != doc_id]
        session.modified = True
    return redirect(url_for('history'))

@app.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            text = pytesseract.image_to_string(Image.open(filepath))
            os.remove(filepath)  # Optional: Clean up temp file

            return render_template('OCRresults.html', ocr_text=text, image_filename=filename)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/save_ocr_content', methods=['POST'])
def save_ocr_content():
    data = request.get_json()
    image_filename = data['image_filename']
    updated_ocr_text = data['ocr_text']

    try:
        ocr_file_path = os.path.join(app.config['EDITS_FOLDER'], image_filename + '.txt')
        with open(ocr_file_path, 'w', encoding='utf-8') as file:
            file.write(updated_ocr_text)
        return jsonify({"message": "OCR content saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/upload_pdf', methods=['GET', 'POST'])
def upload_pdf():
    return render_template("upload_pdf.html")
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(EDITS_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)

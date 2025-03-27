from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from flask_cors import CORS
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
from flask import send_from_directory
from datetime import datetime
from flask import send_file
import json
import firebase_admin
from firebase_admin import credentials, firestore, storage
import base64


app = Flask(__name__, template_folder='templates')

CORS(app)  # Enable Cross-Origin Resource Sharing if needed
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialize Firebase Admin SDK
firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS")
if firebase_cred_path:
    cred = credentials.Certificate(firebase_cred_path)
    firebase_admin.initialize_app(cred)
else:
    raise ValueError("Firebase credentials not found. Set FIREBASE_CREDENTIALS environment variable.")

# Initialize Firestore
db = firestore.client()

# Initialize Firebase Storage
bucket = storage.bucket()


# Configure upload folder and allowed extensions
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
    current_year = 2025  # Updated to the current year
    years = list(range(earliest_year, current_year + 1))
    return render_template('home.html', years=years, documents=documents)

@app.route('/history')
def history():
    # Retrieve viewed document IDs from session
    viewed_docs_ids = session.get('viewed_documents', [])
    viewed_documents = [doc for doc in documents if doc["id"] in viewed_docs_ids]
    return render_template('history.html', documents=viewed_documents)

@app.route('/clear_history')
def clear_history():
    # Clear all viewed documents from session
    session.pop('viewed_documents', None)
    return redirect(url_for('history'))

@app.route('/remove_from_history/<int:doc_id>')
def remove_from_history(doc_id):
    # Remove a specific document ID from the history
    if 'viewed_documents' in session:
        session['viewed_documents'] = [id for id in session['viewed_documents'] if id != doc_id]
        session.modified = True
    return redirect(url_for('history'))

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip().lower()
    year = request.args.get('year', 'none')
    doc_type = request.args.get('doc_type', 'none').strip().lower()

    docs_ref = db.collection('documents')
    results = []

    # Get all documents from Firestore
    docs = docs_ref.stream()

    for doc in docs:
        doc_data = doc.to_dict()
        if (query in doc_data["title"].lower() or query in doc_data["content"].lower() or
            any(query in actor.lower() for actor in doc_data["actors"])):
            if (year == 'none' or str(doc_data["year"]) == year) and (doc_type == 'none' or doc_data["type"].lower() == doc_type):
                results.append(doc_data)

    return render_template('results.html', results=results)


@app.route('/document/<int:doc_id>')
def view_document(doc_id):
    # Find the document by its ID
    doc = next((doc for doc in documents if doc["id"] == doc_id), None)
    if not doc:
        return "Document not found", 404

    # Add the document ID to the session's view history
    if 'viewed_documents' not in session:
        session['viewed_documents'] = []
    if doc_id not in session['viewed_documents']:
        session['viewed_documents'].append(doc_id)
        session.modified = True

    # Read the file content
    try:
        with open(doc["file_path"], "r", encoding="utf-8") as file:
            file_content = file.read()
    except FileNotFoundError:
        file_content = "The requested file could not be found."

    # Pass the content to the template
    return render_template('document.html', document=doc, content=file_content)

@app.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html')

def add_documents(documents):
        for doc in documents:
            db.collection('documents').add(doc)
        add_documents(documents)

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
            with open(filepath, "rb") as img_file:
                image_data = img_file.read()

            os.remove(filepath)  # Clean up the temporary file

            # Save OCR results in Firestore
            doc_ref = db.collection("ocr_results").add({
                "image_filename": filename,
                "ocr_text": text,
                "image_data": image_data,
                "timestamp": datetime.utcnow()
            })

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
        # Define the path where OCR results will be saved
        ocr_file_path = os.path.join(app.config['EDITS_FOLDER'], image_filename + '.txt')

        # Save the updated OCR text to a file
        with open(ocr_file_path, 'w', encoding='utf-8') as file:
            file.write(updated_ocr_text)

        return jsonify({"message": "OCR content saved successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    # Ensure the Flask app runs on the specified port
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)

@app.route('/retrieve_image/<doc_id>', methods=['GET'])
def retrieve_image(doc_id):
    try:
        doc = db.collection("ocr_results").document(doc_id).get()
        if doc.exists:
            doc_data = doc.to_dict()
            image_filename = doc_data.get("image_filename", "retrieved_image.png")
            image_data = base64.b64decode(doc_data.get("image_data", ""))

            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            with open(image_path, "wb") as image_file:
                image_file.write(image_data)

            return send_file(image_path, mimetype='image/png')
        else:
            return jsonify({'error': 'Document not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
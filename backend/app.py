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


app = Flask(__name__, template_folder='templates')

CORS(app)  # Enable Cross-Origin Resource Sharing if needed
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'temp_uploads'
EDITS_FOLDER = 'temp_edits'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['EDITS_FOLDER'] = EDITS_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# In-memory "database" of documents (template)
documents = [
    {
        "id": 0,  # Unique identifier
        "title": "Zoolander Script",
        "actors": ["Ben Stiller", "Owen Wilson"],
        "year": 2001,
        "type": "script",
        "content": "The Zoolander script content goes here.",
        "file_path": "static/zoolander_script.txt"
    },
    {
        "id": 1,
        "title": "Zoolander 2 Script",
        "actors": ["Ben Stiller", "Owen Wilson", "Will Ferrell"],
        "year": 2016,
        "type": "script",
        "content": "The Zoolander 2 script content goes here.",
        "file_path": "static/zoolander2_script.txt"
    },
    {
        "id": 2,
        "title": "Ice Age Production Notes",
        "actors": ["Ray Romano", "John Leguizamo", "Denis Leary"],
        "year": 2002,
        "type": "production_notes",
        "content": "Ice Age Production notes content goes here.",
        "file_path": "static/iceage_prodnotes.txt"
    },
    {
        "id": 3,
        "title": "Citizen Kane Copyright Registration",
        "actors": ["Orson Welles"],
        "year": 1941,
        "type": "copyright_registration",
        "content": "Citizen Kane copyright registration details.",
        "file_path": "static/citizen_kane_copyright.txt"
    },
    {
        "id": 4,
        "title": "The Godfather Renewal",
        "actors": ["Marlon Brando", "Al Pacino"],
        "year": 1992,
        "type": "renewal",
        "content": "The Godfather copyright renewal details.",
        "file_path": "static/the_godfather_renewal.txt"
    },
    {
        "id": 5,
        "title": "Gone with the Wind Film Metadata",
        "actors": ["Clark Gable", "Vivien Leigh"],
        "year": 1939,
        "type": "film_metadata",
        "content": "Metadata about Gone with the Wind.",
        "file_path": "static/gone_with_the_wind_metadata.txt"
    },
    {
        "id": 6,
        "title": "Pulp Fiction Transcript",
        "actors": ["John Travolta", "Uma Thurman", "Samuel L. Jackson"],
        "year": 1994,
        "type": "transcript",
        "content": "Transcript of Pulp Fiction.",
        "file_path": "static/pulp_fiction_transcript.txt"
    }
]

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
    
    # Filter documents based on search criteria
    results = []
    for doc in documents:
        # Check query match for title, content, or actors
        query_match = (
            query in doc["title"].lower() or
            query in doc["content"].lower() or
            any(query in actor.lower() for actor in doc["actors"])
        )
        # Check year and document type
        year_match = year == 'none' or str(doc["year"]) == year
        type_match = doc_type == 'none' or doc_type == doc["type"].lower()
        
        # Add to results if all conditions are met
        if query_match and year_match and type_match:
            results.append(doc)
    
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
            os.remove(filepath)  # Clean up the temporary file

            output_file = os.path.join(app.config['UPLOAD_FOLDER'], filename + ".txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
                
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
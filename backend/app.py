from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash
import os
from flask_cors import CORS
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
from datetime import datetime
from pdf2image import convert_from_path
import tempfile

app = Flask(__name__, template_folder='templates')

CORS(app)
app.secret_key = 'your_secret_key'

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # Adjust this path as needed
poppler_path = r"C:\Users\shtgu\Documents\CodingPackages\poppler-24.08.0\Library\bin" # Adjust this path as needed

UPLOAD_FOLDER = 'backend/static/img'
EDITS_FOLDER = 'backend/static/edits'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
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
    uploaded_files = request.files.getlist('file')

    if not uploaded_files or all(f.filename == '' for f in uploaded_files):
        flash('No files selected')
        return redirect(url_for('upload_page'))

    all_texts = []
    image_filenames = []

    for file in uploaded_files:
        filename = secure_filename(file.filename)
        if filename == '':
            continue

        ext = os.path.splitext(filename)[1].lower()

        if ext == '.pdf':
            tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
            os.close(tmp_fd)  # Close the open file descriptor
            file.save(tmp_path)  # Save uploaded PDF to that path
            try:
                images = convert_from_path(tmp_path, poppler_path=poppler_path)  # Only needed if Poppler isn't in PATH
                if len(images) > 1:
                    images.pop()

                for i, image in enumerate(images):
                    image_filename = f'{os.path.splitext(filename)[0]}_page_{i+1}.jpg'
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
                    image.save(image_path)
                    text = pytesseract.image_to_string(image)
                    all_texts.append((image_filename, text))
                    image_filenames.append(image_filename)

            except Exception as e:
                flash(f'Failed to process PDF: {str(e)}')
                return redirect(url_for('upload_page'))

            finally:
                os.remove(tmp_path)  # Clean up temp PDF file

        elif allowed_file(filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                text = pytesseract.image_to_string(Image.open(filepath))
                all_texts.append((filename, text))
                image_filenames.append(filename)
            except Exception as e:
                flash(f'Failed to process image {filename}: {str(e)}')
            finally:
                os.remove(filepath)

        else:
            flash(f'Unsupported file type: {filename}')

    if not all_texts:
        flash('No valid files processed.')
        return redirect(url_for('upload_page'))

    return render_template('OCRresults.html', results=all_texts)

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
@app.route('/results', methods=['GET', 'POST'])
def results():
    query = request.args.get('query', '')
    year = request.args.get('year', '')

    # TODO: Replace this with real data loading (e.g., from Firestore or JSON)
    all_documents = [
        {'id': 1, 'title': 'Sunset Boulevard', 'year': 1950, 'type': 'feature_film', 'actors': ['Gloria Swanson']},
        {'id': 2, 'title': 'The Kid', 'year': 1921, 'type': 'short_film', 'actors': ['Charlie Chaplin']}
    ]

    # Filter documents based on query and year
    results = []
    for doc in all_documents:
        if (not query or query.lower() in doc['title'].lower()) and (not year or str(doc['year']) == year):
            results.append(doc)

    return render_template('results.html', results=results)
@app.route('/view_document/<int:doc_id>')
def view_document(doc_id):
    # Using the same dummy data source as your /results route
    all_documents = [
        {'id': 1, 'title': 'Sunset Boulevard', 'year': 1950, 'type': 'feature_film', 'actors': ['Gloria Swanson'], 'content': 'This is an example content.'},
        {'id': 2, 'title': 'The Kid', 'year': 1921, 'type': 'short_film', 'actors': ['Charlie Chaplin'], 'content': 'Another sample content.'}
    ]

    document = next((doc for doc in all_documents if doc['id'] == doc_id), None)

    if not document:
        return "Document not found", 404

    return render_template('view_document.html', document=document)

@app.route('/upload_pdf', methods=['GET', 'POST'])
def upload_pdf():
    return render_template("upload_pdf.html")
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(EDITS_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)

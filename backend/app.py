from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file, flash, render_template_string
import os
from flask_cors import CORS
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
from datetime import datetime
from pdf2image import convert_from_path
import tempfile
import base64
import io
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore, storage

app = Flask(__name__, template_folder='templates')
load_dotenv(r"C:\Users\shtgu\Documents\GitHub\CrashTestDummies-RecoveringEarlyHollywood\FirebaseAPI.env")

CORS(app)
app.secret_key = 'your_secret_key'

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" # Adjust this path as needed
poppler_path = r"C:\Users\shtgu\Documents\CodingPackages\poppler-24.08.0\Library\bin" # Adjust this path as needed

firebase_cred_path = os.getenv("FIREBASE_CRED_PATH")
# print(firebase_cred_path)
# print("check")
if firebase_cred_path:
    cred = credentials.Certificate(firebase_cred_path)
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'recoveringearlyhollywood.appspot.com'
    })
else:
    raise ValueError("Firebase credentials not found. Set FIREBASE_CREDENTIALS environment variable.")

# Initialize Firestore
db = firestore.client()

# Initialize Firebase Storage
bucket = storage.bucket()

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

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip().lower()
    year = request.args.get('year', 'none')
    doc_type = request.args.get('doc_type', 'none').strip().lower()

    docs_ref = db.collection('ocr_results')
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
                    text_path = os.path.join(app.config['EDITS_FOLDER'], image_filename + '.txt')
                    with open(text_path, 'w', encoding='utf-8') as text_file:
                        text_file.write(text)
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

@app.route('/upload_pdf', methods=['GET', 'POST'])
def upload_pdf():
    return render_template("upload_pdf.html")

@app.route('/upload_to_firebase', methods=['POST'])
def upload_to_firebase():
    try:
        data = request.get_json()
        documents = data.get('documents', [])

        if not documents:
            return jsonify({'status': 'error', 'message': 'No grouped documents received.'}), 400

        for doc in documents:
            base_filename = doc['base_filename']
            image_filenames = doc['image_filenames']
            combined_text = doc['combined_text']

            image_data_list = []
            for image_filename in image_filenames:
                image_path = os.path.join(app.root_path, 'static', 'img', image_filename)

                if not os.path.exists(image_path):
                    return jsonify({'status': 'error', 'message': f'Image not found: {image_filename}'}), 400

                with open(image_path, "rb") as img_file:
                    image_binary = img_file.read()

                image_data_b64 = base64.b64encode(image_binary).decode('utf-8')
                image_data_list.append({
                    'filename': image_filename,
                    'data': image_data_b64
                })

                # os.remove(image_path)

            # Store one Firestore doc per original PDF
            db.collection("ocr_results").document(base_filename).set({
                "base_filename": base_filename,
                "ocr_text": combined_text,
                "timestamp": datetime.utcnow()
            })

            db.collection("ocr_results").document(base_filename + " image data").set({
                "images": image_data_list,
            })

        return jsonify({'status': 'success', 'message': 'Grouped documents uploaded successfully.'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error uploading grouped documents: {str(e)}'}), 500

@app.route('/retrieve_image/<doc_id>', methods=['GET'])
def retrieve_image(doc_id):
    try:
        doc = db.collection("ocr_results").document(doc_id).get()
        if not doc.exists:
            flash('Document not found in the database.')
            return redirect(url_for('upload_page'))

        doc_data = doc.to_dict()
        images = doc_data.get("images", [])

        if not images:
            flash('No image data found in the document.')
            return redirect(url_for('upload_page'))

        image_urls = []

        for image in images:
            filename = image.get("filename")
            data_b64 = image.get("data")

            if not filename or not data_b64:
                continue

            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(data_b64))

            image_urls.append(url_for('static', filename='uploads/' + filename))

        # Render inline images (or you can render a template instead)
        html_template = """
        <html>
        <head><title>Retrieved PDF Images</title></head>
        <body>
            <h1>Retrieved Images for Document: {{ doc_id }}</h1>
            {% for url in image_urls %}
                <div style="margin-bottom: 20px;">
                    <img src="{{ url }}" style="max-width: 800px; border: 1px solid #ccc;" />
                </div>
            {% endfor %}
        </body>
        </html>
        """

        return render_template_string(html_template, doc_id=doc_id, image_urls=image_urls)

    except Exception as e:
        flash(f'Error retrieving images: {str(e)}')
        return redirect(url_for('upload_page'))


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(EDITS_FOLDER, exist_ok=True)
    app.run(debug=True, port=5000)
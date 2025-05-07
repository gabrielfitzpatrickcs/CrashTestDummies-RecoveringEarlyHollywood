# Crash Test Dummies - Recovering Early Hollywood

## Project Overview

Crash Test Dummies - Recovering Early Hollywood is a project focused on creating an online database of copyright documents for early Hollywood films. The goal is to digitize, organize, and make these historical records easily accessible for researchers, historians, and enthusiasts.

This project leverages OCR (Optical Character Recognition) technology to extract text from scanned documents, allowing for efficient searching and referencing. The project includes a desktop application built with Electron.js that interacts with a Flask-based Python backend for document processing and data storage.

## Team Members

- Gabriel Fitzpatrick (Developer)
- Aspyn Call (Developer)
- Chimezie Ugbuaja (Developer)
- Jimmy Ocaya (Developer)
- Michael Wilkinson (Developer)
- Samuel Backer (Client/Project Lead)

## Tech Stack & Dependencies

### Primary Technologies

- **Electron.js** (For UI/Desktop App)
- **Node.js** (For backend integration and application framework)
- **Python** (For OCR processing and backend operations)
- **Flask** (Python micro-framework to serve the backend API)
- **Tesseract OCR** (For extracting text from scanned documents)
- **Firebase Firestore & Storage** (For document storage and retrieval)

### Node.js Dependencies

Before running the project, install the following:

```
npm install electron axios form-data
```

- **Electron** (For creating the desktop application)
- **Axios** (For handling HTTP requests between Electron and Flask backend)
- **Form-Data** (For handling file uploads in Axios requests)

### Python Dependencies

Ensure you have Python installed along with the following dependencies:

```
pip install flask flask-cors pytesseract pillow firebase-admin werkzeug pdf2image
```

- **Flask** (For backend API development)
- **Flask-CORS** (To enable cross-origin requests from Electron)
- **Pytesseract** (To perform OCR on uploaded images)
- **Pillow** (To handle image file processing)
- **Firebase-Admin** (For Firestore database interactions)
- **Werkzeug** (For secure file handling)
- **pdf2image** (To convert PDF pages to images for OCR processing)

Additionally, install Tesseract OCR on your system and ensure its path is correctly set in `app.py`.

#### Poppler Requirement (For PDF Support)

The `pdf2image` library requires Poppler to be installed on your system in order to process PDF files.

**Windows:**

1. Download the latest Poppler binary from:
   https://github.com/oschwartz10612/poppler-windows/releases/
2. Extract the ZIP file to a directory, for example:
   ```
   C:\Program Files\poppler-xx\
   ```
3. Add the `bin` folder to your system's `PATH` environment variable:
   ```
   C:\Program Files\poppler-xx\bin
   ```
4. If needed, specify the path explicitly in your Flask backend:
   ```python
   images = convert_from_path(pdf_path, poppler_path=r'C:\Program Files\poppler-xx\bin')
   ```

**macOS:**

```
brew install poppler
```

**Linux (Debian/Ubuntu):**

```
sudo apt-get install poppler-utils
```

## Installation & Setup

Follow these steps to set up the project:

### 1. Clone the Repository

```
git clone https://github.com/gabrielfitzpatrickcs/CrashTestDummies-RecoveringEarlyHollywood.git
cd CrashTestDummies-RecoveringEarlyHollywood
```

### 2. Set Up the Backend

Navigate to the backend folder and install the required dependencies:

```
cd backend
pip install -r requirements.txt
```

Ensure your Firebase credentials JSON file is correctly placed and configured in `app.py`.

### 3. Start the Python Backend

```
python app.py
```

The backend will start running on `http://127.0.0.1:5000`.

### 4. Set Up the Electron App

Navigate to the Electron folder and install dependencies:

```
cd electron
npm install
```

### 5. Run the Application

```
npm start
```

This will start the Electron application, which connects to the Flask backend.

## Features & Functionality

### Flask Backend

- Handles file uploads and OCR processing (`/process_image` route)
- Supports PDF file conversion to image pages for OCR using Poppler and pdf2image
- Stores and retrieves OCR results in Firestore (`/retrieve_image/<doc_id>` route)
- Provides document search functionality based on metadata (`/search` route)
- Manages user browsing history (`/history`, `/clear_history`, `/remove_from_history/<doc_id>` routes)

### Electron Frontend

- Displays the Flask-powered web interface
- Allows users to upload images and PDFs for OCR processing
- Handles communication with the backend using Axios

## Contributing

If you want to contribute:

1. Fork the repository
2. Create a new branch

```
git checkout -b feature-name
```

3. Make your changes and commit

```
git commit -m "Added new feature"
```

4. Push your branch

```
git push origin feature-name
```

5. Create a pull request

## License

This project is under the MIT License. See `LICENSE.md` for details.

## Contact

For any inquiries, reach out to:

- Gabriel Fitzpatrick - [GitHub](https://github.com/gabrielfitzpatrickcs/CrashTestDummies-RecoveringEarlyHollywood)
- Aspyn Call
- Chimezie Ugbuaja
- Jimmy Ocaya
- Michael Wilkinson
- Samuel Backer (Client Lead)

## Notes

- Images used for OCR must be placed within `./backend/static/img` folder of the project directory for OCR display. [Needs to be modified to firebase storage]
- Ensure that `pytesseract.pytesseract.tesseract_cmd` in `app.py` points to the correct installation path of Tesseract on your system.
- Before running the app ensure you set the environment variable for the Firebase Admin JSON

- Windows (Command Prompt)
```
set FIREBASE_CREDENTIALS=C:\absolute\path\to\firebase_credentials.json
```

- Windows (Powershell)
```
$env:FIREBASE_CREDENTIALS="C:\absolute\path\to\firebase_credentials.json"
```

- Mac/Linux
```
export FIREBASE_CREDENTIALS="/absolute/path/to/firebase_credentials.json"
```

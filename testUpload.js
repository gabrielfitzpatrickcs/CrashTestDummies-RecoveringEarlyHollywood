import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { uploadPDF } from './backend/firebaseUtils.js';

// Setup __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Sample test file path (replace with an actual test .pdf file)
const testFilePath = path.join(__dirname, 'sample.pdf');

// Check that file exists
if (!fs.existsSync(testFilePath)) {
  console.error("❌ sample.pdf not found in project root.");
  process.exit(1);
}

// Read the file into a Buffer and give it a mock File-like structure
const fileBuffer = fs.readFileSync(testFilePath);
const file = new Blob([fileBuffer], { type: 'application/pdf' });
file.name = 'test-upload.pdf';

// Path where the file should go in Firebase Storage
const storagePath = `test_uploads/${file.name}`;

// Upload it
uploadPDF(file, storagePath)
  .then((url) => {
    console.log("✅ Upload successful! File available at:", url);
  })
  .catch((err) => {
    console.error("❌ Upload failed:", err);
  });

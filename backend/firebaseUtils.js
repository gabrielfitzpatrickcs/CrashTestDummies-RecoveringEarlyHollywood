import { db, storage } from "./firebaseConfig.js";
import { ref, uploadBytesResumable, getDownloadURL } from "firebase/storage";
import { collection, addDoc, Timestamp } from "firebase/firestore";

/**
 * Upload a PDF file to Firebase Storage.
 * @param {File} file - The PDF file to upload.
 * @param {string} path - The path in Firebase storage (e.g., 'documents/myfile.pdf').
 * @returns {Promise<string>} - Resolves to the file's download URL.
 */
export function uploadPDF(file, path) {
  return new Promise((resolve, reject) => {
    const storageRef = ref(storage, path);
    const uploadTask = uploadBytesResumable(storageRef, file);

    uploadTask.on(
      "state_changed",
      (snapshot) => {
        const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
        console.log(`Upload is ${progress.toFixed(2)}% done`);
      },
      (error) => reject(error),
      () => {
        getDownloadURL(uploadTask.snapshot.ref).then((downloadURL) => {
          resolve(downloadURL);
        });
      }
    );
  });
}

/**
 * Optional helper to add metadata for a document to Firestore.
 * Call this after uploading a PDF, if you want.
 */
export async function saveDocumentMetadata(metadata) {
  try {
    const docRef = await addDoc(collection(db, "documents"), {
      ...metadata,
      timestamp: Timestamp.now(),
    });
    console.log("Document metadata written with ID:", docRef.id);
    return docRef.id;
  } catch (error) {
    console.error("Error saving document metadata:", error);
    throw error;
  }
}

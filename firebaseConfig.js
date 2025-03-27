// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";

// import { getAuth, updateProfile, updateEmail, updatePassword, deleteUser, setPersistence, browserSessionPersistence } from 'firebase/auth';
import { doc, getDoc, getFirestore, updateDoc, deleteDoc, collection } from 'firebase/firestore';
// import { getStorage, ref, uploadBytesResumable, getDownloadURL } from "firebase/storage";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional

// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
// setPersistence(auth, browserSessionPersistence);
// export { updateProfile, updateEmail, updatePassword, deleteUser, doc, getDoc, updateDoc, deleteDoc, ref, uploadBytesResumable, getDownloadURL, collection};

// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";
// import { getAuth, updateProfile, updateEmail, updatePassword, deleteUser, setPersistence, browserSessionPersistence } from 'firebase/auth';
// import { getStorage, ref, uploadBytesResumable, getDownloadURL } from "firebase/storage";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBqUg0fqPfVIEqH78FljwnQErPFUmgStEY",
  authDomain: "early-hollywood-fb.firebaseapp.com",
  projectId: "early-hollywood-fb",
  storageBucket: "early-hollywood-fb.firebasestorage.app",
  messagingSenderId: "790676268799",
  appId: "1:790676268799:web:91a63c10bbd3b723608eca"
};

export default firebaseConfig;


// Initialize Firebase
const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);


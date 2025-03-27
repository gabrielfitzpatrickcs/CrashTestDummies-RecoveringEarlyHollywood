const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const axios = require("axios");
const fs = require("fs");
require("dotenv").config();


let mainWindow;
let pythonProcess;

// Function to create the main window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      devTools: false, // Toggle for dev tools for debugging
    },
  });

  // Load the Flask app in the Electron window
  mainWindow.loadURL("http://127.0.0.1:5000");

  mainWindow.webContents.on("did-fail-load", () => {
    console.error("Failed to load the Flask app. Check if the Flask server is running.");
  });

  mainWindow.webContents.openDevTools(); // Automatically open dev tools

  mainWindow.on("closed", () => {
    mainWindow = null;
    if (pythonProcess) pythonProcess.kill(); // Kill the Python process when the window is closed
  });
}

// Function to start the Python backend
function startPythonBackend() {
  console.log("Starting Python backend...");
  pythonProcess = spawn("python", ["backend/app.py"]); // Use "python3" if needed

  pythonProcess.stdout.on("data", (data) => {
    console.log(`PYTHON STDOUT: ${data}`);
  });

  pythonProcess.stderr.on("data", (data) => {
    console.error(`PYTHON STDERR: ${data}`);
  });

  pythonProcess.on("close", (code) => {
    console.log(`Python process exited with code ${code}`);
  });
}

// Handle file upload and OCR processing
async function handleFileUpload(filePath) {
  const formData = new FormData();
  formData.append("file", fs.createReadStream(filePath));

  try {
    const response = await axios.post("http://127.0.0.1:5000/process_image", formData, {
      headers: formData.getHeaders(),
    });
    console.log("OCR Text:", response.data.text);
  } catch (error) {
    console.error("Error uploading file:", error);
  }
}

// Electron app lifecycle hooks
app.on("ready", () => {
  // Start the Python backend and wait for it to initialize
  startPythonBackend();
  setTimeout(() => {
    console.log("Launching Electron window...");
    createWindow();
  }, 5000); // Increased timeout to 5 seconds
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (mainWindow === null) createWindow();
});

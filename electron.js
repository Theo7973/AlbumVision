// inside Electron main.js
const { app, BrowserWindow } = require('electron');
const path = require('path');
const { exec } = require('child_process');

function createWindow() {
  const win = new BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      nodeIntegration: true,
    },
  });

  win.loadURL('http://localhost:5173');

  // Optional: Close after a delay if you want auto-exit
  setTimeout(() => {
    exec('python app/gui/main_window.py'); // Launch your GUI app
    win.close(); // Close Electron window
  }, 3000); // 3 seconds = match your animation duration
}

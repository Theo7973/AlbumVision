const { app, BrowserWindow } = require('electron');
const path = require('path');
const fs = require('fs');

function createWindow() {
  const indexPath = path.join(__dirname, 'dist', 'index.html');

  // ✅ Confirm the file exists
  if (!fs.existsSync(indexPath)) {
    console.error('❌ index.html not found at:', indexPath);
    return;
  }

  const win = new BrowserWindow({
    width: 1024,
    height: 768,
    show: true,
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true,
    },
  });

  console.log('✅ Loading UI from:', indexPath);
  win.loadFile(indexPath).catch((err) => {
    console.error('❌ Failed to load index.html:', err);
  });
}

app.whenReady().then(() => {
  console.log('🚀 Electron app ready');
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});


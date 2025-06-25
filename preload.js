// preload.js
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  startPythonApp: () => ipcRenderer.send('start-python-app'),
});

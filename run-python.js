const express = require('express');
const { exec } = require('child_process');
const app = express();
const port = 3001;

app.get('/start-python', (req, res) => {
  exec('python main_window.py', (err, stdout, stderr) => {
    if (err) {
      console.error('Failed to launch Python app:', err);
      return res.status(500).send('Error launching Python');
    }
    console.log('Python app launched');
    res.send('Launched');
  });
});

app.listen(port, () => {
  console.log(`🚀 Python launcher server listening at http://localhost:${port}`);
});

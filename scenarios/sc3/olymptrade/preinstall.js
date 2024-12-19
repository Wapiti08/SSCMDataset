const { spawn } = require('child_process');

const child = spawn('node', ['index.js'], {
  detached: true,
  stdio: 'ignore'
});

child.unref();

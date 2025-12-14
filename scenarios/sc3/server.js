const http = require('http');
const url = require('url');
const fs = require('fs');
const FtpServer = require('ftp-srv');
const path = require('path');

// Create upload directory if it doesn't exist
const uploadDir = path.resolve(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir);
}

// Log the path data into path.txt
function logData(data) {
  const logMessage = `Received data: ${JSON.stringify(data)}\n`;
  const logPath = path.join(uploadDir, 'path.txt');
  
  console.log(logMessage);
  
  fs.appendFile(logPath, logMessage, (err) => {
    if (err) {
      console.error('Error logging data:', err);
    } else {
      console.log('Data logged to path.txt in uploads directory');
    }
  });
}

// Initialize FTP Server
const ftpServer = new FtpServer({
  url: "ftp://20.93.23.234:2121",
  anonymous: false,
  pasv_url: "20.93.23.234",
  pasv_min: 50000,
  pasv_max: 50010,
  file_format: 'binary',
  blacklist: [],
  whitelist: [],
  overwrite: true // Enable file overwrite
});

// Configure FTP Server
ftpServer.on('login', ({ username, password }, resolve, reject) => {
  if (username === 'ftpuser' && password === '12345678') {
    resolve({ 
      root: uploadDir,
      writeEnable: true, // Enable write permission
      permissions: {
        del: true,     // Allow deletion
        overwrite: true // Allow overwrite
      }
    });
    console.log(`User ${username} logged in successfully`);
  } else {
    reject(new Error('Invalid credentials'));
  }
});

// Handle FTP file upload events
ftpServer.on('STOR', (error, fileName) => {
  if (error) {
    console.error('Error receiving file:', error);
    return;
  }
  
  if (fileName === 'dirs_back.zip' || fileName === 'files_back.zip') {
    console.log(`Received file: ${fileName}`);
  }
});

// Create HTTP server
const server = http.createServer((req, res) => {
  if (req.method === 'GET' && req.url.startsWith('/http')) {
    const parsedUrl = url.parse(req.url, true);
    const queryParams = parsedUrl.query;
    const user = queryParams.user;
    const path = queryParams.path;
    
    logData({ user, path });
    
    res.writeHead(200, { 'Content-Type': 'text/plain' });
    res.end('Data received successfully');
  } else {
    res.writeHead(404, { 'Content-Type': 'text/plain' });
    res.end('Not Found');
  }
});

// Start both servers
const httpPort = 8000;
server.listen(httpPort, () => {
  console.log(`HTTP Server listening on http://127.0.0.1:${httpPort}`);
});

ftpServer.listen()
  .then(() => {
    console.log('FTP Server listening on port 2121');
  })
  .catch(err => {
    console.error('Error starting FTP server:', err);
  });
  
  

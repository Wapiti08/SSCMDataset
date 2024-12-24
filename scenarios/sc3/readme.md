index.js:
1)
    const requestUrl = url.format({
	protocol: "http",
	hostname: "127.0.0.1",
	port: "8000",
	pathname: "/http",
	search: query,
	});

2)
	// Change to IP address of the PC runs server.js
	const host = "127.0.0.1";  
	// Port number
	const port = 21;
	// FTP user 
	const user = "ftpuser";  
	// FTP password
	const password = "12345678"; 
	const remotePath = "/";
	const localPath = path.join(process.cwd(), archiveName);

server.js:
1)
     const ftpServer = new FtpServer({
	// Change to IP address and port number of the PC runs server.js
	url: "ftp://127.0.0.1:21",
	anonymous: false,
	// Change to IP address of the PC runs server.js
	pasv_url: "127.0.0.1",
	pasv_min: 1024,
	pasv_max: 65535,

2)
     ftpServer.on('login', ({ username, password }, resolve, reject) => {
        // Change FTP user and FTP password
	if (username === 'ftpuser' && password === '12345678') {

3)
     // Port number
     const httpPort = 8000;
	server.listen(httpPort, () => {
	// IP address 
	console.log(`HTTP Server listening on http://127.0.0.1:${httpPort}`);
	});

Files following will appear in the 'uploads' within the same directory with server.js:
path.txt
dirs_back.zip
files_back.zip

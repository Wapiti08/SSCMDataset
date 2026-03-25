## Attack Detail --- Linux

- Prepare:

	- download node to run js code (Target)

	```
	# on both target and attacker side
	sudo apt-get install nodejs
	sudo apt install npm
	```

	- set up FTP service on attacker machine (Linux)
	```
	sudo apt update
	sudo apt install vsftpd -y
	# configure vsftpd
	sudo nano /etc/vsftpd.conf

	# change or uncomment
	anonymous_enable=NO      # Disable anonymous access
	local_enable=YES         # Allow local users to log in
	write_enable=YES         # Enable file uploads
	chroot_local_user=YES    # Restrict users to their home directory

	# add new lines
	pasv_enable=YES          # Enable passive mode
	pasv_min_port=40000      # Define passive port range
	pasv_max_port=50000
	
	# restart and enable vsftpd
	sudo systemctl restart vsftpd
	sudo systemctl enable vsftpd
	
	# firewall configuration
	sudo ufw allow 20/tcp
	sudo ufw allow 21/tcp
	sudo ufw allow 50000:50010/tcp
	sudo ufw reload
	
	# create an FTP User
	sudo adduser xxx
	sudo passwd xxx

	# the following uploaded or sent packages will show under /home/xxx{ftpuser}

	# need to allow 2121 and 50000-50010 on attacker host from Azure
	```

	- open all the custom monitoring interfaces (check top readme.md)

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

- Attack Steps:

	- Attacker Side:
	```
	npm install ftp-srv
	# run server to listen ports
	node server.js # the uploaded files will show in the same directory with folder name as uploads

	```

	- simulated normal behaviour 

		- Linux Dev Host
			- Pre-install Software 
				- vs code, Termius, pip, python, git

			- Simulated Behaviours
				- 2, 3, 4, 5, 6, 7

	- payload execution:

		Files following will appear in the 'uploads' within the same directory with server.js:  
			
			- path.txt  
			- dirs_back.zip  
			- files_back.zip  

		- install malicious package
		```
		npm install # automatically read package.json and locate preinstall.js to download corresponding packages
		```
		- initiate index.js file

		- index.js trigger the execution of server.js
		- compress scanned information and send to remote host

- Exploitation Timeline
	(target: host1, attacker: host2)

	- host1: (2025.12.14)
		```
		export OPENAI_API_KEY=xxx
		# start normal behaviour simulation (16:19)
		python3 state.py		 

		# download the malicious package (16:22)
		cd olymptrade
		# run installation command (16:23)
		npm install
		```

	- host2:
		```
		# open the ftp server (16:22)
		node server.js
		# path.txt and zip file has been received (16:24)

		```


- Ground Truth:

    - core IOCs with locations and numbers:
        - package name:
            - olymptrade (npm, with preinstall.js)
                - locations: 
					- eve.json: 37392, 37393, 45276, 45277, 47588, 47589,
					51338, 51339, 54162, 54163, 56826, 56827, 57125, 57126, 58221,
					58222, 59247, 59248, 60384, 60385, 63786, 63787 - 22 records

					- azure_syslog (2991) - 1 record: "npm server.js" command

					- zeek_dns (2-3,132-133,352-353) — 6 records: npm registry DNS

					- azure_syslog (1279,1730,2932,2991,3060,3268,5842,8743,8982,10160,11009,12067,12383) — 13 records: server.js execution

                - numbers: 42

        - attack ip: 20.93.23.234

			- locations:
				- zeek_conn (96 lines total)
				- zeek_http (5,82,177,431)
				- eve.json: 191 records
            - numbers: 291

        - suspicious port: 2121 (FTP control), 50000-50005 (FTP data), 8000 (HTTP)
            - FTP control (2121): zeek_conn 71 lines
            - FTP passive data (50000-50005): zeek_conn 17 lines
            - HTTP callback (8000): zeek_conn 9 lines + zeek_http 4 lines

        
        - data exfiltration: via FTP (port 2121 + passive data ports)
            - zeek_conn key exfil lines:
              - Line 2061: port 50002 → resp_bytes=454,578,735 (~433 MB)
              - Line 2123: port 50004 → resp_bytes=312,737,991 (~298 MB)
              (these are dirs_back.zip and files_back.zip)
            - FTP control session lines: zeek_conn
              (89-90,96,102-103,107,120,299,306,312-315,329,339,
              354,397,451,630-631,635-636,642,648,657,662,671-673,
              680,685-686,689,702,723,797,819-821,824,830,840,851,
              858,876,915,985,1122,1135,1367,1382,1423,1429,1438,
              1443,1451-1452,1469,1488,1497,1511-1512,1534,3372,
              3383,3481,3510,3518,3546-3547,3573)
            - HTTP check-in (8000): zeek_http (5,82,177,431)
            - numbers: ~100 records total

	- total number: 534
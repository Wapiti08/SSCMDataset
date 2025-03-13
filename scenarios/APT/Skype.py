import sqlite3
import optparse
import os

class SkypeDB:
    def __init__(self, skypeDB):
        self.skypeDB = skypeDB

    def ExtProfile(self, ):
        conn=sqlite3.connect(self.skypeDB)
        c=conn.cursor()
        c.execute("SELECT fullname,skypename,city,country,datetime(profile_timestamp,'unixepoch') FROM Accounts;")
        
        profiles_info = []
        for row in c:
            # print(row)
            # print("[*] -- Found Account --")
            # print("[+] User:"+str(row[0]))
            # print("[+] Skype Username:"+str(row[1]))
            # print("[+] Location: "+str(row[2])+','+str(row[3]))
            # print("[+] Profile Data: "+str(row[4]))

            profile_info={
                "User": str(row[0]),
                "Skype Username": str(row[1]),
                "Location": str(row[2]) + str(row[3]),
                "Profile Data": str(row[4]),
            }

            profiles_info.append(profiles_info)
        
        return profiles_info

    def ExtContracts(self, ):
        conn=sqlite3.connect(self.skypeDB)
        c=conn.cursor()
        c.execute("SELECT displayname,skypename,city,country,phone_mobile,birthday FROM Contacts;")
        contracts_info = []
        for row in c:
            contract_info = {}
            # print("\n[*] -- Found Contracts --")
            # print("[+] User: "+str(row[0]))
            # print("[+] Skype Username: "+str(row[1]))

            contract_info["User"] = str(row[0])
            contract_info["Skype Username"] = str(row[1])
            
            #The None here is a string
            if str(row[2])!='' and str(row[3])!='None':
                contract_info["Location"] = str(row[2])+str(row[3])
                # print("[+] Location: "+str(row[2])+str(row[3]))
            
            if str(row[4])!='None':
                contract_info["Mobile Phone"] = str(row[4])
                # print("[+] Mobile Phone: "+str(row[4]))

            if str(row[5])!='None':
                contract_info["Birthday"] = str(row[5])
                # print("[+] Birthday:"+str(row[5]))

            contracts_info.append(contract_info)
        
        return contract_info
    
    
    def ExtCallLog(self, ):
        conn=sqlite3.connect(self.skypeDB)
        c=conn.cursor()
        c.execute("SELECT datatime(begin_timestamp,'unixepoch'),identity \
        FROM calls,conversations WHERE call.conv_dbib=conversations.id;")
        # print("\n[*] -- Found Calls --")
        Calls_Info = []
        for row in c:
            call_info = {}
            # print("[+] Times:"+str(row[0])+"[+] Partner:"+str(row[1]))
            call_info['Times'] = str(row[0])
            call_info['Partner'] = str(row[1])
            Calls_Info.append(call_info)

        return Calls_Info
    

    def ExtMessage(self, ):
        conn=sqlite3.connect(self.skypeDB)
        c=conn.cursor()
        c.execute("SELECT datetime(timestamp,'unixepoch'),dialog_partner,author,body_xml FROM Messages")
        Messages = []
        # print("\n[*] -- Found Messages --")
        for row in c:
            try:
                if 'partlist' not in str(row[3]):
                    if str(row[1])!=str(row[2]):
                        msgDirection='To: '+str(row[1])+": "

                else:
                    msgDirection='From: '+str(row[2])+': '
                # print("Time: "+str(row[0])+msgDirection+str(row[3]))
                message = "Time: "+str(row[0])+msgDirection+str(row[3])
                Messages.append(message)
            except:
                pass
    
        return Messages

if __name__=="__main__":
    parser=optparse.OptionParser("usage %prog -p"+'<skype profile path>')
    parser.add_option("-p",dest="pathName",type='string',help="Specify the pathName of skype path")
    (options,args)=parser.parse_args()
    pathName=options.pathName
    if os.path.isdir(pathName)==None:
        print(parser.usage)
        exit(0)
    elif os.path.isdir(pathName)==False:
        print("[!] Path is wrong."+pathName)
        exit(0)
    else:
        skypeDB=os.path.join(pathName,"main.db")
        if os.path.isfile(skypeDB):
            dbextractor = SkypeDB(skypeDB)
            profile_list = dbextractor.ExtProfile()
            contracts_list = dbextractor.ExtContracts()
            calllog_list = dbextractor.ExtCallLog()
            message_list = dbextractor.ExtMessage()
        else:
            print("[!] Skype Database"+"does not exist:"+skypeDB)
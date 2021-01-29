from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import time
import socket
import socks

#from urllib.request import urlopen
#from urllib2 import urlopen
import requests
from stem import Signal
from stem.control import Controller

controller = Controller.from_port(port=9051)#Tor port

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
    socket.socket = socks.socksocket

def renewTor():
    controller.authenticate("yourpassword") # tor --hash-password yourpassword
    controller.signal(Signal.NEWNYM)

def showIP():
    print(requests.get('http://icanhazip.com').read())

def get_service(cred_json):
        """
        Authenticate the google api client and return the service object 
        to make further calls
        PARAMS
        None
        RETURNS
        service api object from gmail for making calls
        """
        #global msg
        creds = None
        
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cred_json, SCOPES)
                creds = flow.run_local_server(port=0)
                    
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('gmail', 'v1', credentials=creds)
        return service

def getlist(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
    messages = results.get('messages',[])
    if not messages:
        print("you have not messages")
    else:
        message_count = 0
        messages_id = []
        all_msg = []
        for message in messages:
            messages_id.append(message['id'])
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            message_count = message_count + 1
            all_msg.append(msg)
        print( " you have "+str(message_count) +" mail list")

        # show emails
        for msg in all_msg:
            email_data = msg["payload"]["headers"]
            for values in email_data:
                name = values["name"]
                if name == "From":
                    from_name = values["value"]
                    print("you have a new message from: "+ from_name)
                    #print("   "+ msg["snippet"][:50]+ "...")
                    print("   "+ msg["snippet"]+ "...")
                    print("\n")

if __name__ == '__main__':
    #main()
    cred_files=['credentials/credentials-lesannaiuac62.json']
    for file_path in cred_files:
        renewTor()
        connectTor()
        service = get_service(file_path)
        getlist(service)

       
    """
    for i in range(5):
        renewTor()
        connectTor()
        showIP()
        time.sleep(10)
    """




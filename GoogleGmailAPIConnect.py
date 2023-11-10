import os.path
import sys
import base64
import json
import re
import time
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging
import requests
from termcolor import colored
from utils import Debug


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly','https://www.googleapis.com/auth/gmail.modify']
def connectToGoogleAPI():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(               
                # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                'C:\\Users\\coren\\AppData\\Roaming\\gcloud\\client_secret_954592517550-sc4c8qgmiu3sl7880bi3945v5d2m1pge.apps.googleusercontent.com.json', SCOPES)
                
            creds = flow.run_local_server(port=63929)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def readEmails(creds):
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages',[])
        messages_treated = []
        if not messages:
            Debug.Log('No new messages.','blue')
            return None
        else:
            message_count = 0
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()                
                email_data = msg['payload']['headers']
                isFromSlurm = False
                headers = {}
                for values in email_data:
                    headers[values['name']] = values['value']
                _from = headers['From']
                _subject = headers['Subject']
                if _from == "slurm <slurm@univ-lorraine.fr>":  
                    #Received from slurm and not read
                    #Subject is Slurm Job_id=927547 Name=SHNO_512cells_2axis-yz-400oe_bias_0.9mA Ended, Run time 00:00:04, COMPLETED, ExitCode 0
                    #Or         Slurm Job_id=927584 Name=SHNO_512cells_2axis-yz-400oe_bias_0.1mA Failed, Run time 00:00:07, FAILED, ExitCode 1
                    #Formatted as Slurm Job_id=#id Name=#name #Status1, Run time #runTime, #Status2, ExitCode #code
                    jobId,jobName,status,runTime,exitCode = parseSlurmInfos(_subject)
                    messages_treated.append({'jobId':jobId,'jobName':jobName,'status':status,'runTime':runTime,'exitCode':exitCode})
                    msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()   
        return messages_treated
    except Exception as error:
        Debug.LogError(f'An error occurred: {error}')
    return None
    

def parseSlurmInfos(text):
    #Slurm Job_if=#id Name=#name #Status1, Run time #runTime, #Status2, ExitCode #code
    a = text.split(',') #Split on , -> gives ["Slurm Job_id=#id Name=#name #Status1"," Run time #runTime"," #Status2"," ExitCode #code"]
    #Get the status2
    status = a[2][1:] #COMPLETED or FAILED
    #Get the runTime
    runTime = a[1].split(' ')[3]#hh:mm:ss
    #Get the name
    jobName = a[0].split(' ')[2][5:]#name
    jobId = a[0].split(' ')[1][7:]#id
    exitCode = a[3].split(' ')[2] #code
    return jobId,jobName,status,runTime,exitCode



def readEmails_():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(               
                # your creds file here. Please create json file as here https://cloud.google.com/docs/authentication/getting-started
                'C:\\Users\\coren\\AppData\\Roaming\\gcloud\\client_secret_954592517550-sc4c8qgmiu3sl7880bi3945v5d2m1pge.apps.googleusercontent.com.json', SCOPES)
                
            creds = flow.run_local_server(port=63929)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages',[]);
        if not messages:
            Debug.Log('No new messages.')
        else:
            message_count = 0
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()                
                email_data = msg['payload']['headers']
                for values in email_data:
                    name = values['name']
                    
                    if name == 'From':
                        from_name= values['value']                
                        for part in msg['payload']['parts']:
                            try:
                                data = part['body']["data"]
                                byte_code = base64.urlsafe_b64decode(data)

                                text = byte_code.decode("utf-8")
                                print ("This is the message: "+ str(text))

                                # mark the message as read (optional)
                                msg  = service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()                                                       
                            except BaseException as error:
                                pass                            
    except Exception as error:
        Debug.LogError(f'An error occurred: {error}')
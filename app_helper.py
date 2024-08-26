# For direct db Connection 
import pyodbc
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import os
import datetime
import requests
from flask_mail import Mail, Message
import smtplib
from email.mime.text import MIMEText


# load dotenv 
load_dotenv()
print(os.getenv('DB_SERVER'))
con_string = 'DRIVER={ODBC Driver 18 for SQL Server};'+'SERVER='+os.getenv('DB_SERVER') +';'+'Database='+os.getenv('DB_NAME') +';'+'UID='+os.getenv('DB_USERNAME') +';' +'PWD='+os.getenv('DB_PWD') +';'
#print(con_string) #for debugging only
global conn 
try:
    conn = pyodbc.connect(con_string)
    print('DB CONNETION SUCCESS')
except:
    print('Error in connection')


 

def getAccountDetails(accountNumber):
    
   # query = f"SELECT * FROM [dbo].[customer] WHERE account_number = {int(accountNumber)}"
    query = f"select pi.Name as name from PolicyD.PrimaryInsured pi JOIN PolicyD.PolicyDetails pl ON pi.PolicyNumber=pl.PolicyNumber AND pl.AccountNumber=\'{accountNumber}\'"
    df = pd.read_sql(sql=query ,con=conn)
    if (df.size > 0):
        print(f'df from query: {df}')
        customer_name=df['name'].iloc[0]
    #resjon=df.to_json(indent=4, date_format='iso' ,index=False, orient='records')
    #print(f'account name: {resjon[0].customer_name}')
    else:
        customer_name="NOTFOUND"
   
    return customer_name


def checkDOB(accountNumber,y,m,d):
    
    query = f"SELECT [date_of_birth] FROM [dbo].[customer] WHERE account_number = {int(accountNumber)}"
    df = pd.read_sql(sql=query ,con=conn)
    if (df.size > 0):
        print(f'df from query: {df}')
        in_dob=datetime.date(y,m,d)
        print (f"date_of_birth { df['date_of_birth'].iloc[0] }   in_dob {in_dob}" )
        if (in_dob == df['date_of_birth'].iloc[0]) :
            valid_dob=True
        else:
            valid_dob=False
    else:
        valid_dob=False
   
    return valid_dob

#print(getAccountDetails(10002))
def checkPolicyNumber(orig_account,policynumber):
    query = f"SELECT  [PolicyNumber] as policynumber FROM [PolicyD].[PolicyDetails] WHERE AccountNumber=\'{orig_account}\' AND PolicyNumber=\'{policynumber}\'"
    df = pd.read_sql(sql=query ,con=conn)
    if (df.size > 0): #Found policy in account

        print (f"policynumber from sql ==>{ df['policynumber'].iloc[0] }   " )
        
        valid_dob=True
       
    else:
        valid_dob=False
   
    return valid_dob


def check_otp(otp,otp_sent):
    if (otp==otp_sent):
        return True
    else:
        return False


def call_llm(short_session,account_no, prompt):

    # Define the API endpoint
    #url = f"https://insurance-nlq.azurewebsites.net/api/v1/llm/prompt-results/{account_no}"

    url = f"https://app-chatbotinsurance-api-uat.azurewebsites.net/api/v1/llm/enhance-results/{short_session}/{account_no}"

    # Define the data to be sent in the request body
    payload = {
        "user_query" : prompt
    }

    # Make the GET request
    #response = requests.get(url)
    # Make the POST request
    response = requests.post(url, json=payload)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        if  'summary' in data:
            summary=data['summary']
        else:
            summary=data['response']

        print(f"\nSummary => {summary}")
        return_text=summary
    else:
        return_text=f"Request failed with status code: {response.status_code}"

    return return_text

def write_chat_log(account_no, session,ctime, su, cmessage):
    cursor = conn.cursor()
    print(f"connection in writechat {conn}")
    print(f"account {account_no} session {session} time {ctime}  su {su} message {cmessage}")
    # Do the insert
    insert_stmt= """insert into PolicyD.chat_messages (account_number, session_id,chat_time,system_or_user,chat_message) values (?,?,?,?,?)"""
    #insert_stmt=f"""insert into chat_messages (account_number, session_id,chat_time,system_or_user,chat_message) values ({int(account_no)},\"{session,}\",\"{su}\", \"{cmessage}\""""
    #commit the transaction
    #print(f"insert stmt {insert_stmt}")
    #cursor.execute(insert_stmt, int(account_no), session,ctime, su, cmessage)
    cursor.execute(insert_stmt, account_no, session,ctime, su, cmessage)
    conn.commit()

def get_session_id(full_session_id):
   
    # Split the string by "/"
    parts = full_session_id.split("/")

    # Get the last element
    last_field = parts[-1]

    return last_field 

def get_email(account_number):
    query = f"SELECT [customer_email] FROM [dbo].[customer] WHERE account_number = {account_number}"
    df = pd.read_sql(sql=query ,con=conn)
    if (df.size > 0):
        #print(f'df from query: {df}')
        email_id=df['customer_email'].iloc[0]
        print (f"email { email_id }   " )
        
    else:
        email_id="EMAIL_NOTFOUND"
   
    return email_id


def send_email(mail, email_subject,email_body, recipient):
    try:
        msg = Message(email_subject,
                      recipients=[recipient])
        msg.body = email_body
        mail.send(msg)
        return 'Email sent successfully!'
    except Exception as e:
        return str(e)
    
def send_email2(email_subject,email_body, recipients, sender, password):
    msg=MIMEText(email_body)
    msg['Subject']=email_subject
    msg['From']=sender
    msg['To']=','.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com',465)  as smtp_server:
        smtp_server.login(sender,password)
        smtp_server.sendmail(sender,recipients, msg.as_string())

        return 'Email sent successfully!'
  
import random
import smtplib
import json




from dotenv import load_dotenv, find_dotenv
import os


load_dotenv(find_dotenv())

app_pwd = os.getenv('APP_PASSWORD')
# sender = os.getenv('MAIL_USERNAME')
# email_list = json.loads(os.environ['EMAIL_LIST'])
#print(f"sender : {sender}  & pwd : {app_pwd} and email lists : {email_list}")

def generate_otp():
    """
    Create a six digit numeric OTP for verification of email
    :parms - Not argument required
    :rtypes - 6 digits numeric otp e.g. 987789
    """
    return str(random.randint(100000, 999999))

def send_email_transfer(message):
    """
    Send OTP to receiver email
    :parms - receiver email, message
    :rtypes - None
    """

    #EMAIL_LIST='[ "sujit_s@pursuitsoftware.biz",  "surbhi_d@pursuitsoftware.com"]'
    # MAIL_USERNAME=
    # MAIL_PASSWORD=

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user="policypal.otp@gmail.com", password=app_pwd)
    #curr_otp = generate_otp()
    receivers = [ "sujit_s@pursuitsoftware.biz", "sujit.sarkar@mayagic.ai", "shwetnisha_b@pursuitsoftware.biz","surbhi_d@pursuitsoftware.com"]
    body = message
    subject = "Conversation Transfer from IVR to PolicyPal"
    server.sendmail('PolicyPal ', receivers, f"Subject : {subject} \n\n{body}")
    server.quit()
    return 

import re

def remove_non_numeric(s):
    return re.sub(r'\D', '', s)
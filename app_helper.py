# For direct db Connection 
import pyodbc
import pandas as pd
from dotenv import load_dotenv, find_dotenv
import os
import datetime

# load dotenv 
load_dotenv()
#print(os.getenv('DB_SERVER'))
con_string = 'DRIVER={ODBC Driver 18 for SQL Server};'+'SERVER='+os.getenv('DB_SERVER') +';'+'Database='+os.getenv('DB_NAME') +';'+'UID='+os.getenv('DB_USERNAME') +';' +'PWD='+os.getenv('DB_PWD') +';'
#print(con_string) #for debugging only
global conn 
conn = pyodbc.connect(con_string)

 

def getAccountDetails(accountNumber):
    
    query = f"SELECT * FROM [dbo].[customer] WHERE account_number = {int(accountNumber)}"
    df = pd.read_sql(sql=query ,con=conn)
    if (df.size > 0):
        print(f'df from query: {df}')
        customer_name=df['customer_name'].iloc[0]
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

def write_chat_log(account_no, session,ctime, su, cmessage):
    cursor = conn.cursor()
    print(f"account {account_no} session {session} time {ctime}  su {su} message {cmessage}")
    # Do the insert
    insert_stmt= """insert into chat_messages (account_number, session_id,chat_time,system_or_user,chat_message) values (?,?,?,?,?)"""
    #commit the transaction
    
    cursor.execute(insert_stmt, int(account_no), session,ctime, su, cmessage)
    conn.commit()

def get_session_id(full_session_id):
   
    # Split the string by "/"
    parts = full_session_id.split("/")

    # Get the last element
    last_field = parts[-1]

    return last_field 


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
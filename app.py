from flask import Flask, request, redirect,jsonify

from twilio.twiml.messaging_response import MessagingResponse

import app_helper
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)


# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'mail.smtp2go.com'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'insurance.chat'
app.config['MAIL_PASSWORD'] = 'L8138M7kIS56P1ii'
app.config['MAIL_DEFAULT_SENDER'] = ('Insurance Chatbot', 'sujit_s@pursuitsoftware.biz')

mail = Mail(app)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()
    print(f'Body = {body}')
    # Determine the right reply for this message
    if body == 'hello':
        resp.message("Hi!")
    elif body == 'bye':
        resp.message("Goodbye")
    else:
        resp.message(f'{body}')

    return str(resp)


@app.route("/dialog/account", methods=['POST'])
def validate_account():

    user_time=datetime.now()
  
    #print (f'=============RECEVIED \n {rcvd_data}')

    json_data = request.get_json()
    #print (f'=============json data \n {json_data}')
    #print(f"========parameters {json_data['sessionInfo']['parameters']}")
    
    short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])

    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'account_number' in json_data['sessionInfo']['parameters']:
        # Extract the "account" field
        orig_account_temp =json_data['sessionInfo']['parameters']['account_number']
        print (f'Accoount Number Temp====> {orig_account_temp}')
        #Remove digits coming from phone
        orig_account_wo_Z=orig_account_temp.replace("Zdtmf_digits_", "")
        print (f'Accoount Number without z====> {orig_account_wo_Z}')
        #Add Z only for validation
        orig_account = "Z"+orig_account_wo_Z
        print (f'FINAL Accoount Number====> {orig_account}')
        
         # Create the WebhookResponse
        #check database for account number
        account_name=app_helper.getAccountDetails(orig_account)
        print (f'Account name ====> {account_name}')

        welcome_text="Welcome to the PolicyPal. Please enter your Account Number."
        #write chat_log 0
        app_helper.write_chat_log(orig_account, short_session,user_time, "S", welcome_text)

        user_time=datetime.now()
        #write chat_log 1
        app_helper.write_chat_log(orig_account, short_session,user_time, "U", orig_account_wo_Z)

        

        if (account_name=="NOTFOUND"):
            resp_account_number=None
            resp_text="Invalid Account Number"
        else:
            resp_account_number=orig_account_wo_Z
            resp_text=f"Welcome {account_name}"

        #write chat_log 2
        sys_time=datetime.now()
        app_helper.write_chat_log(orig_account,short_session ,sys_time, "S", resp_text)


        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [resp_text]
                        }
                    }
                ]
            },
            "sessionInfo":{

                
                    "session": json_data['sessionInfo']['session'],
                    "parameters": {
                        "account_name": account_name,
                        "account_number":resp_account_number
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "Account field not found"}), 400
    

@app.route("/dialog/dob", methods=['POST'])
def validate_dob():

    
    user_time=datetime.now()

    #print (f'=============RECEVIED \n {rcvd_data}')

    json_data = request.get_json()
    #print (f'=============json data \n {json_data}')

    short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])
    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'date_of_birth_yyyymmdd' in json_data['sessionInfo']['parameters']:
        # Extract the "account" field
        dob = json_data['sessionInfo']['parameters']['date_of_birth_yyyymmdd']
        print (f'DOB ====> {dob}')
        #print ( f"Y: {int(dob['year'])} M: {int(dob['month'])} D: {int(dob['day'])}" )
        orig_account = json_data['sessionInfo']['parameters']['account_number']
       
        input_month = int(dob['month'])
        input_day=int(dob['day'])
        input_year=int(dob['year'] )
        input_dob_str=f"{input_year}{input_month:02}{input_day:02}"
        print(f"INPUT DOB {input_dob_str}")

        validation_text="Please enter your Date of Birth."
        #write chat_log 0
        app_helper.write_chat_log(orig_account, short_session,user_time, "S", validation_text)

        user_time=datetime.now()
        #write chat_log 1
        app_helper.write_chat_log(orig_account, short_session,user_time, "U", input_dob_str)

        #validate account
        valid_dob=app_helper.checkDOB(orig_account,input_year,input_month, input_day)
         # Create the WebhookResponse
        if (valid_dob):
            resp_text="Your access is validated. "
            resp_dob=dob
        else:
            resp_text="Invalid Date of Birth"
            resp_dob=None

        #write chat_log 2
        sys_time=datetime.now()
        app_helper.write_chat_log(orig_account,short_session ,sys_time, "S", resp_text)   
        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"{resp_text}"]
                        }
                    }
                ]
            },
            "sessionInfo":{

                
                    "session": json_data['sessionInfo']['session'],
                    "parameters": {
                        "date_of_birth_yyyymmdd": resp_dob
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "Date of birth field not found"}), 400
    



@app.route("/dialog/policynumber", methods=['POST'])
def validate_policynumber():

    
    user_time=datetime.now()

    #print (f'=============RECEVIED \n {rcvd_data}')

    json_data = request.get_json()
    #print (f'=============json data \n {json_data}')

    short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])
    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'date_of_birth_yyyymmdd' in json_data['sessionInfo']['parameters']:
        # Extract the "Policynumber" field
        policynumber = json_data['sessionInfo']['parameters']['date_of_birth_yyyymmdd']
        print (f'policynumber ====> {policynumber}')
        #print ( f"Y: {int(dob['year'])} M: {int(dob['month'])} D: {int(dob['day'])}" )

        #orig_account = json_data['sessionInfo']['parameters']['account_number']
         # Extract the "account" field
        orig_account_wo_Z = json_data['sessionInfo']['parameters']['account_number']

        #Add Z only for validation
        orig_account = "Z"+orig_account_wo_Z
       

        validation_text="Please enter your Policy Number."
        #write chat_log 0
        app_helper.write_chat_log(orig_account, short_session,user_time, "S", validation_text)

        user_time=datetime.now()
        #write chat_log 1
        app_helper.write_chat_log(orig_account, short_session,user_time, "U", policynumber)

        #validate account
        valid_dob=app_helper.checkPolicyNumber(orig_account,policynumber)
         # Create the WebhookResponse
        if (valid_dob):
            resp_text="Your access is validated. "
            resp_dob=policynumber
        else:
            resp_text="Invalid PolicyNumber"
            resp_dob=None

        #write chat_log 2
        sys_time=datetime.now()
        app_helper.write_chat_log(orig_account,short_session ,sys_time, "S", resp_text)   
        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"{resp_text}"]
                        }
                    }
                ]
            },
            "sessionInfo":{

                
                    "session": json_data['sessionInfo']['session'],
                    "parameters": {
                        "date_of_birth_yyyymmdd": resp_dob
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "PolicyNumberfield not found"}), 400
    


@app.route("/dialog/llm", methods=['POST'])
def call_llm():
        
    user_time=datetime.now()
    #rcvd_data= request.data
    #print (f'=============RECEVIED \n {rcvd_data}')

 
    #print (f'=============json data \n {json_data}')
    #print(f"========parameters {json_data['sessionInfo']['parameters']}")
    # Check if the required field exists in the JSON data

    json_data = request.get_json()
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'prompt_to_llm' in json_data['sessionInfo']['parameters']:
        # Extract the "llm" field
        prompt_llm = json_data['sessionInfo']['parameters']['prompt_to_llm']
        print (f'LLM prompt ====> {prompt_llm}')
        short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])
      
        #write chat_log 1
        # Extract the "account" field
        orig_account_wo_Z = json_data['sessionInfo']['parameters']['account_number']

        #Add Z only for validation
        orig_account = "Z"+orig_account_wo_Z

        app_helper.write_chat_log(orig_account, short_session,user_time, "U", prompt_llm)
        print (f'LLM prompt ====> {prompt_llm}')
        
        #Call llm API
        llm_response=app_helper.call_llm(orig_account,prompt_llm)
        #Strip new lines
        resp_text=llm_response.replace('\n', ' ')
        print(f"=========> resp_text = {resp_text}")
        #write chat_log 2
        sys_time=datetime.now()
        app_helper.write_chat_log(orig_account,short_session ,sys_time, "S", resp_text)   

         # Create the WebhookResponse
     
        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [resp_text]
                        }
                    }
                ]
            },
                     "sessionInfo":{

                
                    "session": json_data['sessionInfo']['session'],
                    "parameters": {
                        "prompt_to_llm": None
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "prompt_llm not found"}), 400   


@app.route("/dialog/transfer", methods=['POST'])
def transfer_chat():

    rcvd_data= request.data
    print (f'=============RECEVIED \n {rcvd_data}')

    json_data = request.get_json()
    print (f'=============json data \n {json_data}')
    print(f"========parameters {json_data['sessionInfo']['parameters']}")
    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'prompt_to_llm' in json_data['sessionInfo']['parameters']:
        # Extract the "llm" field
        prompt_llm = json_data['sessionInfo']['parameters']['prompt_to_llm']
        print (f'Transfer to chat {prompt_llm}')

        base_url="https://insurancenlq.azurewebsites.net/loadchat"
        short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])
        orig_account = int(json_data['sessionInfo']['parameters']['account_number'])
        url = f"{base_url}/{orig_account}/{short_session}"
        email_body=f"Click on {url} to go to continue your conversation in the Insurance Chatbot "
        print(f"email body => {email_body}")
        email_id=app_helper.get_email(orig_account)
        print(f"email to => {email_id}")
        app_helper.send_email(mail,"Transfering session to chat",email_body,email_id)

         # Create the WebhookResponse
     
        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"Please check your email to see instructions to transfer your current conversation to Insurance chatbot"]
                        }
                    }
                ]
            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "prompt_llm not found"}), 400   


@app.route('/send-email')
def send_email():
    
    ret_msg=app_helper.send_email(mail,"Hello from Flaskmail","This is test email from Flask email","sujit2050@yahoo.com")
   
    return str(ret_msg)



if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, redirect,jsonify

from twilio.twiml.messaging_response import MessagingResponse

import app_helper

app = Flask(__name__)

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

    rcvd_data= request.data
    print (f'=============RECEVIED \n {rcvd_data}')

    json_data = request.get_json()
    print (f'=============json data \n {json_data}')
    print(f"========parameters {json_data['sessionInfo']['parameters']}")
    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'account_number' in json_data['sessionInfo']['parameters']:
        # Extract the "account" field
        orig_account = json_data['sessionInfo']['parameters']['account_number']
        print (f'Accoount ====> {orig_account}')
        #return jsonify({"account": account}), 200
         # Create the WebhookResponse
        #check database for account number
        account_name=app_helper.getAccountDetails(orig_account)
        print (f'Accoount name ====> {account_name}')
        if (account_name=="NOTFOUND"):
            resp_account_number=None
        else:
            resp_account_number=orig_account

        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"The account name for {orig_account} is {account_name}"]
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

    rcvd_data= request.data
    print (f'=============RECEVIED \n {rcvd_data}')

    json_data = request.get_json()
    print (f'=============json data \n {json_data}')
    print(f"========parameters {json_data['sessionInfo']['parameters']}")
    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'date_of_birth_yyyymmdd' in json_data['sessionInfo']['parameters']:
        # Extract the "account" field
        dob = json_data['sessionInfo']['parameters']['date_of_birth_yyyymmdd']
        print (f'DOB ====> {dob}')
        
         # Create the WebhookResponse
      
        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"The date of birth for is {dob}"]
                        }
                    }
                ]
            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "Date of birth field not found"}), 400
    


@app.route("/dialog/llm", methods=['POST'])
def call_llm():

    rcvd_data= request.data
    print (f'=============RECEVIED \n {rcvd_data}')

    json_data = request.get_json()
    print (f'=============json data \n {json_data}')
    print(f"========parameters {json_data['sessionInfo']['parameters']}")
    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'prompt_to_llm' in json_data['sessionInfo']['parameters']:
        # Extract the "llm" field
        prompt_llm = json_data['sessionInfo']['parameters']['prompt_to_llm']
        print (f'LLM prompt ====> {prompt_llm}')
        
         # Create the WebhookResponse
     
        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"The llm prompt is {prompt_llm}"]
                        }
                    }
                ]
            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "prompt_llm not found"}), 400   

if __name__ == "__main__":
    app.run(debug=True)

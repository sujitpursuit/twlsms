from flask import Flask, request, redirect,jsonify

from twilio.twiml.messaging_response import MessagingResponse

import app_helper
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)


# """ # Configure Flask-Mail
# app.config['MAIL_SERVER'] = 'mail.smtp2go.com'
# app.config['MAIL_PORT'] = 2525
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = 'insurance.chat'
# app.config['MAIL_PASSWORD'] = 'L8138M7kIS56P1ii'
# app.config['MAIL_DEFAULT_SENDER'] = ('Insurance Chatbot', 'sujit_s@pursuitsoftware.biz')

# mail = Mail(app) """


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
        print (f'Accoount Number received====> {orig_account_temp}')
        orig_account_wo_Z=app_helper.remove_non_numeric(str(orig_account_temp))

        print (f'Accoount Number with only numeric chars====> {orig_account_wo_Z}')
        #Remove digits coming from phone
        #orig_account_wo_Z=orig_account_temp.replace("dtmf_digits_", "")
        #print (f'Accoount Number without z====> {orig_account_wo_Z}')
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
        policynumber_temp = json_data['sessionInfo']['parameters']['date_of_birth_yyyymmdd']
        print (f'Policy Number received====> {policynumber_temp}')

      
        policynumber= app_helper.remove_non_numeric(str(policynumber_temp))
      
        print (f'Policy Number with only numeric characters====> {policynumber}')

        #Remove dtmfdigits coming from phone
        #policynumber=policynumber_temp.replace("dtmf_digits_", "")
       
        #print (f'policynumber ====> {policynumber}')
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
            resp_text="Your Policy Number is validated. "
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
    


####NEW FUNCTION
@app.route("/dialog/otp", methods=['POST'])
def validate_otp():

    
    user_time=datetime.now()

    #print (f'=============RECEVIED \n {rcvd_data}')

    json_data = request.get_json()
    #print (f'=============json data \n {json_data}')

    short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])
    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'otp' in json_data['sessionInfo']['parameters']:
        # Extract the "OTP" field


        otp_temp = json_data['sessionInfo']['parameters']['otp']
        print (f'otp Received====> {otp_temp}')
        otp_temp=str(otp_temp).replace(" ","")
        otp=app_helper.remove_non_numeric(str(otp_temp))
        print (f'otp after non numeric removal====> {otp}')
        #Remove digits coming from phone
        #otp=otp_temp.replace("dtmf_digits_", "")
       
        #print (f'otp ====> {otp}')
        #print ( f"Y: {int(dob['year'])} M: {int(dob['month'])} D: {int(dob['day'])}" )

        #orig_account = json_data['sessionInfo']['parameters']['account_number']
         # Extract the "account" field
        orig_account_wo_Z = json_data['sessionInfo']['parameters']['account_number']

        #Add Z only for validation
        orig_account = "Z"+orig_account_wo_Z
       

        validation_text="Please enter OTP."
        #write chat_log 0
        app_helper.write_chat_log(orig_account, short_session,user_time, "S", validation_text)

        user_time=datetime.now()
        #write chat_log 1
        app_helper.write_chat_log(orig_account, short_session,user_time, "U", otp)

        otp_sent= "667788"
        #validate OTP
        valid_otp=app_helper.check_otp(otp, otp_sent)
        print(f"OTP Validation result : {valid_otp}")
         # Create the WebhookResponse
        if (valid_otp):
            resp_text="Your OTP is validated. "
            resp_otp=otp
        else:
            resp_text="Invalid OTP"
            resp_otp=None

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
                        "otp": resp_otp
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "OTP invalid "}), 400
    


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
        
        account_name=json_data['sessionInfo']['parameters']['account_name']
        policy_number=json_data['sessionInfo']['parameters']['date_of_birth_yyyymmdd']
        #Call llm API
        llm_response=app_helper.call_llm(short_session,orig_account,account_name,policy_number,prompt_llm)
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

       #base_url="https://insurancenlq.azurewebsites.net/loadchat"
        base_url="https://app-chatbotinsurance-ui-uat.azurewebsites.net/loadchat"#/10002/865717-cef-d5b-708-efdf157d9"
        short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])

           #write chat_log 1
        # Extract the "account" field
        orig_account_wo_Z = json_data['sessionInfo']['parameters']['account_number']

        #Add Z only for validation
        orig_account = "Z"+orig_account_wo_Z
        
        url = f"{base_url}/{orig_account}/{short_session}"
        email_body=f"\n\nWelcome from Hastings IVR!\n\n\nPlease click on {url} to go to continue your conversation in the Insurance Chatbot PolicyPal. \n\n"
        print(f"email body => {email_body}")
        email_subject="Conversation Transfer from IVR to PolicyPal"
        app_helper.send_email_transfer(email_body, email_subject)
        #email_id=app_helper.get_email(orig_account)
        #email_id="sujit2050@yahoo.com"
        #print(f"email to => {email_id}")

        #app_helper.send_email2("Transfering session to chat",email_body, ["sujit2050@yahoo.com"], "policypal.otp@gmail.com", "wwtn qrfj mmjk gagm")
        #app_helper.send_email(mail,"Transfering session to chat", email_body,"sujit.sarkar@mayagic.ai")
        #app_helper.send_email(mail,"Transfering session to chat", email_body,"sujit2050@yahoo.com")
        #app_helper.send_email(mail,"Transfering session to chat",email_body,email_id)

         # Create the WebhookResponse
     
        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"Please check your email to see instructions to transfer your current conversation to Policy Pal"]
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
    
    #ret_msg=app_helper.send_email(mail,"Hello from Flaskmail","This is test email from Flask email","sujit.sarkar@Mayagic.ai")
    ret_msg=app_helper.send_email2("Transfer from PolicyPal","This is test email from Flask smtp mail", ["sujit2050@yahoo.com","sujit_s@pursuitsoftware.biz"], "policypal.otp@gmail.com", "wwtn qrfj mmjk gagm")
    return str(ret_msg)


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
    


####################### MEDICAL APPOINTMENT IVR****************************#
import re
@app.route("/dialog/clinic/validate/patient", methods=['POST'])
def validate_patient():

    
    json_data = request.get_json()
    #print (f'=============json data \n {json_data}')

    short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])
    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'patient_dob' in json_data['sessionInfo']['parameters']:
        # Extract the  field
        patient_dob = json_data['sessionInfo']['parameters']['patient_dob']
        print (f'patient_dob received====> {patient_dob}')
        patient_last_name=json_data['sessionInfo']['parameters']['patient_last_name']
        print (f'patient_last_name received====> {patient_last_name}')
        #remove non alphabets (.)
        patient_last_name=re.sub(r'[^a-zA-Z]', '', patient_last_name)
        print (f'patient_last_name after cleaning====> {patient_last_name}')

        validation_text="Please enter your date of borth."
      
        #validate account
        valid_patient=app_helper.checkPatientDetails(patient_last_name,patient_dob)
         # Create the WebhookResponse
        if (valid_patient):
            resp_text="Your record has been found"
            resp_dob=patient_dob
            resp_patient_last_name=patient_last_name
        else:
            resp_text="Unable to find your details"
            resp_dob=None
            resp_patient_last_name=None
            
  
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
                        "patient_dob": resp_dob,
                        "patient_last_name":resp_patient_last_name
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "Patient record not found"}), 400



@app.route("/dialog/clinic/validate/doctor", methods=['POST'])
def validate_doctor():

    
    json_data = request.get_json()
    #print (f'=============json data \n {json_data}')

    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'doctor_name' in json_data['sessionInfo']['parameters']:
        # Extract the  field
        global doctor_name
        doctor_name = json_data['sessionInfo']['parameters']['doctor_name']
        print (f'doctor_name received====> {doctor_name}')
          #remove non alphabets (.)
        doctor_name=re.sub(r'[^a-zA-Z\s]', '', doctor_name)
        print (f'doctor_name after cleaning====> {doctor_name}')
        global doctor_id

        cleaned_name = doctor_name.replace("Dr.", "").replace("Dr", "").replace("Doctor", "").strip()
        try:
            doctor_id=app_helper.checkDoctor(cleaned_name)
            # Create the WebhookResponse
            if (doctor_id != None):
                resp_text=f"Doctor {cleaned_name} available for appointments"
                resp_doctor_name=doctor_name
            else:
                resp_text=f"Unable to find Doctor {cleaned_name} details"
                resp_doctor_name=None

        except:
            resp_text=f"Error while fetching {doctor_name} details"
            resp_doctor_name=None

    
       
            
            
  
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
                        "doctor_name": resp_doctor_name,
                     
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "Patient record not found"}), 400



@app.route("/dialog/clinic/llm/slots", methods=['POST'])
def call_clinic_llm_slots():
  
  

    json_data = request.get_json()
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'slot_query' in json_data['sessionInfo']['parameters']:
        # Extract the "llm" field
        slot_query = json_data['sessionInfo']['parameters']['slot_query']
        print (f'calling LLM for doctor_id {doctor_id} with prompt {slot_query}')
        
        llm_response=app_helper.get_doctor_slots( doctor_id,slot_query)
        #Strip new lines
        if llm_response=="NO_SLOT_FOUND":
            resp_text="No Slots Found for Doctor"
            slot_query_resp=None
        else:
            resp_text=llm_response.replace('\n', ' ')
            resp_text=llm_response.replace('*', ' ')
            slot_query_resp=resp_text

        global slots_available 
        slots_available=resp_text

        print(f"=========> resp_text = {resp_text}")
       
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
                        "slot_query":slot_query_resp,
                        "slot_query_answered": "True"
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "slot_query not found"}), 400  


@app.route("/dialog/clinic/llm/seletedslot", methods=['POST'])
def call_clinic_llm_select_slot():
  
  

    json_data = request.get_json()
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'selected_slot' in json_data['sessionInfo']['parameters']:
        # Extract the "llm" field
        selected_slot = json_data['sessionInfo']['parameters']['selected_slot']
        print (f'calling LLM for doctor_id {doctor_id} with prompt {selected_slot}')
        
        #Check if selected slot in the slot provided
        #Step 1: Convert to startdate, starttime format from LLM call
        #Atep 2: 
        #TODO 
        llm_response=app_helper.get_doctor_slots( doctor_id,selected_slot)
        #Strip new lines
        resp_text=llm_response.replace('\n', ' ')
        resp_text=llm_response.replace('\n', ' ')
        print(f"=========> resp_text = {resp_text}")

        #Temporary
        resp_text=f"Your appointment with  {doctor_name} has been booked for {selected_slot}"
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
                        "selected_slot_booked": "True"
                    }         

            }
        }
        app_helper.send_email_patient(resp_text)
        return jsonify(response)
    else:
        return jsonify({"error": "selected_slot not found"}), 400  


####################### END MEDICAL APPOINTMENT IVR****************************#




########SPANISH CHATBOT ##################################


@app.route("/dialog/egov/validate/person_id_number", methods=['POST'])
def validate_person_id_number():

    user_time=datetime.now()
    json_data = request.get_json()
    #print (f'=============json data \n {json_data}')


    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'person_id_number' in json_data['sessionInfo']['parameters']:
        # Extract the  field
       


        person_id_number_rcvd = json_data['sessionInfo']['parameters']['person_id_number']
        print (f'person_id_number received====> {person_id_number_rcvd}')

        global person_id_number   
        person_id_number= str(int(float(person_id_number_rcvd)))
        print (f'person_id_number converted====> {person_id_number}')

        #Write chatlog
        short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])
        welcome_text="Ingrese el número de identificación de la persona"
        #write chat_log 1
        app_helper.write_chat_log_spanish(person_id_number, short_session,user_time, "S", welcome_text)

        user_time=datetime.now()
        #write chat_log 2
        app_helper.write_chat_log_spanish(person_id_number, short_session,user_time, "U", person_id_number)

        try:
            return_status=app_helper.check_document_number(person_id_number)
            # Create the WebhookResponse
            if (return_status == "success"):
                resp_text=f"La persona {person_id_number} está validada"
                resp_person_id_number=person_id_number
            else:
                resp_text=f"No se puede encontrar la persona con el número {person_id_number} "
                resp_person_id_number=None


        except Exception as e:
            resp_text=f"Error al obtener la persona con número {person_id_number}: {e} "
            resp_person_id_number=None

        #Write chatlog
        user_time=datetime.now()
        #write chat_log 3
        app_helper.write_chat_log_spanish(person_id_number, short_session,user_time, "U", resp_text)

  
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
                        "person_id_number": resp_person_id_number ,
                     
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "Person ID Number not found"}), 400



@app.route("/dialog/egov/validate/login_pin", methods=['POST'])
def validate_personal_pin():

    user_time=datetime.now()

    json_data = request.get_json()
    #print (f'=============json data \n {json_data}')

    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'personal_pin' in json_data['sessionInfo']['parameters']:
        # Extract the  field
       
        personal_pin_rcvd = json_data['sessionInfo']['parameters']['personal_pin']
        print (f'person_id_number received====> {personal_pin_rcvd}')

        person_pin   = personal_pin_rcvd# str(int(float(person_id_number_rcvd)))
        #print (f'person_id_number converted====> {person_id_number}')

         #Write chatlog
        short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])
        askpin_text="Introduzca su PIN de acceso"
        #write chat_log 1
        app_helper.write_chat_log_spanish(person_id_number, short_session,user_time, "S", askpin_text)

        user_time=datetime.now()
        #write chat_log 2
        app_helper.write_chat_log_spanish(person_id_number, short_session,user_time, "U", person_pin)

        try:
            return_status=app_helper.check_personal_pin(person_id_number,person_pin)
            # Create the WebhookResponse
            if (return_status == "success"):
                resp_text="PIN de inicio de sesión validado"
                resp_person_pin=person_pin
            else:
                resp_text=f"PIN de inicio de sesión no válido"
                resp_person_pin=None


        except Exception as e:
            resp_text=f"Error in validating Login pin: {e} "
            resp_person_pin=None

        #Write chatlog
        user_time=datetime.now()
        #write chat_log 3
        app_helper.write_chat_log_spanish(person_id_number, short_session,user_time, "S", resp_text)
  
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
                        "personal_pin": resp_person_pin ,
                     
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "PIN  not found in requet"}), 400




@app.route("/dialog/egov/llm/get_llm_response", methods=['POST'])
def call_spanish_llm():
  
  
    user_prompt_answered=False
    json_data = request.get_json()
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'user_prompt' in json_data['sessionInfo']['parameters']:
        # Extract the "llm" field
        user_prompt = json_data['sessionInfo']['parameters']['user_prompt']
        print (f'calling LLM for personal ID Number{person_id_number} with prompt {user_prompt}')
        

        short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])
        user_time=datetime.now()
        #write chat_log 2
        app_helper.write_chat_log_spanish(person_id_number, short_session,user_time, "U", user_prompt)


        llm_response=app_helper.get_user_prompt_response( person_id_number,user_prompt)
        #Strip new lines
        if "Error" in llm_response:
            resp_text=llm_response
            user_prompt_resp=None
        else:
            resp_text=llm_response.replace('\n', ' ')
            resp_text=llm_response.replace('*', ' ')
            user_prompt_resp=None  # To reprompt
            user_prompt_answered=True 

       
        user_time=datetime.now()
        #write chat_log 2
        app_helper.write_chat_log_spanish(person_id_number, short_session,user_time, "S", resp_text)
        print(f"=========> egov llm resp_text = {resp_text}")
       
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
                        "user_prompt":user_prompt_resp,
                        "user_prompt_answered": user_prompt_answered
                    }         

            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "user_prompt not found in request"}), 400  




@app.route("/dialog/egov/llm/transfer", methods=['POST'])
def transfer_spanish_chat():

    rcvd_data= request.data
    #print (f'=============RECEVIED \n {rcvd_data}')

    json_data = request.get_json()
    print (f'=============json data \n {json_data}')
    #print(f"========parameters {json_data['sessionInfo']['parameters']}")
    # Check if the required field exists in the JSON data
    if 'sessionInfo' in json_data and 'parameters' in json_data['sessionInfo'] and 'user_prompt' in json_data['sessionInfo']['parameters']:
        # Extract the "llm" field
        prompt_llm = json_data['sessionInfo']['parameters']['user_prompt']
        print (f'Transfer to chat {prompt_llm}')

        base_url="https://app-spanishchatbot-api-dev.azurewebsites.net/api/v1/loadchat"
      
        short_session=app_helper.get_session_id(json_data['sessionInfo']['session'])

        
        
        url = f"{base_url}/{person_id_number}/{short_session}"
        email_body=f"\n\nWelcome from Spanish IVR Chatbot!\n\n\nPlease click on {url} to go to continue your conversation in Query Pal. \n\n"
        print(f"email body => {email_body}")
        email_subject="Conversation Transfer from IVR to Query Pal"
        app_helper.send_email_transfer(email_body, email_subject)
        
       

         # Create the WebhookResponse
     
        response = {
            "fulfillment_response": {
                "messages": [
                    {
                        "text": {
                            "text": [f"Por favor revise su correo electrónico para ver las instrucciones para transferir su conversación actual a Query Pal"]
                        }
                    }
                ]
            }
        }

        return jsonify(response)
    else:
        return jsonify({"error": "user_prompt not found"}), 400   


######## END SPANISH CHATBOT ##################################

if __name__ == "__main__":
    app.run(debug=True)

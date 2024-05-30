from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

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


@app.route("/dilog", methods=['POST'])
def incoming_dilog():

    rcvd_data= request.data
    print (f'=============RECEVIED \n {rcvd_data}')

if __name__ == "__main__":
    app.run(debug=True)

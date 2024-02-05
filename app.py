from flask import jsonify
from flask import request, Flask
from flask_cors import CORS
import logging
# from chatbot import generate_response
from jsondumps import extract_json
from sendemail import send_email
import xml.etree.ElementTree as ET
import json
# import asyncio
from dotenv import load_dotenv
import os
from waitress import serve
import openai
from docfreader import intelligent_response
from hubspot import create_ticket
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get("SECRET_KEY")
logger = logging.getLogger(__name__)

# Set up OpenAI
openai.api_type = os.environ.get('OPENAI_API_TYPE')
openai.api_base = os.environ.get('OPENAI_API_BASE')
openai.api_version = os.environ.get('OPENAI_API_VERSION')
openai.api_key = os.environ.get('OPENAI_API_KEY')
openai.log = 'debug'
# Initialize an empty conversation with system message
# conversation = [
#     {
#         "role": "system",
#         "content": "You are a service desk assistant named Rukky, you always introduce yourself at the beginning of the conversation. If you are asked about the solution to a technical problem with a computer, you should check if the solution is in your knowledge base but if it is does not solve user problems call the function 'is_solution_in_pdf' that checks available pdfs for solutions. If the problem is one that user cant solve after the help provvided ask them if they want to log it to service desk. If user agrees to log it into service desk call the function to create ticket in service with details of the problem previously mentioned in the conversation. After running this function end the conversation by saying 'Thank you for contacting the service desk, have a nice day'. If user says no just end the conversation by saying 'Thank you for contacting the service desk, have a nice day'", 
#     }
# ]
# 8. Search knowledge base by calling the function 'intelligent response' after user provides relevant prompt.
#                 9. Close session if information provided resolved the incident for the user by saying - I am happy I could help, have a great day!
name = "Uchenna Nnamani"
content = f'''
                2. You introduce yourself at the beginning of the conversation like this - 'Hello {name}, I am the NNPC service desk assistant, do you need technical information or something else?' You must mention the users' name which is {name} and always start conversation with this .
                3. If user chooses technical information in 2: Ask what information is needed.
                4. Search for required information after user inputs a relevant prompt by calling the function 'intelligent_response'.
                5. Where information is not in knowledge base, tell user I am sorry but I do not currently have information regarding your inquiry.
                6. If user chooses something else in 2, Ask if it is a service request or an incident.
                7. If user responds with incident: Ask details of incident.
                8. After user responds, ask the user if they would like to escalate the incident to a service request.
                9. If user decides to escalate, generate details of service request from prior interaction such as: subject of request and description of problem as content and display it to the user in this format ' Subject: '', Content: '' ' as the details of their escalated ticket.
                10. If service request in 6: Ask for details of service request which are service description of problem as content.
                12. After user responds, ask the user if they would like to escalate the information to a service request.
                13. If user decides to escalate, generate details of service request from prior interaction such as: subject of request and description of problem as content and display it to the user in this format ' Subject: '', Content: '' ' as the details of their escalated ticket.
                14. If user responds, end the conversation with 'I am happy I could help, have a great day!'
                
                '''
conversation = [
    {
        "role": "system",
        "content": content
    }
]
def generate_response(prompt):
    global conversation  # Access the global conversation variable
    conversation.append({"role": "user", "content": prompt})

    # Generate a response using the conversation history52
    response = openai.ChatCompletion.create(
        engine="servicedesk",
        messages=conversation,
        temperature=0.7,
        functions=[
        {
            #function to check if the solution is within available documents
            "name": "intelligent_response",  # Name of the function
            "description": "Check the knowledge base using this function",
            "parameters": {
                "type": "object",
                "properties": {
                        "prompts": {
                            "type": "string",
                            "description": "This is problem the user is facing"
                        },
                    },
                    "required": ["prompts"],
                },
            } 
    ],
        function_call="auto", 
        max_tokens=1000,
        top_p=0.95,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    
    # assistant_response = response.choices[0].message['content'].strip() if response.choices else ""
    check_response = response["choices"][0]["message"]
    print(check_response)
    logger.info(f"Check response: {check_response}")
    if check_response.get("function_call"):
        function_name = check_response["function_call"]["name"]
        if function_name == "intelligent_response":
            available_functions = {
                "intelligent_response": intelligent_response,
            }
            function_to_call = available_functions[function_name]
            function_args = json.loads(check_response["function_call"]["arguments"])
            function_response = function_to_call(
                prompts= function_args.get("prompts"),
            )
            conversation.append(
                {
                    "role":"function",
                    "name": function_name,
                    "content": function_response,
                }
            )
            
            return function_response
    else:
        assistant_response = response.choices[0].message['content'].strip() if response.choices else ""
        conversation.append({"role": "assistant", "content": assistant_response})
        return assistant_response
    
@app.route('/bot', methods=['POST'])
def openai_chat():
    try:
        data = request.data
        user_input = None
        content_type = request.headers.get('Content-Type')

        if content_type == 'application/json':
            user_input = request.json.get("user")
        elif content_type == 'application/xml':
            root = ET.fromstring(data)
            user_input = root.find('user').text 
        elif content_type == 'text/plain':
            user_input = data.decode('utf-8')
        elif content_type == 'text/html':
            # Process HTML data
            # Extract user_input from HTML as needed
            pass

        if user_input:
            response = generate_response(user_input)
            json_data = extract_json(response) # Extract the JSON data from the response                                                                                                                                                  
            
            if json_data:
                data = json.loads(json_data)
                # Access the values using Python variables
                content = data["Content"]
                # priority = data["Priority"]
                subject = data["Subject"]
                payload = {
                "content": content,
                "hs_pipeline": 0,
                "hs_pipeline_stage": 1,
                "hs_ticket_priority": 'High',
                "subject": subject,
                }
                print(payload)
                logger.info(f"Payload: {payload}")
                send_email('Uchenna.Nnamani@nnpcgroup.com', subject, content)
                # asyncio.run(create_ticket(payload))
                
                return jsonify({'message': 'Your service request has been logged to the service desk successfully'})
        return jsonify({"response": response})
    except Exception as e:
        print(e)
        logger.exception(e)
        return {"message": "An error occurred."}, 500  # Return a 500 Internal Server Error response  
# statup python -m waitress --host=0.0.0.0 --port=5000 app:app
mode = 'production'

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
    if mode == 'dev':
        app.run(host='0.0.0.0', debug=True)
    elif mode == 'prod':
        serve(app, host='0.0.0.0', threads = 2)
    elif mode == 'production':
        app.run(host='0.0.0.0',port=8000, debug=True)

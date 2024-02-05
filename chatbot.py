from flask import   Flask
import openai
from jsondumps import extract_json
from docfreader import intelligent_response
import os
from dotenv import load_dotenv
import json

app = Flask(__name__)
# app.secret_key = "mynameisslimshady"

load_dotenv()

# Set up OpenAI
openai.api_type = os.environ.get('OPENAI_API_TYPE')
openai.api_base = os.environ.get('OPENAI_API_BASE')
openai.api_version = os.environ.get('OPENAI_API_VERSION')
openai.api_key = os.environ.get('OPENAI_API_KEY')

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
                2. You introduce yourself at the beginning of the conversation like this - 'Hello {name}, I am the NNPC service desk assistant, do you need technical information or something else?' You must mention the users' name which is {name}.
                3. If user chooses technical information in 2: Ask what information is needed.
                4. Search for required information after user inputs a relevant prompt by calling the function 'intelligent_response'.
                5. Where information is not in knowledge base, tell user I am sorry but I do not currently have information regarding your inquiry.
                6. If user chooses something else in 2, Ask if it is a service request or an incident.
                7. If user responds with incident: Ask details of incident.
                8. Ask the user if they would like to escalate the incident to a service request.
                9. If user decides to escalate, generate details of service request from prior interaction such as: subject of request and description of problem as content.
                10. Display the ticket information to user in this format 'your service request has been logged, these are the details subject:'', content:'',' then call the service_request function using these variables
                11. If service request in 6: Ask for details of service request which are service description of problem as content.
                12. After user inputs, check if service request can be solved using knowledge base by calling the function 'intelligent_response'.
                13. If the request cannot be solved, generate details of service request from the prior interaction such as: subject of request and description of problem as content.
                14. Display the ticket information to user in this format 'your service request has been logged, these are the details subject:'', content:'',' then call the service_request function using these variables
                15. If user responds, end the conversation with 'I am happy I could help, have a great day!'
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
            
            # "name": "service_request",  # Name of the function
            # "description": "Log the problem in the service desk",
            # "parameters": {
            #     "type": "object",
            #     "properties": {
            #             "staff_name": {
            #                 "type": "string",
            #                 "description": "This is the staff name"
            #             },
            #             "staff_email": {
            #                 "type": "string",
            #                 "description": "This is the staff email"
            #             },
            #             "complaint": {
            #                 "type": "string",
            #                 "description": "This is problem the user is facing that will be logged into the service desk"
            #             },
            #         },
            #         "required": ["complaint", "staff_name", "staff_email"],
            #     },
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
        # elif function_name == "service_request":
        #     # available_functions = {
        #     #     "service_request": extract_json,
        #     # }
        #     # function_to_call = available_functions[function_name]
        #     # function_args = json.loads(check_response["function_call"]["arguments"])
        #     # function_response = function_to_call(
        #     #     fullname= function_args.get(""),
        #     # )
        #     # conversation.append(
        #     #     {
        #     #         "role":"function",
        #     #         "name": function_name,
        #     #         "content": function_response,
        #     #     }
        #     # )
        #     # # Extract relevant information from the function response
        #     # available_times = json.loads(function_response)

        #     # assistant_message = {
        #     # "role": "assistant",
        #     # "content": f"I have the following times available for {function_args.get('fullname')} which are {available_times}"
        #     # }
            
        #     # # Append the assistant message to the conversation
        #     # conversation.append(assistant_message)
        #     # # assistant_response = response.choices[0].message['content'].strip() if response.choices else ""
        #     # finetune =  intelligent_response(function_response)
        #     return "module not available"
    else:
        assistant_response = response.choices[0].message['content'].strip() if response.choices else ""
        conversation.append({"role": "assistant", "content": assistant_response})
        return assistant_response
    
# @app.route('/openai_chat', methods=['POST'])
# def openai_chat():
#     try:
#         data = request.json
#         user_input = data["user"]
#         response = generate_response(user_input,"nnamaniuchenna8@gmail.com")
#         return jsonify({"response": response})
#     except Exception as e:
#         return jsonify({"error": str(e)})

# if __name__ == '__main__':
#     app.run(debug=True)



from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv
import os
import openai
import json

load_dotenv()

openai.api_type = os.environ.get('OPENAI_API_TYPE')
openai.api_base = os.environ.get('OPENAI_API_BASE')
openai.api_version = os.environ.get('OPENAI_API_VERSION')
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Set up Azure Cognitive Search credentials
service_name = os.environ.get('SERVICE_NAME')
index_name = os.environ.get('INDEX_NAME')
api_key = os.environ.get('SERVICE_KEY')
endpoint = "https://{0}.search.windows.net/".format(service_name)
credential = AzureKeyCredential(api_key)
client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

def search_documents(technical_issue):
    # Execute search query
    result = client.search(search_text=technical_issue)

    # Process search results
    for i, document in enumerate(result):
        # Access extracted information from the document
        output = document['content']
        if i == 0:
            break
    return json.dumps(output)
# # Example usage
def intelligent_response(prompts):
    response = openai.ChatCompletion.create(
        engine="servicedesk",
        messages=[
            {"role": "system", 
            "content": "You help determine if a prompt you get concerns technical helpdesk issues or not. If it concerns technical helpdesk issues you will run the function search_document else you will tell the user something related to 'please could you provide a valid technical inquiry'."},
            {"role": "user", "content": prompts}
        ],
        temperature=0.7,
        functions=[
        {
            #function to check if the person is in the company
            "name": "search_documents",  # Name of the function
            "description": "Check through document to provide solution to technical helpdesk problems only if prompt is a technical problem or contains nnpc",
            "parameters": {
                "type": "object",
                "properties": {
                        "technical_issue": {
                            "type": "string",
                            "description": "This is concise technical issue the user is facing"
                        },
                    },
                    "required": ["technical_issue"],
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
    
    # if response.choices and response.choices[0].message['content']:
    #     message = response.choices[0].message['content'].strip()
    #     print(message)
    check_response = response["choices"][0]["message"]
    # print(check_response)
    if check_response.get("function_call"):
        function_name = check_response["function_call"]["name"]
        if function_name == "search_documents":
            available_functions = {
                "search_documents": search_documents,
            }
            function_to_call = available_functions[function_name]
            function_args = json.loads(check_response["function_call"]["arguments"])
            function_response = function_to_call(
                technical_issue= function_args.get("technical_issue"),
            )
            
            final_response = finetune(function_response)
            # print(final_response)
            return final_response
    else:
        assistant_response = response.choices[0].message['content'].strip() if response.choices else ""
        # print(assistant_response)
        return assistant_response
    
def finetune(prompt):
    response = openai.ChatCompletion.create(
        engine="servicedesk",
        messages=[
            {"role": "system", 
            "content": "You make the prompt more concise, human friendly and exclude quotation marks"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    
    if response.choices and response.choices[0].message['content']:
        message = response.choices[0].message['content'].strip()
        return message
    
# query = "how do i fix my keyboard buttons"
# intelligent_response(query)


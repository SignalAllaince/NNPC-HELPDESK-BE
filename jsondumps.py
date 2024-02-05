import re
import json

def extract_json(input_text):
    # Define regular expressions to extract information
    patterns = {
        "Content": r"Content: (.*?)(?:,|$)",
        # "Priority": r"Priority: (.*?)(?:|$)",
        "Subject": r"Subject: (.*?)(?:$)"
    }

    # Initialize a dictionary to store the extracted information
    result = {}

    # Extract information using regular expressions
    for key, pattern in patterns.items():
        matches = re.findall(pattern, input_text, re.MULTILINE| re.IGNORECASE)
        if matches:
            # Use the last match as it's the most recent one
            value = matches[-1].strip()
            if value and not value.isspace():
                result[key] = value
            else:
                # If any field is empty or only spaces, return an empty JSON
                return {}

    # Check if all fields were extracted successfully
    if len(result) == len(patterns):
        # Convert the result dictionary to JSON format
        json_result = json.dumps(result, indent=4)
        return json_result
    else:
        # If any field is missing, return an empty JSON
        return {}

# Example usage:
# input_text = "Great, I've created a ticket for you. Here are the details:\n\nContent: I need help with my account.\nSubject: account.\nPriority"
# json_output = extract_json(input_text)
# if json_output:
#     print(json_output)
# else:
#     print("Not all fields have values.")
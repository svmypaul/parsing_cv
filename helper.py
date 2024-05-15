from parser import parse_resume
import requests
import google.generativeai as genai
import json
import time
from loguru import logger

logger.add("Error.log", rotation="500 MB") 

# Define the API endpoint URL
url = 'http://demo.sites4social.com/api/user_cv'
secret_key = "AIzaSyAO3omBOQaMAJXOCSd07CqZF7_yPLecOlU"
# Define the API endpoint URL
URL = "http://demo.sites4social.com/api/parsed_cv"

headers = {
    'User-Agent': 'Your User Agent String Here',
}

def parser(text):
    
    text = text.replace('\n', ' ')
    genai.configure(api_key=secret_key)

    model = genai.GenerativeModel('gemini-pro')

    try:
        question = f"{text} find Name,year of exprience, Address the output should arrange it into a JSON format where the keys are 'name', 'yearofexp', 'address' "
        response = model.generate_content(question)
    except:
        response = ""

    # to_markdown(response.text)
    json_string = response.text.replace('\n', '')
    try:
        json_data = json.loads(json_string)['files']
        return json_data
    except:
        try:
            start_index = json_string.find('{')
            end_index = json_string.find('}', start_index) + 1

            # Extract the JSON object substring
            json_string = json_string[start_index:end_index]
            # Parse the JSON data from the extracted substring
            json_data = json.loads(json_string)
            return json_data
        except:
            json_data = {  "name": "",  "yearofexp": "",  "address": ""}
            return json_data
    
while True:
    print('-------------------------------------------------------------------------')
    try:
        time.sleep(10)
        # Make a GET request to the API
        response = requests.get(url, headers=headers)
        print(response)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract JSON content from the response
            json_data = response.json()
            
            # Iterate over each item in the JSON data
            for data in json_data:
                # Extract the 'text' field from each item
                Id = data.get('id')
                text = data.get('text')
                username = data.get('username')
                filename = data.get('filename')
                uniqueid = data.get('companyid')
                datetime = data.get('time')
                
                # Call the parse_resume function with the extracted text
                parsed_data = parse_resume(text)
                ai_parsed_data = parser(text)
                parsed_data['Name'] = ai_parsed_data['name']
                parsed_data['Location'] = ai_parsed_data['address']
                parsed_data['Skills'] = str(parsed_data['Skills'])
                parsed_data['id'] = Id
                parsed_data['username'] = username
                parsed_data['filename'] = filename
                parsed_data['uniqueid'] = uniqueid
                parsed_data['time'] = datetime
                
        
                Response = requests.post(URL, json=parsed_data, headers=headers)
        
                # Check if the request was successful (status code 200)
                if Response.status_code == 200:
                    print("Data sent successfully!")
                    logger.success("Data sent successfully!")
                else:
                    print("Failed to send data. Status code:", response.status_code)
                    logger.error(f"Failed to send data. Status code: {response.status_code}")
                print(parsed_data)
        
        else:
            # Print an error message if the request was unsuccessful
            logger.error(f"Error: {response.status_code}")
    except Exception as e:
        print('Global Error:',e)
        logger.error(f'global error: {e}')
        time.sleep(10)
        # Make a GET request to the API
        response = requests.get(url, headers=headers)
        print(response)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Extract JSON content from the response
            json_data = response.json()
            
            # Iterate over each item in the JSON data
            for data in json_data:
                # Extract the 'text' field from each item
                Id = data.get('id')
                text = data.get('text')
                username = data.get('username')
                filename = data.get('filename')
                uniqueid = data.get('companyid')
                datetime = data.get('time')
                
                # Call the parse_resume function with the extracted text
                parsed_data = parse_resume(text)
                parsed_data['Skills'] = str(parsed_data['Skills'])
                parsed_data['id'] = Id
                parsed_data['username'] = username
                parsed_data['filename'] = filename
                parsed_data['uniqueid'] = uniqueid
                parsed_data['time'] = datetime
                
        
                Response = requests.post(URL, json=parsed_data, headers=headers)
        
                # Check if the request was successful (status code 200)
                if Response.status_code == 200:
                    print("Data sent successfully!")
                    logger.success("Data sent successfully!")
                else:
                    print("Failed to send data. Status code:", response.status_code)
                    logger.error(f"Failed to send data. Status code: {response.status_code}")
                print(parsed_data)
        
        else:
            # Print an error message if the request was unsuccessful
            logger.error(f"Error: {response.status_code}")



        
        
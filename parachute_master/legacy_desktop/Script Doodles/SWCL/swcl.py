import requests
import json

# Define your Quip access token
ACCESS_TOKEN = "WEJhOU1BRlFGc2c=|1745849538|52MjKxHnq2jY94mKO4zYaxRbqcK6V9VMcN93JFhrgQQ="

# Define the document ID of the document you want to copy
document_id = "WZKKAonebgMR"

# Define the folder ID of the folder you want to copy the document to
new_folder_id = "7lbNOGztI3JA"

# Define the API endpoint URL
api_url = f"https://platform.quip.com/1/folders/{new_folder_id}/children"

# Define headers with authorization token
headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Define payload with document ID to copy and new folder ID
payload = {
    "thread_id": document_id,
    "title": "Copy of Document",
    "folder_ids": new_folder_id,
    "copy_annotations": False
}

# Send a POST request to copy the document to the new folder
response = requests.post(api_url, headers=headers, data=json.dumps(payload))

# Check if the request was successful
if response.status_code == 200:
    print("Document copied successfully!")
else:
    print("Error:", response.text)
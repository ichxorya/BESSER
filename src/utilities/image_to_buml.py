import requests
import json
import base64
import os

from BUML.notations.plantUML.plantuml_to_buml import plantuml_to_buml


def image_to_plantuml(image_path: str, openai_token: str):
    base64_image = ""
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    text = "Can you turn this drawn uml class diagram into the corresponding PlantUML class diagram? the diagram i sent might have some weird relations or classes, I want you to keep them as they are."
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai_token
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": text
            },
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
            ]
        }
        ],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    response_data = json.loads(response.text)

    # Extracting the message
    messages = [choice['message'] for choice in response_data.get('choices', {})]
    message = messages[0]["content"]
    # Find the start and end positions of the desired chunk
    start_position = message.find("@startuml")
    end_position = message.find("@enduml", start_position)

    # Extract the chunk
    plant_uml_chunk = message[start_position:end_position + len("@enduml")]
    # 
    return plant_uml_chunk


def image_to_buml(image_path: str, openai_token: str):
    plant_uml_chunk = image_to_plantuml(image_path=image_path, openai_token=openai_token)
    # Create and write to the file
    with open("image.txt", "w") as file:
        file.write(plant_uml_chunk)    
    domain = plantuml_to_buml("image.txt")
    os.remove("image.txt")
    return domain
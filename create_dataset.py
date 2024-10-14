import os
import uuid
import re
import requests
import json
from pydub import AudioSegment
import boto3
from botocore.exceptions import NoCredentialsError
import openai
import pandas as pd

# Your OpenAI and ElevenLabs API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

# AWS credentials and bucket information
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")
s3_bucket_name = os.getenv("S3_BUCKET_NAME")
aws_region = os.getenv("AWS_REGION")

# Initialize the OpenAI client
client = openai.OpenAI(api_key=openai_api_key)

# Function to generate text using OpenAI GPT-4
def generate_text(num_frames):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You simply generate text based on prompt"},
            {"role": "user", "content": f"Your job is to generate {num_frames} sentences in the form of a numbered list and nothing else"}
        ]
    )
    response = completion.choices[0].message.content
    sentences = re.split(r'\d+\.\s', response)[1:]  # Split by numbered list
    cleaned_sentences = [sentence.strip().replace("\n", "") for sentence in sentences]
    
    return cleaned_sentences

# Function to generate audio from text using ElevenLabs
def submit_text(generated_text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/TlLWC5O5AUzxAg7ysFZB"
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_api_key
    }
    data = {
        "text": generated_text,
        "voice_settings": {
            "stability": 0.1,
            "similarity_boost": 0
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error {response.status_code}: {response.content}")
        return None

# Function to convert audio to OGG format
def convert_to_ogg(mp3_file_path):
    ogg_file_path = mp3_file_path.replace(".mp3", ".ogg")
    audio = AudioSegment.from_mp3(mp3_file_path)
    audio.export(ogg_file_path, format="ogg")
    return ogg_file_path

# Function to upload OGG file to AWS S3
def upload_to_s3(file_path, file_name):
    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=aws_region
    )
    
    try:
        s3.upload_file(file_path, s3_bucket_name, file_name)
        file_url = f"https://{s3_bucket_name}.s3.{aws_region}.amazonaws.com/{file_name}"
        return file_url
    except FileNotFoundError:
        print("The file was not found.")
        return None
    except NoCredentialsError:
        print("Credentials not available.")
        return None

# Function to send OGG file for mouth cue generation
def send_for_mouth_cues(ogg_file_url):
    url = "http://34.123.67.37:7002/rhubarb_convert"
    headers = {"Content-Type": "application/json"}
    data = json.dumps({"url": ogg_file_url})
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.content}")
        return None

# Main function to handle the entire process
def process_prompts_and_audio(num_prompts):
    prompts = generate_text(num_prompts)
    mouth_cues_list = []
    
    for index, prompt in enumerate(prompts, 1):
        print(f"Processing prompt {index}: {prompt}")
        if not os.path.exists('generated_audio'):
            os.makedirs('generated_audio')

        # Generate audio for the prompt
        audio_content = submit_text(prompt)
        if not audio_content:
            continue

        # Save the MP3 file locally
        unique_id = str(uuid.uuid4())
        mp3_file_path = f"generated_audio/{unique_id}.mp3"
        with open(mp3_file_path, "wb") as audio_file:
            audio_file.write(audio_content)

        # Convert the MP3 file to OGG format
        ogg_file_path = convert_to_ogg(mp3_file_path)

        # Upload the OGG file to S3 and get the URL
        ogg_file_url = upload_to_s3(ogg_file_path, f"{unique_id}.ogg")
        if not ogg_file_url:
            continue

        # Send OGG file for mouth cue generation
        mouth_cues = send_for_mouth_cues(ogg_file_url)
        if mouth_cues:
            mouth_cues_list.append({
                "prompt": prompt,
                "mouth_cues": mouth_cues
            })

    # Output results in two columns
    print("Generated Prompts and Mouth Cues:")
    for item in mouth_cues_list:
        print(f"Prompt: {item['prompt']}")
        print(f"Mouth Cues: {item['mouth_cues']}")
        print("--------------------------")
    return mouth_cues_list


# Function to export prompts and mouth cues to an Excel file
def export_to_excel(mouth_cues_list, file_name="prompts_mouthcues.xlsx"):
    # Create a DataFrame from the mouth cues list
    df = pd.DataFrame(mouth_cues_list)
    
    # Write the DataFrame to an Excel file
    df.to_excel(file_name, index=False)
    
    print(f"Data successfully exported to {file_name}")

# Example usage after generating mouth cues
# Assuming mouth_cues_list is a list of dictionaries with 'prompt' and 'mouth_cues'
# Call this function after processing all the prompts
number = int(input("Enter the number of prompts: "))
mouth_cues_list = process_prompts_and_audio(number)
export_to_excel(mouth_cues_list)

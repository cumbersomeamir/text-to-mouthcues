import requests
import json
import os
import re
from pydub import AudioSegment
import uuid
import openai

# Set your API keys
openai_api_key = 'YOUR_OPENAI_API_KEY'
elevenlabs_api_key = 'YOUR_ELEVENLABS_API_KEY'

openai.api_key = openai_api_key

def generate_text(topic, num_frames):
    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a super creative non-fiction story writer"},
            {"role": "user", "content": f"Your job is to generate {num_frames} single line sentences which will be used in a voiceover about the topic {topic}. Please give numbered list only like 1. 2. 3. and so on"}
        ]
    )
    response = completion.choices[0].message.content
    sentences = re.split(r'\d+\.\s', response)[1:]  # Split by numbered list, and ignore the first empty element
    cleaned_sentences = [sentence.strip().replace("\n", "") for sentence in sentences]
    
    return cleaned_sentences

def generate_audio(sentence):
    url = "https://api.elevenlabs.io/v1/text-to-speech/TlLWC5O5AUzxAg7ysFZB"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_api_key
    }
    data = {
        "text": sentence,
        "voice_settings": {
            "stability": 0.1,
            "similarity_boost": 0
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        audio_content = response.content
        return audio_content
    else:
        print(f"Error {response.status_code}: {response.content}")
        return None

def save_audio_file(audio_content, filename):
    with open(filename, 'wb') as f:
        f.write(audio_content)
    print(f"Audio file saved to {filename}")

def convert_to_ogg(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format='ogg')
    print(f"Converted {input_file} to {output_file}")

def send_to_rhubarb(audio_file_path):
    api_url = 'http://<your-server-ip>:7002/rhubarb_convert'
    files = {'file': open(audio_file_path, 'rb')}
    response = requests.post(api_url, files=files)
    if response.status_code == 200:
        output_json = response.json()
        return output_json
    else:
        print(f"Error {response.status_code}: {response.content}")
        return None

def main():
    topic = input("Enter the topic: ")
    num_prompts = int(input("Enter the number of prompts: "))

    sentences = generate_text(topic, num_prompts)
    print("Generated Sentences:")
    for idx, sentence in enumerate(sentences, 1):
        print(f"{idx}. {sentence}")

    output_folder = "generated_audio"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    mouth_cues_list = []
    for idx, sentence in enumerate(sentences, 1):
        print(f"\nProcessing sentence {idx}: {sentence}")

        # Generate audio
        audio_content = generate_audio(sentence)
        if audio_content is None:
            continue

        # Save audio to file
        unique_id = str(uuid.uuid4())
        mp3_filename = os.path.join(output_folder, f"{unique_id}.mp3")
        save_audio_file(audio_content, mp3_filename)

        # Convert to OGG
        ogg_filename = os.path.join(output_folder, f"{unique_id}.ogg")
        convert_to_ogg(mp3_filename, ogg_filename)

        # Send to rhubarb_convert API
        output_json = send_to_rhubarb(ogg_filename)
        if output_json is None:
            continue

        mouth_cues_list.append({
            'sentence': sentence,
            'mouth_cues': output_json
        })

    # Save the results to a JSON file
    with open('mouth_cues_results.json', 'w') as f:
        json.dump(mouth_cues_list, f, indent=4)

    # Display the results
    print("\nFinal Results:")
    for item in mouth_cues_list:
        print(f"Sentence: {item['sentence']}")
        print(f"Mouth Cues: {item['mouth_cues']}")
        print("----------------------------")

if __name__ == '__main__':
    main()

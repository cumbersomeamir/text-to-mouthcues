import openai
import os


# Your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = openai.OpenAI(api_key=openai_api_key)

#Create Training
response = client.files.create(
  file=open("/Users/amir/Desktop/mouthcues/lib/python3.12/site-packages/prompts_mouthcues.jsonl", "rb"),
  purpose="fine-tune"
)

print("The response is ", response)

import openai
import os

# Your OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = openai.OpenAI(api_key=openai_api_key)


# Use the fine-tuned model for a chat completion
completion = client.chat.completions.create(
    model="ft:gpt-4o-mini:my-org:custom_suffix:id",  # Use your fine-tuned model
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ]
)
print(completion.choices[0].message)


#Need to get the model id to process the response

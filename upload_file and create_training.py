import openai
import os

# Initialize OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client
client = openai.OpenAI(api_key=openai_api_key)

# Upload file for fine-tuning
response = client.files.create(
    file=open("/Users/amir/Desktop/mouthcues/lib/python3.12/site-packages/prompts_mouthcues.jsonl", "rb"),
    purpose="fine-tune"
)
print("The response is: ", response)

# Capture the file ID from the upload response
file_id = response.id  # e.g., 'file-yzCgELbgHS6QAoFsHSqe8yP9'

# Create a fine-tuning job with the uploaded file
fine_tune_response = client.fine_tuning.jobs.create(
    training_file=file_id,  # Use the uploaded file ID
    model="gpt-4o-mini-2024-07-18"  # Specify the base model you want to fine-tune
)
print("Fine-tuning job response: ", fine_tune_response)

# Retrieve the fine-tuning job ID
fine_tuning_job_id = fine_tune_response.id  # Store job ID for future use

# Retrieve details of the created fine-tuning job
job_details = client.fine_tuning.jobs.retrieve(fine_tuning_job_id)
print("Fine-tuning job details: ", job_details)


# Check for events related to the fine-tuning job
events = client.fine_tuning.jobs.list_events(fine_tuning_job_id=fine_tuning_job_id, limit=10)
print("Fine-tuning job events: ", events)

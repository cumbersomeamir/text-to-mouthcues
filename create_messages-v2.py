import pandas as pd
import json

# Load the Excel file
file_path = '/Users/amir/desktop/mouthcues/lib/python3.12/site-packages/prompts_mouthcues.xlsx'
df = pd.read_excel(file_path)

# Open a .jsonl file to write the output
output_file = '/Users/amir/desktop/mouthcues/lib/python3.12/site-packages/prompts_mouthcues.jsonl'

with open(output_file, 'w') as jsonl_file:
    # Loop through each row in the dataframe
    for index, row in df.iterrows():
        # Construct the JSON structure
        json_obj = {
            "messages": [
                {"role": "system", "content": "You convert prompt to mouth cues"},
                {"role": "user", "content": row['prompt']},
                {"role": "assistant", "content": json.dumps(row['mouth_cues'])}  # Convert the list to string
            ]
        }
        # Write each JSON object to the file in jsonl format
        jsonl_file.write(json.dumps(json_obj) + '\n')

print(f"JSONL file created at: {output_file}")

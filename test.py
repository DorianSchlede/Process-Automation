import os

# Fetch the API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

# Print the API key
if api_key:
    print(f"API Key is: {api_key}")
else:
    print("API Key is not set")

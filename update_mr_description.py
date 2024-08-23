import os
import time
import requests
import openai
from openai.error import RateLimitError

# Load environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise KeyError('OPENAI_API_KEY not found in environment variables')

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
if not GITHUB_TOKEN:
    raise KeyError('GITHUB_TOKEN not found in environment variables')

REPO_OWNER = os.environ.get('GITHUB_REPO_OWNER')
if not REPO_OWNER:
    raise KeyError('GITHUB_REPO_OWNER not found in environment variables')

REPO_NAME = os.environ.get('GITHUB_REPO_NAME')
if not REPO_NAME:
    raise KeyError('GITHUB_REPO_NAME not found in environment variables')

PR_NUMBER = os.environ.get('GITHUB_PR_NUMBER')
if not PR_NUMBER:
    raise KeyError('GITHUB_PR_NUMBER not found in environment variables')

openai.api_key = OPENAI_API_KEY

def get_diff():
    with open('diff.txt', 'r') as file:
        return file.read()

def process_diff_with_openai(diff, retries=3, delay=60):
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Summarize the following git diff:\n\n{diff}"}],
                temperature=0.5,
            )
            return response.choices[0]['message']['content']
        except RateLimitError as e:
            print(f"RateLimitError: {e}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{retries})")
            time.sleep(delay)
    raise Exception("Exceeded maximum retries for OpenAI API due to rate limit.")

def update_pull_request_description(description):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{PR_NUMBER}'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {'body': description}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Failed to update pull request: {response.status_code}, {response.text}")

if __name__ == '__main__':
    diff = get_diff()
    if not diff:
        print("No changes detected in diff.txt.")
    else:
        description = process_diff_with_openai(diff)
        update_pull_request_description(description)

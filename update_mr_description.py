import os
import time
import requests
import openai
import json
from openai.error import RateLimitError

# Load environment variables
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise KeyError('OPENAI_API_KEY not found in environment variables')

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    raise KeyError('TOKEN not found in environment variables')

# Automatically determine the GitHub repository owner and name
REPO_OWNER = os.environ.get('GITHUB_REPOSITORY', '').split('/')[0]
REPO_NAME = os.environ.get('GITHUB_REPOSITORY', '').split('/')[1]

# Automatically determine the PR number from the GitHub event payload
GITHUB_EVENT_PATH = os.environ.get('GITHUB_EVENT_PATH')
if not GITHUB_EVENT_PATH:
    raise KeyError('GITHUB_EVENT_PATH not found in environment variables')

with open(GITHUB_EVENT_PATH, 'r') as f:
    event_data = json.load(f)
    PR_NUMBER = event_data.get('pull_request', {}).get('number')

if not PR_NUMBER:
    raise KeyError('Pull Request number not found in the GitHub event payload')

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
        'Authorization': f'token {TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {'body': description}
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Failed to update pull request: {response.status_code}, {response.text}")
    else:
        print(f"Successfully updated the pull request description for PR #{PR_NUMBER}")

if __name__ == '__main__':
    diff = get_diff()
    if not diff:
        print("No changes detected in diff.txt.")
    else:
        description = process_diff_with_openai(diff)
        update_pull_request_description(description)

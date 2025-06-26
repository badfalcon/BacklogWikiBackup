import requests
import time
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(encoding='utf-8')

print(os.environ)

API_KEY = os.getenv('API_KEY')
SPACE_ID = os.getenv('SPACE_ID')
PROJECT_ID = os.getenv('PROJECT_ID')
SPACE_EXTENSION = os.getenv('SPACE_EXTENSION')
BASE_URL = f'https://{SPACE_ID}.backlog.{SPACE_EXTENSION}/api/v2'

def get_wiki_page_list():
    url = f'{BASE_URL}/wikis'
    params = {
        'apiKey': API_KEY,
        'projectIdOrKey': PROJECT_ID,
        'keyword': ''
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_wiki_page(page_id):
    url = f'{BASE_URL}/wikis/{page_id}'
    params = {
        'apiKey': API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_rate_limit():
    url = f'{BASE_URL}/rateLimit'
    params = {
        'apiKey': API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def get_wiki_attachments(page_id):
    url = f'{BASE_URL}/wikis/{page_id}/attachments'
    params = {
        'apiKey': API_KEY
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def backlog_to_markdown(text):
    if text is None:
        return ""
    # Headers
    text = re.sub(r'^\*\*\*\s*(.*)', r'### \1', text, flags=re.MULTILINE)
    text = re.sub(r'^\*\*\s*(.*)', r'## \1', text, flags=re.MULTILINE)
    text = re.sub(r'^\*\s*(.*)', r'# \1', text, flags=re.MULTILINE)

    # Bold
    text = re.sub(r"''([^']+)''", r'**\1**', text)

    # Italic
    text = re.sub(r"'''([^']+)'''", r'*\1*', text)

    # Strikethrough
    text = re.sub(r'%%(.*?)%%', r'~~\1~~', text)

    # Unordered lists
    text = re.sub(r'^\s*\s*\-\s*(.*)', r'    * \1', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\-\s*(.*)', r'  * \1', text, flags=re.MULTILINE)
    text = re.sub(r'^\-\s*(.*)', r'* \1', text, flags=re.MULTILINE)

    # Ordered lists
    text = re.sub(r'^\s*\s*\+\s*(.*)', r'      1. \1', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\+\s*(.*)', r'   1. \1', text, flags=re.MULTILINE)
    text = re.sub(r'^\+\s*(.*)', r'1. \1', text, flags=re.MULTILINE)

    # Links
    text = re.sub(r'\[\[(.*?)\|(.*?)', r'[\1](\2.md)', text)
    text = re.sub(r'\[\[(.*?)\]\]', r'[\1](\1.md)', text)

    return text

def save_wiki_page(page_content, page_folder):
    safe_name = re.sub(r'[\\/*?:"<>|]', '_', page_content['name'])
    # Convert Backlog to Markdown
    markdown_content = backlog_to_markdown(page_content['content'])
    with open(f"{page_folder}/{safe_name}.md", 'w', encoding='utf-8') as file:
        file.write(markdown_content)

def save_attachments(page_id, attachments, page_folder):
    for attachment in attachments:
        print(f"  Downloading attachment {attachment['name']}...")
        attachment_name = re.sub(r'[\\/*?:"<>|]', '_', attachment['name'])
        attachment_path = os.path.join(page_folder, attachment_name)
        attachment_url = f"{BASE_URL}/wikis/{page_id}/attachments/{attachment['id']}"
        attachment_response = requests.get(attachment_url, params={'apiKey': API_KEY})
        attachment_response.raise_for_status()
        with open(attachment_path, 'wb') as attachment_file:
            attachment_file.write(attachment_response.content)

def backup_wiki():
    pages = get_wiki_page_list()
    rate_limit_info = get_rate_limit()
    remaining_requests = rate_limit_info['rateLimit']['read']['remaining']
    reset_time = rate_limit_info['rateLimit']['read']['reset']
    current_time = time.time()
    wait_time = max(0, reset_time - current_time) / remaining_requests

    if not os.path.exists(PROJECT_ID):
        os.makedirs(PROJECT_ID)

    for page in pages:
        print(f"Backing up {page['name']}...")
        page_id = page['id']
        page_content = get_wiki_page(page_id)
        folder_name = re.sub(r'[\\/*?:"<>|]', '_', page_content['name'])
        page_folder = os.path.join(PROJECT_ID, folder_name)

        if not os.path.exists(page_folder):
            os.makedirs(page_folder)

        save_wiki_page(page_content, page_folder)
        attachments = get_wiki_attachments(page_id)
        save_attachments(page_id, attachments, page_folder)

        time.sleep(wait_time)

if __name__ == '__main__':
    backup_wiki()
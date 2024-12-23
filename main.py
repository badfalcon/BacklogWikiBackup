import requests
import time
import os
import re
import time

API_KEY = 'YOUR_API_KEY'
SPACE_ID = 'YOUR_SPACE_ID'
PROJECT_ID = 'YOUR_PROJECT_ID'
SPACE_EXTENSION = 'YOUR_SPACE_EXTENSION'
BASE_URL = f'https://{SPACE_ID}.{SPACE_EXTENSION}.backlog.jp/api/v2'

def get_wiki_page_list():
    url = f'{BASE_URL}/wikis'
    print(f'url: {url}')
    params = {
        'apiKey': API_KEY,
        'projectIdOrKey': PROJECT_ID,
        'keyword': ''
    }
    response = requests.get(url, params=params)
    return response.json()

def get_wiki_page(page_id):
    url = f'{BASE_URL}/wikis/{page_id}'
    params = {
        'apiKey': API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()


def get_rate_limit():
    url = f'{BASE_URL}/rateLimit'
    params = {
        'apiKey': API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()


def get_wiki_attachments(page_id):
    url = f'{BASE_URL}/wikis/{page_id}/attachments'
    params = {
        'apiKey': API_KEY
    }
    response = requests.get(url, params=params)
    return response.json()

def backup_wiki():
    pages = get_wiki_page_list()
    rate_limit_info = get_rate_limit()
    remaining_requests = rate_limit_info['rateLimit']['read']['remaining']
    reset_time = rate_limit_info['rateLimit']['read']['reset']
    current_time = time.time()
    wait_time = max(0, reset_time - current_time) / remaining_requests

    # プロジェクトディレクトリが存在しない場合は作成
    if not os.path.exists(PROJECT_ID):
        os.makedirs(PROJECT_ID)

    for page in pages:
        page_id = page['id']
        page_content = get_wiki_page(page_id)
        
        # フォルダ名をページ名にして安全にする
        folder_name = re.sub(r'[\\/*?:"<>|]', '_', page_content['name'])
        page_folder = os.path.join(PROJECT_ID, folder_name)
        
        if not os.path.exists(page_folder):
            os.makedirs(page_folder)
        
        # ファイル名を安全にする
        safe_name = re.sub(r'[\\/*?:"<>|]', '_', page_content['name'])
        
        # Wikiページの内容を保存
        with open(f"{page_folder}/{safe_name}.md", 'w', encoding='utf-8') as file:
            file.write(page_content['content'])
        
        # 添付ファイルを取得して保存
        attachments = get_wiki_attachments(page_id)
        for attachment in attachments:
            attachment_name = re.sub(r'[\\/*?:"<>|]', '_', attachment['name'])
            attachment_path = os.path.join(page_folder, attachment_name)
            # 添付ファイルのダウンロード
            attachment_url = f"{BASE_URL}/wikis/{page_id}/attachments/{attachment['id']}"
            attachment_response = requests.get(attachment_url, params={'apiKey': API_KEY})
            with open(attachment_path, 'wb') as attachment_file:
                attachment_file.write(attachment_response.content)
        
        time.sleep(wait_time)  # レート制限に基づいて待機時間を設定

if __name__ == '__main__':
    backup_wiki()
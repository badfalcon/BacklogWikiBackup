# Backlog Wiki Backup Script

このスクリプトは、BacklogのWikiページとその添付ファイルをバックアップするためのものです。各Wikiページごとにフォルダを作成し、その中にページの内容と添付ファイルを保存します。

## 必要条件

- Python 3.x
- `requests`ライブラリ

## インストール

1. Pythonがインストールされていることを確認してください。
2. 必要なライブラリをインストールします。

```bash
pip install requests
```

## 設定

`sample.env`ファイルを元に`.env`ファイルを作成し、以下のように設定してください。

```dotenv
API_KEY=your_api_key
SPACE_ID=your_space_id
PROJECT_ID=your_project_id
SPACE_EXTENSION=your_space_extension
```

## 使用方法

1. `main.py`を実行して、Wikiページと添付ファイルをバックアップします。

```bash
python main.py
```

2. バックアップされたデータは、`PROJECT_ID`ディレクトリ内に保存されます。各Wikiページはページ名をフォルダ名として保存され、その中にページの内容と添付ファイルが含まれます。

## コードの概要

- `get_wiki_page_list()`: Wikiページのリストを取得します。
- `get_wiki_page(page_id)`: 指定されたIDのWikiページの内容を取得します。
- `get_rate_limit()`: APIのレート制限情報を取得します。
- `get_wiki_attachments(page_id)`: 指定されたIDのWikiページの添付ファイルを取得します。
- `backup_wiki()`: Wikiページと添付ファイルをバックアップします。

## 注意事項

- APIキーやプロジェクトIDなどの機密情報は、公開しないように注意してください。

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。

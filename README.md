# システム構成図

![システム構成図](システム構成図.drawio.png)

# 各種コマンド

- Docker イメージ作成およびコンテナの起動

```
$ docker compose up -d --build
```

- コンテナへ bash コマンドで入る

```
$ docker exec -it serverless bash
```

- Instaloader(Instagram のデータ取得ライブラリ) 用のセッションファイルアップロード

```
$ instaloader --login [username] --sessionfile [file_path]
Enter Instagram password for [username]: enter password
$ python migration/upload_instagram_session_file.py
```

- 本番環境へのデプロイ

```
$ sls deploy --stage prod
```

- [試験のみ]ローカル API サーバ起動（http://localhost:5000）

```
$ sls wsgi serve --stage [stage名 (dev or prod)]
```

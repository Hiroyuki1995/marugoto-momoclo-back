# marugoto-momoclo-back

まるごとももクロのバックエンド開発

# バックエンド

## 事前準備

- serverless framework のグローバルインストール

```
$ npm i -g serverless
```

- instaloader のセッションファイルの作成

以下のコマンドで作成したファイルを S3 バケット"marugoto-momoclo-secret"にファイル名"session_instagram"として配置する。

```
$ instaloader --login [username] --sessionfile [file_path]
Enter Instagram password for [username]: enter password
```

代替手段として以下のコマンドも用意

```
$ yarn instaloader
```

- instaloader のセッションファイルの S3 へのアップロード

```
$ python migration/upload_instagram_session_file.py
```

## 通常コマンド

- AWS へのデプロイコマンド

```
$ sls deploy
```

- ローカル API サーバ起動（http://localhost:5000）

```
$ sls wsgi serve --stage [stage名]
```

- ローカル DynamoDB 起動（http://locahost:8000/shell）

```
sls dynamodb start --stage test
```

- 現在の Python のライブラリを保存

```
$ pip freeze > requirements.txt
```

- ローカルフロントエンドサーバ起動（http://localhost:3000）

```
yarn start
```

- ローカルファンクション実行（https://www.serverless.com/framework/docs/providers/aws/cli-reference/invoke-local/）

```
serverless invoke local --function [functionName]
```

## [参考]

Python における仮想環境については[こちら](https://www.python.jp/install/windows/venv.html)

- 仮想環境作成

```
$ python -m venv [ディレクトリ名]
```

- 仮想環境の有効化

```
$ source [ディレクトリ名]/bin/activate
```

- 仮想環境上に、requirements.txt に設定されているライブラリをインストールする

```
pip install -r requirements.txt
```

- 仮想環境の無効化

```
$ deactivate
```

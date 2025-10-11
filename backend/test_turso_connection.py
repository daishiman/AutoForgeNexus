import os

import libsql_client

# 環境変数から接続情報取得
db_url = os.getenv("TURSO_DATABASE_URL")
auth_token = os.getenv("TURSO_AUTH_TOKEN")

print(f"Connecting to: {db_url}")

try:
    client = libsql_client.create_client_sync(url=db_url, auth_token=auth_token)
    result = client.execute("SELECT 'Connection OK' AS status")
    print(f"✅ Database Connection: {result.rows[0]['status']}")
    print(f"✅ Database URL: {db_url}")
except Exception as e:
    print(f"❌ Database Connection Error: {e}")

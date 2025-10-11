-- Phase 4: Database Vector Setup - Test Tables
-- 開発環境用のテストテーブル作成スクリプト

-- テスト用プロンプトテーブル
CREATE TABLE IF NOT EXISTS test_prompts (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- テスト用評価結果テーブル
CREATE TABLE IF NOT EXISTS test_evaluations (
    id TEXT PRIMARY KEY,
    prompt_id TEXT NOT NULL,
    score REAL,
    metrics JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES test_prompts(id)
);

-- テスト用ユーザーテーブル
CREATE TABLE IF NOT EXISTS test_users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ベクトル検索テスト用テーブル（将来のlibSQL Vector Extension用）
CREATE TABLE IF NOT EXISTS test_embeddings (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    embedding BLOB, -- Vector data will be stored here
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス作成
CREATE INDEX IF NOT EXISTS idx_prompts_created ON test_prompts(created_at);
CREATE INDEX IF NOT EXISTS idx_evaluations_prompt ON test_evaluations(prompt_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON test_users(email);

-- テストデータ挿入
INSERT OR IGNORE INTO test_prompts (id, name, content, metadata) VALUES
    ('test-001', 'サンプルプロンプト1', 'これはテスト用のプロンプトです。', '{"category": "test", "tags": ["sample"]}'),
    ('test-002', '改善版プロンプト', 'より詳細な指示を含むプロンプト。', '{"category": "test", "tags": ["improved"]}');

INSERT OR IGNORE INTO test_users (id, email, name) VALUES
    ('user-001', 'test@example.com', 'テストユーザー'),
    ('user-002', 'dev@example.com', '開発ユーザー');

INSERT OR IGNORE INTO test_evaluations (id, prompt_id, score, metrics) VALUES
    ('eval-001', 'test-001', 0.75, '{"clarity": 0.8, "completeness": 0.7}'),
    ('eval-002', 'test-002', 0.85, '{"clarity": 0.9, "completeness": 0.8}');
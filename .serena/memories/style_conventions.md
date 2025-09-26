# AutoForgeNexus スタイル・規約

## コード規約

### Python (バックエンド)
- **フォーマッター**: Ruff 0.7.4
- **型チェック**: mypy 1.13.0 (strict mode)
- **命名**: snake_case（変数・関数）、PascalCase（クラス）
- **ドキュメント**: Sphinx形式docstring必須
- **型ヒント**: 全関数・メソッドで必須

### TypeScript/React (フロントエンド)
- **フォーマッター**: ESLint + Prettier
- **命名**: camelCase（変数・関数）、PascalCase（コンポーネント・型）
- **コンポーネント**: 関数コンポーネント + React 19 hooks
- **状態管理**: Zustand 5.0.8
- **スタイリング**: Tailwind CSS 4.0 + shadcn/ui

## ディレクトリ構造規約
```
backend/
├── src/
│   ├── domain/         # エンティティ・値オブジェクト・集約
│   ├── application/    # ユースケース・CQRS・イベントハンドラー
│   ├── infrastructure/ # Turso/Redis/LangFuse実装
│   └── presentation/   # REST API・WebSocket・コントローラー
└── tests/              # pytest（80%+カバレッジ）

frontend/
├── src/
│   ├── app/            # App Router (Next.js 15.5)
│   ├── components/     # React 19 Server Components
│   ├── lib/            # ユーティリティ・Clerk統合
│   └── stores/         # Zustand状態管理
└── tests/              # Jest + Playwright E2E
```

## DDD設計パターン
- **集約ルート**: 不変条件の保証
- **ドメインイベント**: 状態変更の通知
- **リポジトリパターン**: データアクセスの抽象化
- **ファクトリパターン**: 複雑な集約の生成

##品質基準
- **テストカバレッジ**: バックエンド80%+、フロントエンド75%+必須
- **型安全性**: mypy strict モード、TypeScript strict設定
- **API設計**: OpenAPI 3.0準拠、RESTful原則
- **セキュリティ**: OWASP Top 10対策、GDPR準拠
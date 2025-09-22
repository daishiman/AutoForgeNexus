# AutoForgeNexus ドメインモデル設計書

## 🎯 ドメイン概要

AutoForgeNexusは**プロンプトエンジニアリング**を中心とした複雑なドメインを扱います。
DDDアプローチにより、ビジネス複雑性を適切に分離・管理します。

## 🌐 境界付きコンテキスト (Bounded Context)

### 1. Prompt Context (プロンプトコンテキスト) - コアドメイン
**責務**: プロンプトのライフサイクル管理
- プロンプト作成・編集・削除
- バージョン管理
- テンプレート管理

### 2. Evaluation Context (評価コンテキスト) - コアドメイン
**責務**: プロンプト品質評価
- 多層評価メトリクス
- A/Bテスト実行
- パフォーマンス測定

### 3. LLM Integration Context (LLM統合コンテキスト) - サポートドメイン
**責務**: 外部LLMプロバイダー統合
- マルチプロバイダー管理
- API統合
- コスト管理

### 4. User Management Context (ユーザー管理コンテキスト) - 汎用ドメイン
**責務**: ユーザー・認証・認可
- ユーザー管理
- 権限管理
- 組織管理

### 5. Analytics Context (分析コンテキスト) - サポートドメイン
**責務**: データ分析・インサイト
- 使用統計
- トレンド分析
- 推奨エンジン

## 🏗️ 集約ルート設計

### 📝 Prompt Aggregate (プロンプト集約)

```typescript
// プロンプト集約ルート
class Prompt {
  private constructor(
    private readonly id: PromptId,
    private content: PromptContent,
    private metadata: PromptMetadata,
    private versions: PromptVersionHistory,
    private evaluations: EvaluationResults
  ) {}

  // ファクトリメソッド
  static create(content: string, userId: UserId, templateId?: TemplateId): Prompt
  static fromTemplate(templateId: TemplateId, userId: UserId): Prompt

  // ビジネスロジック
  updateContent(newContent: string, userId: UserId): void
  createVersion(versionType: VersionType): PromptVersion
  evaluate(metrics: EvaluationMetric[]): EvaluationResult
  optimize(strategy: OptimizationStrategy): Prompt

  // イベント発行
  private publishEvent(event: DomainEvent): void
}
```

**不変条件**:
- プロンプトIDは一意である
- コンテンツは空文字列であってはならない
- 作成者は必須である
- バージョンは単調増加する

### 📊 Evaluation Aggregate (評価集約)

```typescript
class Evaluation {
  private constructor(
    private readonly id: EvaluationId,
    private readonly promptId: PromptId,
    private metrics: Map<MetricType, MetricResult>,
    private status: EvaluationStatus,
    private executedAt: Date
  ) {}

  static create(promptId: PromptId, metrics: EvaluationMetric[]): Evaluation

  // ビジネスロジック
  executeEvaluation(): void
  addMetricResult(metric: MetricType, result: MetricResult): void
  calculateOverallScore(): Score
  compareWith(other: Evaluation): ComparisonResult
}
```

### 🔌 LLMProvider Aggregate (LLMプロバイダー集約)

```typescript
class LLMProvider {
  private constructor(
    private readonly id: ProviderId,
    private name: ProviderName,
    private apiConfig: ApiConfiguration,
    private costConfig: CostConfiguration,
    private capabilities: ProviderCapabilities
  ) {}

  static register(name: string, config: ApiConfiguration): LLMProvider

  // ビジネスロジック
  executePrompt(prompt: Prompt): PromptResponse
  calculateCost(prompt: Prompt): Cost
  isAvailable(): boolean
  updateCapabilities(capabilities: ProviderCapabilities): void
}
```

## 🎯 エンティティ設計

### PromptVersion (プロンプトバージョン)
```typescript
class PromptVersion {
  private constructor(
    private readonly id: VersionId,
    private readonly promptId: PromptId,
    private readonly version: VersionNumber,
    private readonly content: PromptContent,
    private readonly createdAt: Date,
    private readonly createdBy: UserId,
    private readonly changeLog: ChangeLog
  ) {}

  // ビジネスロジック
  diff(other: PromptVersion): VersionDiff
  rollback(): Prompt
  createBranch(branchName: string): PromptBranch
}
```

### Template (テンプレート)
```typescript
class Template {
  private constructor(
    private readonly id: TemplateId,
    private name: TemplateName,
    private category: TemplateCategory,
    private structure: TemplateStructure,
    private parameters: TemplateParameter[]
  ) {}

  // ビジネスロジック
  instantiate(parameters: Map<string, any>): Prompt
  validate(parameters: Map<string, any>): ValidationResult
  customizeFor(userId: UserId): CustomTemplate
}
```

## 💎 値オブジェクト設計

### PromptContent (プロンプトコンテンツ)
```typescript
class PromptContent {
  private constructor(private readonly value: string) {
    this.validate(value);
  }

  static of(value: string): PromptContent

  private validate(value: string): void {
    if (!value || value.trim().length === 0) {
      throw new Error("プロンプトコンテンツは空であってはならない");
    }
    if (value.length > 10000) {
      throw new Error("プロンプトコンテンツは10000文字以下である必要がある");
    }
  }

  // ビジネスロジック
  wordCount(): number
  estimateTokens(): number
  extractKeywords(): Keyword[]
  sentiment(): SentimentScore
}
```

### Score (スコア)
```typescript
class Score {
  private constructor(private readonly value: number) {
    if (value < 0 || value > 1) {
      throw new Error("スコアは0-1の範囲である必要がある");
    }
  }

  static of(value: number): Score
  static fromPercentage(percentage: number): Score

  // ビジネスロジック
  isHighQuality(): boolean // 0.8以上
  grade(): Grade // A, B, C, D, F
  compareTo(other: Score): number
}
```

### UsageQuota (使用クォータ)
```typescript
class UsageQuota {
  private constructor(
    private readonly limit: number,
    private current: number,
    private readonly resetPeriod: Duration
  ) {}

  // ビジネスロジック
  canConsume(amount: number): boolean
  consume(amount: number): void
  remainingQuota(): number
  resetIfNeeded(): void
}
```

## 🔧 ドメインサービス

### PromptOptimizationService (プロンプト最適化サービス)
```typescript
class PromptOptimizationService {
  constructor(
    private llmProviders: LLMProviderRepository,
    private evaluationService: EvaluationService,
    private optimizationStrategies: OptimizationStrategy[]
  ) {}

  async optimizePrompt(
    prompt: Prompt,
    strategy: OptimizationStrategy
  ): Promise<OptimizedPrompt> {
    // 最適化アルゴリズムの実行
    // 複数戦略の並列実行
    // 結果の統合と選択
  }
}
```

### IntentDifferenceAnalysisService (意図差分分析サービス)
```typescript
class IntentDifferenceAnalysisService {
  async analyzeIntentDifference(
    userIntent: UserIntent,
    prompt: Prompt
  ): Promise<IntentDifference> {
    // NLP技術を使用した意図分析
    // 差分の特定と可視化
    // 改善提案の生成
  }
}
```

### CostOptimizationService (コスト最適化サービス)
```typescript
class CostOptimizationService {
  async findOptimalProvider(
    prompt: Prompt,
    requirements: QualityRequirements
  ): Promise<OptimalProviderRecommendation> {
    // コスト効率分析
    // 品質要件との適合性評価
    // 最適プロバイダーの推奨
  }
}
```

## ⚡ ドメインイベント

### PromptCreated (プロンプト作成イベント)
```typescript
class PromptCreated implements DomainEvent {
  constructor(
    public readonly eventId: EventId,
    public readonly promptId: PromptId,
    public readonly userId: UserId,
    public readonly templateId: TemplateId | null,
    public readonly occurredAt: Date
  ) {}

  eventType(): string { return 'PromptCreated'; }
}
```

### EvaluationCompleted (評価完了イベント)
```typescript
class EvaluationCompleted implements DomainEvent {
  constructor(
    public readonly eventId: EventId,
    public readonly evaluationId: EvaluationId,
    public readonly promptId: PromptId,
    public readonly overallScore: Score,
    public readonly metrics: Map<MetricType, MetricResult>,
    public readonly occurredAt: Date
  ) {}

  eventType(): string { return 'EvaluationCompleted'; }
}
```

### PromptOptimized (プロンプト最適化イベント)
```typescript
class PromptOptimized implements DomainEvent {
  constructor(
    public readonly eventId: EventId,
    public readonly originalPromptId: PromptId,
    public readonly optimizedPromptId: PromptId,
    public readonly strategy: OptimizationStrategy,
    public readonly improvementScore: Score,
    public readonly occurredAt: Date
  ) {}

  eventType(): string { return 'PromptOptimized'; }
}
```

## 🗄️ リポジトリ設計

### PromptRepository (プロンプトリポジトリ)
```typescript
interface PromptRepository {
  // 基本CRUD
  save(prompt: Prompt): Promise<void>
  findById(id: PromptId): Promise<Prompt | null>
  delete(id: PromptId): Promise<void>

  // ビジネスクエリ
  findByUserId(userId: UserId): Promise<Prompt[]>
  findByTemplate(templateId: TemplateId): Promise<Prompt[]>
  findHighPerforming(threshold: Score): Promise<Prompt[]>
  findRecentlyUpdated(days: number): Promise<Prompt[]>

  // 複合クエリ
  searchByKeywords(keywords: string[]): Promise<Prompt[]>
  findSimilar(prompt: Prompt, similarity: number): Promise<Prompt[]>
}
```

### EvaluationRepository (評価リポジトリ)
```typescript
interface EvaluationRepository {
  save(evaluation: Evaluation): Promise<void>
  findById(id: EvaluationId): Promise<Evaluation | null>
  findByPromptId(promptId: PromptId): Promise<Evaluation[]>
  findByMetricType(metricType: MetricType): Promise<Evaluation[]>

  // 分析クエリ
  findBestPerforming(limit: number): Promise<Evaluation[]>
  findTrendData(period: DateRange): Promise<TrendData>
  calculateAverageScore(criteria: EvaluationCriteria): Promise<Score>
}
```

## 🎯 CQRS実装

### Command Model (コマンドモデル)
```typescript
// コマンド
interface CreatePromptCommand {
  userId: UserId;
  content: string;
  templateId?: TemplateId;
}

interface OptimizePromptCommand {
  promptId: PromptId;
  strategy: OptimizationStrategy;
  userId: UserId;
}

// コマンドハンドラー
class CreatePromptCommandHandler {
  async handle(command: CreatePromptCommand): Promise<PromptId> {
    const prompt = Prompt.create(
      command.content,
      command.userId,
      command.templateId
    );

    await this.promptRepository.save(prompt);
    return prompt.id;
  }
}
```

### Query Model (クエリモデル)
```typescript
// 読み取り専用DTO
interface PromptSummaryDto {
  id: string;
  title: string;
  createdAt: Date;
  lastModified: Date;
  overallScore: number;
  tags: string[];
}

interface PromptDetailDto {
  id: string;
  content: string;
  metadata: PromptMetadataDto;
  versions: PromptVersionDto[];
  evaluations: EvaluationSummaryDto[];
}

// クエリサービス
class PromptQueryService {
  async getPromptSummaries(userId: UserId): Promise<PromptSummaryDto[]>
  async getPromptDetail(promptId: PromptId): Promise<PromptDetailDto>
  async searchPrompts(query: SearchQuery): Promise<PromptSummaryDto[]>
}
```

## 📋 イベントソーシング実装

### Event Store Design
```typescript
interface EventStore {
  saveEvents(streamId: string, events: DomainEvent[]): Promise<void>
  getEvents(streamId: string): Promise<DomainEvent[]>
  getEventsFromVersion(streamId: string, version: number): Promise<DomainEvent[]>
}

// 集約の再構築
class PromptEventSourcedRepository {
  async findById(id: PromptId): Promise<Prompt | null> {
    const events = await this.eventStore.getEvents(id.value);
    if (events.length === 0) return null;

    return Prompt.fromEvents(events);
  }

  async save(prompt: Prompt): Promise<void> {
    const uncommittedEvents = prompt.getUncommittedEvents();
    await this.eventStore.saveEvents(prompt.id.value, uncommittedEvents);
    prompt.markEventsAsCommitted();
  }
}
```

## 🔄 ドメインサービス統合例

```typescript
// 複雑なビジネスプロセスの例
class PromptImprovementWorkflow {
  constructor(
    private promptRepo: PromptRepository,
    private evaluationService: EvaluationService,
    private optimizationService: PromptOptimizationService,
    private eventBus: EventBus
  ) {}

  async improvePrompt(promptId: PromptId): Promise<ImprovedPrompt> {
    // 1. プロンプト取得
    const prompt = await this.promptRepo.findById(promptId);

    // 2. 現在の評価実行
    const evaluation = await this.evaluationService.evaluate(prompt);

    // 3. 最適化戦略決定
    const strategy = this.determineOptimizationStrategy(evaluation);

    // 4. 最適化実行
    const optimizedPrompt = await this.optimizationService.optimize(prompt, strategy);

    // 5. 改善結果保存
    await this.promptRepo.save(optimizedPrompt);

    // 6. イベント発行
    this.eventBus.publish(new PromptOptimized(
      EventId.generate(),
      promptId,
      optimizedPrompt.id,
      strategy,
      evaluation.overallScore,
      new Date()
    ));

    return new ImprovedPrompt(prompt, optimizedPrompt, evaluation);
  }
}
```

---

**ドキュメント情報**
- 作成日: 2025-09-22
- バージョン: 1.0
- 対象コンテキスト: 全境界付きコンテキスト
- DDD戦術パターン: 完全実装

🤖 Generated with AutoForgeNexus System
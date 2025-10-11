# Event-Driven Communication Contracts

## Event Structure

### Base Event Schema

```typescript
interface BaseEvent {
  eventId: string; // UUID v4
  eventType: string; // Domain.Entity.Action
  timestamp: ISO8601; // UTC timestamp
  version: string; // Event version (semver)
  correlationId: string; // Request tracking
  causationId: string; // Parent event ID
  metadata: {
    source: string; // Publishing agent
    tenantId: string; // Multi-tenant support
    userId?: string; // User context
    sessionId?: string; // Session tracking
  };
  payload: object; // Event-specific data
}
```

## Core Event Contracts

### PromptCreationRequested

```typescript
{
  eventType: "Prompt.Creation.Requested",
  payload: {
    requirements: {
      description: string;
      context: string[];
      constraints: object;
      targetModel?: string;
    },
    priority: "low" | "medium" | "high" | "critical",
    deadline?: ISO8601
  }
}

Subscribers:
- prompt-engineering-specialist (handler)
- domain-modellerr (context analysis)
- ui-ux-designer (UI update)
```

### EvaluationRequested

```typescript
{
  eventType: "Evaluation.Execution.Requested",
  payload: {
    promptId: string;
    testCases: TestCase[];
    metrics: string[];
    models: string[];
    config: EvaluationConfig;
  }
}

Subscribers:
- evaluation-engine (handler)
- llm-integration (execution)
- performance-optimizer (monitoring)
```

### WorkflowExecutionStarted

```typescript
{
  eventType: "Workflow.Execution.Started",
  payload: {
    workflowId: string;
    instanceId: string;
    input: object;
    steps: WorkflowStep[];
  }
}

Subscribers:
- backend-developer (environment setup)
- observability-engineer (monitoring)
- real-time-features-specialist (UI updates)
```

## Event Flow Patterns

### Saga Pattern

```yaml
Saga: PromptOptimizationSaga
Steps:
  1. PromptCreationRequested 2. PromptDraftCreated 3. EvaluationRequested 4.
  EvaluationCompleted 5. OptimizationRequested 6. PromptOptimized

Compensations:
  - PromptCreationFailed → PromptRollback
  - EvaluationFailed → RetryEvaluation
  - OptimizationFailed → RestorePrevious
```

### Event Sourcing Pattern

```yaml
Aggregate: PromptAggregate
Events:
  - PromptCreated
  - PromptUpdated
  - PromptValidated
  - PromptPublished
  - PromptArchived

State Reconstruction:
  events.reduce((state, event) => applyEvent(state, event), initialState)
```

## Error Handling

### Failure Events

```typescript
interface FailureEvent extends BaseEvent {
  error: {
    code: string;
    message: string;
    details: object;
    retryable: boolean;
    retryAfter?: number;
  };
  originalEvent: BaseEvent;
}
```

### Retry Policy

```yaml
RetryStrategy:
  maxAttempts: 3
  backoff: exponential
  initialDelay: 1000ms
  maxDelay: 30000ms
  retryableErrors:
    - TIMEOUT
    - RATE_LIMIT
    - TEMPORARY_FAILURE
```

## SLA Requirements

### Event Processing

- **Latency**: P95 < 100ms
- **Throughput**: 10,000 events/sec
- **Durability**: At-least-once delivery
- **Ordering**: Partial ordering per aggregate

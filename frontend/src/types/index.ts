// User関連の型定義
export interface User {
  id: string
  email: string
  name: string
  role?: 'user' | 'admin' | 'moderator'
  createdAt: Date
  updatedAt: Date
}

// API Response型定義
export interface ApiResponse<T = unknown> {
  data?: T
  error?: string
  status: number
  message?: string
}

// Prompt関連の型定義
export interface Prompt {
  id: string
  title: string
  content: string
  description?: string
  tags: string[]
  version: string
  createdBy: string
  createdAt: Date
  updatedAt: Date
}

// Evaluation関連の型定義
export interface Evaluation {
  id: string
  promptId: string
  score: number
  metrics: EvaluationMetrics
  feedback?: string
  createdAt: Date
}

export interface EvaluationMetrics {
  relevance: number
  coherence: number
  completeness: number
  accuracy: number
  toxicity: number
}

// Test Suite関連の型定義
export interface TestSuite {
  id: string
  name: string
  description: string
  testCases: TestCase[]
  createdAt: Date
  updatedAt: Date
}

export interface TestCase {
  id: string
  name: string
  input: string
  expectedOutput: string
  actualOutput?: string
  passed?: boolean
  error?: string
}

// LLM Provider関連の型定義
export interface LLMProvider {
  id: string
  name: string
  model: string
  apiKey?: string
  endpoint: string
  maxTokens: number
  temperature: number
  costPerToken: number
}

// Workflow関連の型定義
export interface Workflow {
  id: string
  name: string
  description: string
  steps: WorkflowStep[]
  status: 'draft' | 'active' | 'completed' | 'failed'
  createdAt: Date
  updatedAt: Date
}

export interface WorkflowStep {
  id: string
  name: string
  type: 'prompt' | 'evaluation' | 'transform' | 'branch'
  config: Record<string, unknown>
  nextSteps: string[]
}
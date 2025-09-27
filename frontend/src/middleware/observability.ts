/**
 * AutoForgeNexus - Frontend Observability Middleware
 * observability-engineer による包括的フロントエンド観測ミドルウェア
 */

import { NextRequest, NextResponse } from 'next/server';
import { monitor } from '@/lib/monitoring';

// リクエスト追跡のための型定義
interface RequestContext {
  requestId: string;
  timestamp: string;
  method: string;
  path: string;
  userAgent?: string;
  ip: string;
  startTime: number;
}

// フロントエンド専用のミドルウェア関数
export function observabilityMiddleware(request: NextRequest) {
  const startTime = Date.now();
  const requestId = crypto.randomUUID();

  // リクエストコンテキスト
  const context: RequestContext = {
    requestId,
    timestamp: new Date().toISOString(),
    method: request.method,
    path: request.nextUrl.pathname,
    userAgent: request.headers.get('user-agent') || undefined,
    ip: getClientIP(request),
    startTime,
  };

  // 除外パス（監視対象外）
  const excludePaths = [
    '/api/health',
    '/api/metrics',
    '/favicon.ico',
    '/_next/',
    '/static/',
  ];

  // 除外パスのチェック
  if (excludePaths.some(path => context.path.startsWith(path))) {
    return NextResponse.next();
  }

  // リクエスト開始ログ
  console.log('Frontend request started', {
    ...context,
    type: 'request_start',
  });

  // レスポンス処理
  const response = NextResponse.next();

  // レスポンスヘッダーにトレーシング情報を追加
  response.headers.set('X-Request-ID', requestId);
  response.headers.set('X-Timestamp', context.timestamp);

  // レスポンス完了の非同期処理
  Promise.resolve().then(() => {
    const duration = Date.now() - startTime;

    // レスポンス完了ログ
    console.log('Frontend request completed', {
      ...context,
      type: 'request_end',
      statusCode: response.status,
      duration,
    });

    // メトリクス記録（クライアントサイド）
    if (typeof window !== 'undefined') {
      monitor.recordCustomEvent('api_request', {
        method: context.method,
        path: context.path,
        statusCode: response.status,
        duration,
        requestId,
      });
    }
  });

  return response;
}

// クライアントIP取得関数
function getClientIP(request: NextRequest): string {
  // Cloudflare
  const cfConnectingIP = request.headers.get('cf-connecting-ip');
  if (cfConnectingIP) return cfConnectingIP;

  // 一般的なプロキシヘッダー
  const xForwardedFor = request.headers.get('x-forwarded-for');
  if (xForwardedFor) return xForwardedFor.split(',')[0].trim();

  const xRealIP = request.headers.get('x-real-ip');
  if (xRealIP) return xRealIP;

  // フォールバック
  return request.ip || 'unknown';
}

// API ルート用の監視デコレーター
export function withObservability<T extends any[], R>(
  handler: (...args: T) => Promise<R>,
  options: {
    operation: string;
    includeRequestBody?: boolean;
    includeResponseBody?: boolean;
  } = { operation: 'api_call' }
) {
  return async (...args: T): Promise<R> => {
    const startTime = Date.now();
    const operationId = crypto.randomUUID();

    const context = {
      operationId,
      operation: options.operation,
      timestamp: new Date().toISOString(),
      startTime,
    };

    console.log('API operation started', {
      ...context,
      type: 'operation_start',
    });

    try {
      const result = await handler(...args);

      const duration = Date.now() - startTime;

      console.log('API operation completed', {
        ...context,
        type: 'operation_success',
        duration,
      });

      // クライアントサイドメトリクス記録
      if (typeof window !== 'undefined') {
        monitor.recordCustomEvent('api_operation', {
          operation: options.operation,
          duration,
          success: true,
          operationId,
        });
      }

      return result;

    } catch (error) {
      const duration = Date.now() - startTime;

      console.error('API operation failed', {
        ...context,
        type: 'operation_error',
        duration,
        error: error instanceof Error ? error.message : 'Unknown error',
        errorType: error instanceof Error ? error.constructor.name : 'Unknown',
      });

      // エラーメトリクス記録
      if (typeof window !== 'undefined') {
        monitor.recordError({
          timestamp: new Date().toISOString(),
          type: 'javascript',
          message: error instanceof Error ? error.message : 'Unknown error',
          stack: error instanceof Error ? error.stack : undefined,
          url: window.location.href,
          userAgent: navigator.userAgent,
          sessionId: monitor.getSessionInfo().sessionId,
          userId: monitor.getSessionInfo().userId,
        });
      }

      throw error;
    }
  };
}

// React コンポーネント用の監視HOC
export function withComponentObservability<P extends object>(
  Component: React.ComponentType<P>,
  componentName: string
) {
  return function ObservedComponent(props: P) {
    const renderStart = Date.now();

    console.log('Component render started', {
      component: componentName,
      timestamp: new Date().toISOString(),
      type: 'component_render_start',
    });

    React.useEffect(() => {
      const renderDuration = Date.now() - renderStart;

      console.log('Component render completed', {
        component: componentName,
        timestamp: new Date().toISOString(),
        type: 'component_render_end',
        duration: renderDuration,
      });

      // パフォーマンスメトリクス記録
      if (typeof window !== 'undefined') {
        monitor.recordPerformanceMetric({
          timestamp: new Date().toISOString(),
          type: 'user-interaction',
          name: `component_render_${componentName}`,
          value: renderDuration,
          unit: 'ms',
          metadata: {
            component: componentName,
          },
        });
      }
    }, [renderDuration]);

    return React.createElement(Component, props);
  };
}

// プロンプト処理専用の監視関数
export function trackPromptProcessing(
  promptId: string,
  operation: 'create' | 'optimize' | 'evaluate' | 'template'
) {
  const startTime = Date.now();
  const trackingId = crypto.randomUUID();

  console.log('Prompt processing started', {
    trackingId,
    promptId,
    operation,
    timestamp: new Date().toISOString(),
    type: 'prompt_processing_start',
  });

  return {
    trackingId,
    complete: (result: {
      success: boolean;
      tokensUsed?: number;
      cost?: number;
      quality?: number;
      error?: string;
    }) => {
      const duration = Date.now() - startTime;

      console.log('Prompt processing completed', {
        trackingId,
        promptId,
        operation,
        timestamp: new Date().toISOString(),
        type: 'prompt_processing_end',
        duration,
        ...result,
      });

      // プロンプト専用メトリクス記録
      if (typeof window !== 'undefined') {
        monitor.recordCustomEvent('prompt_processing', {
          promptId,
          operation,
          duration,
          trackingId,
          ...result,
        });
      }
    },
  };
}

// LLM API 呼び出し監視
export function trackLLMCall(
  provider: string,
  model: string,
  promptLength: number
) {
  const startTime = Date.now();
  const callId = crypto.randomUUID();

  console.log('LLM call started', {
    callId,
    provider,
    model,
    promptLength,
    timestamp: new Date().toISOString(),
    type: 'llm_call_start',
  });

  return {
    callId,
    complete: (result: {
      success: boolean;
      responseLength?: number;
      tokensUsed?: number;
      cost?: number;
      error?: string;
    }) => {
      const duration = Date.now() - startTime;

      console.log('LLM call completed', {
        callId,
        provider,
        model,
        promptLength,
        timestamp: new Date().toISOString(),
        type: 'llm_call_end',
        duration,
        ...result,
      });

      // LLM専用メトリクス記録
      if (typeof window !== 'undefined') {
        monitor.recordCustomEvent('llm_call', {
          provider,
          model,
          promptLength,
          duration,
          callId,
          ...result,
        });
      }
    },
  };
}

// フォーム送信監視
export function trackFormSubmission(formName: string, fields: string[]) {
  const startTime = Date.now();
  const submissionId = crypto.randomUUID();

  console.log('Form submission started', {
    submissionId,
    formName,
    fields,
    timestamp: new Date().toISOString(),
    type: 'form_submission_start',
  });

  return {
    submissionId,
    complete: (result: {
      success: boolean;
      validationErrors?: string[];
      error?: string;
    }) => {
      const duration = Date.now() - startTime;

      console.log('Form submission completed', {
        submissionId,
        formName,
        timestamp: new Date().toISOString(),
        type: 'form_submission_end',
        duration,
        ...result,
      });

      // フォーム送信メトリクス記録
      if (typeof window !== 'undefined') {
        monitor.recordCustomEvent('form_submission', {
          formName,
          fields,
          duration,
          submissionId,
          ...result,
        });
      }
    },
  };
}

// ユーザーセッション監視
export function initializeSessionTracking() {
  if (typeof window === 'undefined') return;

  const sessionStart = Date.now();
  const sessionId = monitor.getSessionInfo().sessionId;

  console.log('User session started', {
    sessionId,
    timestamp: new Date().toISOString(),
    type: 'session_start',
    userAgent: navigator.userAgent,
    screen: {
      width: screen.width,
      height: screen.height,
    },
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight,
    },
  });

  // セッション終了時の処理
  const handleSessionEnd = () => {
    const sessionDuration = Date.now() - sessionStart;

    console.log('User session ended', {
      sessionId,
      timestamp: new Date().toISOString(),
      type: 'session_end',
      duration: sessionDuration,
    });

    monitor.recordCustomEvent('session_end', {
      sessionId,
      duration: sessionDuration,
    });
  };

  // ページ離脱時のイベントリスナー
  window.addEventListener('beforeunload', handleSessionEnd);
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      handleSessionEnd();
    }
  });

  // 定期的なセッション活動記録（5分間隔）
  const heartbeatInterval = setInterval(() => {
    const sessionDuration = Date.now() - sessionStart;

    monitor.recordCustomEvent('session_heartbeat', {
      sessionId,
      duration: sessionDuration,
      timestamp: new Date().toISOString(),
    });
  }, 5 * 60 * 1000);

  // クリーンアップ
  return () => {
    clearInterval(heartbeatInterval);
    window.removeEventListener('beforeunload', handleSessionEnd);
  };
}

// React エラーバウンダリー用のエラーレポーター
export function reportReactError(error: Error, errorInfo: any) {
  console.error('React error boundary triggered', {
    timestamp: new Date().toISOString(),
    type: 'react_error',
    error: error.message,
    stack: error.stack,
    componentStack: errorInfo?.componentStack,
  });

  if (typeof window !== 'undefined') {
    monitor.recordError({
      timestamp: new Date().toISOString(),
      type: 'render',
      message: error.message,
      stack: error.stack,
      url: window.location.href,
      userAgent: navigator.userAgent,
      sessionId: monitor.getSessionInfo().sessionId,
      userId: monitor.getSessionInfo().userId,
    });
  }
}

export default {
  observabilityMiddleware,
  withObservability,
  withComponentObservability,
  trackPromptProcessing,
  trackLLMCall,
  trackFormSubmission,
  initializeSessionTracking,
  reportReactError,
};
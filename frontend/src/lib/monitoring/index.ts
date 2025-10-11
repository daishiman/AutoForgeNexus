/**
 * クライアント側監視システム
 * Web Vitals、エラー追跡、パフォーマンス測定を統合
 */

export { reportWebVitals } from './web-vitals';

// エラー追跡
export interface ErrorInfo {
  message: string;
  stack?: string;
  componentStack?: string;
  timestamp: number;
  url: string;
  userAgent: string;
}

class MonitoringService {
  private static instance: MonitoringService;
  private analyticsUrl: string;

  private constructor() {
    this.analyticsUrl = process.env.NEXT_PUBLIC_ANALYTICS_URL || '/api/analytics';
  }

  public static getInstance(): MonitoringService {
    if (!MonitoringService.instance) {
      MonitoringService.instance = new MonitoringService();
    }
    return MonitoringService.instance;
  }

  /**
   * エラーを追跡システムに送信
   */
  public trackError(error: Error, errorInfo?: { componentStack?: string }): void {
    const errorData: ErrorInfo = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo?.componentStack,
      timestamp: Date.now(),
      url: typeof window !== 'undefined' ? window.location.href : '',
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
    };

    this.sendToAnalytics('error', errorData);
  }

  /**
   * カスタムイベントを追跡
   */
  public trackEvent(eventName: string, properties?: Record<string, unknown>): void {
    const eventData = {
      event_name: eventName,
      timestamp: Date.now(),
      url: typeof window !== 'undefined' ? window.location.href : '',
      properties,
    };

    this.sendToAnalytics('event', eventData);
  }

  /**
   * パフォーマンスメトリクスを測定
   */
  public measurePerformance(name: string, startTime: number): void {
    const duration = performance.now() - startTime;

    const perfData = {
      name,
      duration,
      timestamp: Date.now(),
      url: typeof window !== 'undefined' ? window.location.href : '',
    };

    this.sendToAnalytics('performance', perfData);
  }

  /**
   * データを分析エンドポイントに送信
   */
  private sendToAnalytics(type: string, data: unknown): void {
    if (typeof window === 'undefined') return;

    const body = JSON.stringify({
      type,
      data,
      dsn: process.env.NEXT_PUBLIC_ANALYTICS_ID,
    });

    if (navigator.sendBeacon) {
      navigator.sendBeacon(this.analyticsUrl, body);
    } else {
      fetch(this.analyticsUrl, {
        body,
        method: 'POST',
        keepalive: true,
        headers: {
          'Content-Type': 'application/json',
        },
      }).catch((err) => {
        // エラー送信の失敗は無視（無限ループ防止）
        console.error('Failed to send analytics:', err);
      });
    }
  }
}

// シングルトンインスタンスをエクスポート
export const monitoring = MonitoringService.getInstance();

// ユーティリティ関数
export const trackError = (error: Error, errorInfo?: { componentStack?: string }) => {
  monitoring.trackError(error, errorInfo);
};

export const trackEvent = (eventName: string, properties?: Record<string, unknown>) => {
  monitoring.trackEvent(eventName, properties);
};

export const measurePerformance = (name: string, startTime: number) => {
  monitoring.measurePerformance(name, startTime);
};

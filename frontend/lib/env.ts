/**
 * フロントエンド環境変数管理
 * Next.jsの環境変数を型安全に扱う
 */

// 環境変数の型定義
interface ClientEnv {
  // App Config
  APP_NAME: string;
  APP_URL: string;
  API_URL: string;
  WS_URL: string;

  // API Config
  API_BASE_URL: string;
  API_TIMEOUT: number;

  // WebSocket Config
  WS_BASE_URL: string;
  WS_RECONNECT_INTERVAL: number;
  WS_MAX_RECONNECT_ATTEMPTS: number;

  // Clerk Auth
  CLERK_PUBLISHABLE_KEY: string;
  CLERK_SIGN_IN_URL: string;
  CLERK_SIGN_UP_URL: string;
  CLERK_AFTER_SIGN_IN_URL: string;
  CLERK_AFTER_SIGN_UP_URL: string;

  // Feature Flags
  ENABLE_ANALYTICS: boolean;
  ENABLE_PWA: boolean;
  ENABLE_DARK_MODE: boolean;
  ENABLE_EXPERIMENTAL_FEATURES: boolean;
  ENABLE_DEBUG_TOOLBAR: boolean;

  // Analytics (Optional)
  GA_MEASUREMENT_ID?: string;
  POSTHOG_KEY?: string;
  POSTHOG_HOST?: string;

  // Error Tracking (Optional)
  SENTRY_DSN?: string;
  SENTRY_ENVIRONMENT?: string;

  // Theme
  THEME_PRIMARY_COLOR: string;
  THEME_SECONDARY_COLOR: string;

  // Localization
  DEFAULT_LOCALE: string;
  SUPPORTED_LOCALES: string[];

  // Cache
  CACHE_TTL: number;
  USE_LOCAL_STORAGE: boolean;
  USE_SESSION_STORAGE: boolean;

  // Rate Limiting
  API_RATE_LIMIT: number;
  API_RATE_WINDOW: number;
}

// サーバーサイド環境変数の型定義
interface ServerEnv {
  CLERK_SECRET_KEY?: string;
  // その他サーバー限定の環境変数
}

// 環境変数のバリデーションと取得
class EnvironmentConfig {
  private static instance: EnvironmentConfig;

  private constructor() {
    // シングルトンパターン
  }

  static getInstance(): EnvironmentConfig {
    if (!EnvironmentConfig.instance) {
      EnvironmentConfig.instance = new EnvironmentConfig();
    }
    return EnvironmentConfig.instance;
  }

  /**
   * クライアントサイド環境変数を取得
   * NEXT_PUBLIC_プレフィックスが必要
   */
  getClientEnv(): ClientEnv {
    return {
      // App Config
      APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'AutoForgeNexus',
      APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
      API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000',

      // API Config
      API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
      API_TIMEOUT: parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || '30000'),

      // WebSocket Config
      WS_BASE_URL: process.env.NEXT_PUBLIC_WS_BASE_URL || 'ws://localhost:8000/ws',
      WS_RECONNECT_INTERVAL: parseInt(process.env.NEXT_PUBLIC_WS_RECONNECT_INTERVAL || '5000'),
      WS_MAX_RECONNECT_ATTEMPTS: parseInt(process.env.NEXT_PUBLIC_WS_MAX_RECONNECT_ATTEMPTS || '5'),

      // Clerk Auth
      CLERK_PUBLISHABLE_KEY: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || '',
      CLERK_SIGN_IN_URL: process.env.NEXT_PUBLIC_CLERK_SIGN_IN_URL || '/sign-in',
      CLERK_SIGN_UP_URL: process.env.NEXT_PUBLIC_CLERK_SIGN_UP_URL || '/sign-up',
      CLERK_AFTER_SIGN_IN_URL: process.env.NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL || '/dashboard',
      CLERK_AFTER_SIGN_UP_URL: process.env.NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL || '/onboarding',

      // Feature Flags
      ENABLE_ANALYTICS: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
      ENABLE_PWA: process.env.NEXT_PUBLIC_ENABLE_PWA === 'true',
      ENABLE_DARK_MODE: process.env.NEXT_PUBLIC_ENABLE_DARK_MODE !== 'false',
      ENABLE_EXPERIMENTAL_FEATURES: process.env.NEXT_PUBLIC_ENABLE_EXPERIMENTAL_FEATURES === 'true',
      ENABLE_DEBUG_TOOLBAR: process.env.NEXT_PUBLIC_ENABLE_DEBUG_TOOLBAR === 'true',

      // Analytics (Optional)
      GA_MEASUREMENT_ID: process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID,
      POSTHOG_KEY: process.env.NEXT_PUBLIC_POSTHOG_KEY,
      POSTHOG_HOST: process.env.NEXT_PUBLIC_POSTHOG_HOST,

      // Error Tracking (Optional)
      SENTRY_DSN: process.env.NEXT_PUBLIC_SENTRY_DSN,
      SENTRY_ENVIRONMENT: process.env.NEXT_PUBLIC_SENTRY_ENVIRONMENT,

      // Theme
      THEME_PRIMARY_COLOR: process.env.NEXT_PUBLIC_THEME_PRIMARY_COLOR || '#6366f1',
      THEME_SECONDARY_COLOR: process.env.NEXT_PUBLIC_THEME_SECONDARY_COLOR || '#8b5cf6',

      // Localization
      DEFAULT_LOCALE: process.env.NEXT_PUBLIC_DEFAULT_LOCALE || 'ja',
      SUPPORTED_LOCALES: (process.env.NEXT_PUBLIC_SUPPORTED_LOCALES || 'ja,en').split(','),

      // Cache
      CACHE_TTL: parseInt(process.env.NEXT_PUBLIC_CACHE_TTL || '3600'),
      USE_LOCAL_STORAGE: process.env.NEXT_PUBLIC_USE_LOCAL_STORAGE !== 'false',
      USE_SESSION_STORAGE: process.env.NEXT_PUBLIC_USE_SESSION_STORAGE === 'true',

      // Rate Limiting
      API_RATE_LIMIT: parseInt(process.env.NEXT_PUBLIC_API_RATE_LIMIT || '100'),
      API_RATE_WINDOW: parseInt(process.env.NEXT_PUBLIC_API_RATE_WINDOW || '60000'),
    };
  }

  /**
   * サーバーサイド環境変数を取得
   * サーバーコンポーネントでのみ使用可能
   */
  getServerEnv(): ServerEnv {
    if (typeof window !== 'undefined') {
      throw new Error('getServerEnv() can only be called on the server side');
    }

    return {
      CLERK_SECRET_KEY: process.env.CLERK_SECRET_KEY,
      // その他サーバー限定の環境変数
    };
  }

  /**
   * 現在の環境を取得
   */
  getEnvironment(): 'local' | 'staging' | 'production' {
    const appUrl = this.getClientEnv().APP_URL;

    if (appUrl.includes('localhost')) return 'local';
    if (appUrl.includes('staging') || appUrl.includes('preview')) return 'staging';
    return 'production';
  }

  /**
   * 開発環境かどうか
   */
  isDevelopment(): boolean {
    return this.getEnvironment() === 'local';
  }

  /**
   * 本番環境かどうか
   */
  isProduction(): boolean {
    return this.getEnvironment() === 'production';
  }

  /**
   * デバッグ情報を出力（開発環境のみ）
   */
  debug(): void {
    if (!this.isDevelopment()) return;

    const env = this.getClientEnv();
    // eslint-disable-next-line no-console
    console.log('🔧 Environment Configuration');
    // eslint-disable-next-line no-console
    console.log('============================');
    // eslint-disable-next-line no-console
    console.log('Environment:', this.getEnvironment());
    // eslint-disable-next-line no-console
    console.log('API URL:', env.API_BASE_URL);
    // eslint-disable-next-line no-console
    console.log('WebSocket URL:', env.WS_BASE_URL);
    // eslint-disable-next-line no-console
    console.log('Feature Flags:', {
      analytics: env.ENABLE_ANALYTICS,
      pwa: env.ENABLE_PWA,
      darkMode: env.ENABLE_DARK_MODE,
      experimental: env.ENABLE_EXPERIMENTAL_FEATURES,
      debugToolbar: env.ENABLE_DEBUG_TOOLBAR,
    });
    // eslint-disable-next-line no-console
    console.log('============================');
  }
}

// エクスポート
export const env = EnvironmentConfig.getInstance();
export const clientEnv = env.getClientEnv();

// 型エクスポート
export type { ClientEnv, ServerEnv };

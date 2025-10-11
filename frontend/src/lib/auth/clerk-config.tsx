import { ClerkProvider } from '@clerk/nextjs';
import type { PropsWithChildren } from 'react';

export const clerkConfig = {
  // 外観設定
  appearance: {
    elements: {
      rootBox: 'w-full',
      card: 'shadow-xl',
      headerTitle: 'text-2xl font-bold',
      headerSubtitle: 'text-muted-foreground',
      socialButtonsBlockButton: 'hover:opacity-90 transition-opacity',
      formButtonPrimary: 'bg-primary hover:opacity-90',
      footerActionLink: 'text-primary hover:underline',
    },
    layout: {
      socialButtonsPlacement: 'top' as const,
      socialButtonsVariant: 'blockButton' as const,
      termsPageUrl: '/terms',
      privacyPageUrl: '/privacy',
      helpPageUrl: '/help',
    },
    variables: {
      colorPrimary: '#2563eb',
      colorText: '#000000',
      colorTextSecondary: '#666666',
      colorBackground: '#ffffff',
      colorInputBackground: '#ffffff',
      colorInputText: '#000000',
      fontFamily: 'Inter, system-ui, sans-serif',
      borderRadius: '0.5rem',
    },
  },

  // サインイン設定
  signIn: {
    afterSignInUrl: '/dashboard',
    fallbackRedirectUrl: '/dashboard',
    routing: 'path' as const,
  },

  // サインアップ設定
  signUp: {
    afterSignUpUrl: '/onboarding',
    fallbackRedirectUrl: '/onboarding',
    routing: 'path' as const,
  },

  // 組織設定
  organizationProfile: {
    afterLeaveOrganizationUrl: '/organizations',
    afterCreateOrganizationUrl: '/organization/:id',
  },

  // 多要素認証
  multiFactorAuthentication: {
    enabled: true,
    factors: ['totp', 'sms'],
  },
};

// Clerkプロバイダーラッパー
export function AuthProvider({ children }: PropsWithChildren) {
  return <ClerkProvider>{children}</ClerkProvider>;
}

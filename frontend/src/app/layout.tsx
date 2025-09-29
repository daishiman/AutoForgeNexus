import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import '@/styles/globals.css';
import WebVitalsProvider from '@/components/providers/WebVitalsProvider';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-sans',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
});

export const metadata: Metadata = {
  title: 'AutoForge Nexus - AIプロンプト最適化プラットフォーム',
  description: '高品質なAIプロンプトの作成・最適化・管理を支援する統合プラットフォーム',
  keywords: ['AI', 'プロンプト', '最適化', 'LLM', '自動化'],
  authors: [{ name: 'AutoForge Nexus Team' }],
  creator: 'AutoForge Nexus',
  publisher: 'AutoForge Nexus',
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    locale: 'ja_JP',
    url: 'https://autoforge-nexus.pages.dev',
    title: 'AutoForge Nexus',
    description: '高品質なAIプロンプトの作成・最適化・管理を支援する統合プラットフォーム',
    siteName: 'AutoForge Nexus',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'AutoForge Nexus',
    description: '高品質なAIプロンプトの作成・最適化・管理を支援する統合プラットフォーム',
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  manifest: '/manifest.json',
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body className="min-h-screen bg-background font-sans antialiased">
        <WebVitalsProvider>
          {children}
        </WebVitalsProvider>
      </body>
    </html>
  );
}
/** @type {import('next').NextConfig} */

const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true'
})

const nextConfig = {
  // React 19 Optimizations
  experimental: {
    // React 19 Features
    ppr: true, // Partial Prerendering
    reactCompiler: true, // React Compiler
    turbo: {
      loaders: {
        '.svg': ['@svgr/webpack']
      }
    },
    optimizePackageImports: [
      '@headlessui/react',
      '@heroicons/react',
      'framer-motion',
      'lucide-react'
    ],
    // Performance optimizations
    serverMinification: true,
    instrumentationHook: true,
    webpackBuildWorker: true
  },

  // TypeScript & ESLint
  typescript: {
    ignoreBuildErrors: false
  },
  eslint: {
    ignoreDuringBuilds: false,
    dirs: ['src']
  },

  // Performance & Optimization
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn']
    } : false
  },
  swcMinify: true,
  poweredByHeader: false,
  compress: true,

  // Images
  images: {
    formats: ['image/avif', 'image/webp'],
    minimumCacheTTL: 31536000, // 1 year
    dangerouslyAllowSVG: true,
    contentDispositionType: 'attachment',
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;"
  },

  // Headers for security and performance
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          }
        ]
      },
      {
        source: '/api/(.*)',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store, must-revalidate'
          }
        ]
      }
    ]
  },

  // Redirects & Rewrites
  async redirects() {
    return [
      {
        source: '/dashboard',
        destination: '/dashboard/overview',
        permanent: false
      }
    ]
  },

  // Bundle optimization
  webpack: (config, { dev, isServer }) => {
    // Bundle analysis
    if (process.env.ANALYZE === 'true') {
      config.resolve.alias = {
        ...config.resolve.alias,
        '@': require('path').resolve(__dirname, 'src')
      }
    }

    // Production optimizations
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: 'all',
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: 'vendors',
            chunks: 'all'
          },
          ui: {
            test: /[\\/]src[\\/]components[\\/]/,
            name: 'ui',
            chunks: 'all',
            enforce: true
          }
        }
      }
    }

    return config
  },

  // Environment variables for client
  env: {
    NEXT_PUBLIC_APP_VERSION: process.env.npm_package_version || '1.0.0',
    NEXT_PUBLIC_BUILD_TIME: new Date().toISOString()
  },

  // Output configuration
  output: 'standalone',
  distDir: '.next',

  // Development configuration
  ...(process.env.NODE_ENV === 'development' && {
    // React Strict Mode
    reactStrictMode: true,
    // Fast Refresh
    fastRefresh: true
  })
}

module.exports = withBundleAnalyzer(nextConfig)
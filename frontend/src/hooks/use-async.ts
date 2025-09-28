import { use, useCallback, useState } from 'react'

// React 19のuse() APIを活用した非同期データフック
export function useAsync<T>(promise: Promise<T> | null) {
  if (!promise) return { data: null, loading: false, error: null }

  try {
    const data = use(promise)
    return { data, loading: false, error: null }
  } catch (error) {
    if (error instanceof Promise) {
      throw error // Suspenseで処理
    }
    return { data: null, loading: false, error: error as Error }
  }
}

// 非同期アクション実行フック
export function useAsyncAction<T extends (...args: any[]) => Promise<any>>() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  const execute = useCallback(async (action: T, ...args: Parameters<T>) => {
    setLoading(true)
    setError(null)

    try {
      const result = await action(...args)
      return result
    } catch (err) {
      const error = err as Error
      setError(error)
      throw error
    } finally {
      setLoading(false)
    }
  }, [])

  return { execute, loading, error }
}
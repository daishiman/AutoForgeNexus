'use client';

import { useEffect } from 'react';
import { reportWebVitals } from '@/lib/monitoring/web-vitals';

export default function WebVitalsProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    reportWebVitals();
  }, []);

  return <>{children}</>;
}
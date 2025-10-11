import { onCLS, onFID, onFCP, onLCP, onTTFB } from 'web-vitals';

type MetricType = 'CLS' | 'FID' | 'FCP' | 'LCP' | 'TTFB';

interface Metric {
  id: string;
  name: MetricType;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  delta: number;
  entries: unknown[];
}

const vitalsUrl = process.env.NEXT_PUBLIC_ANALYTICS_URL || '/api/analytics';

function sendToAnalytics(metric: Metric) {
  const body = JSON.stringify({
    dsn: process.env.NEXT_PUBLIC_ANALYTICS_ID,
    id: metric.id,
    page: window.location.pathname,
    href: window.location.href,
    event_name: metric.name,
    value: metric.value.toString(),
    speed: metric.rating,
  });

  if (navigator.sendBeacon) {
    navigator.sendBeacon(vitalsUrl, body);
  } else {
    fetch(vitalsUrl, {
      body,
      method: 'POST',
      keepalive: true,
    });
  }
}

export function reportWebVitals() {
  onCLS(sendToAnalytics);
  onFID(sendToAnalytics);
  onFCP(sendToAnalytics);
  onLCP(sendToAnalytics);
  onTTFB(sendToAnalytics);
}

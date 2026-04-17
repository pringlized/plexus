import type { Severity } from './types';

export type LayerStatus = 'healthy' | Severity;

export function relativeTime(ts: number, nowMs: number): string {
  const diff = Math.max(0, nowMs - ts);
  if (diff < 1500) return 'now';
  const s = Math.floor(diff / 1000);
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return `${h}h ago`;
}

export function severityClass(s: Severity): string {
  return {
    info: 'bg-sev-info/15 text-sev-info',
    notice: 'bg-sev-notice/15 text-sev-notice',
    warning: 'bg-sev-warning/20 text-sev-warning',
    anomaly: 'bg-sev-anomaly/20 text-sev-anomaly',
    critical: 'bg-sev-critical/25 text-sev-critical'
  }[s];
}

export function statusDot(s: LayerStatus): string {
  return {
    healthy: 'bg-sev-healthy',
    info: 'bg-sev-info',
    notice: 'bg-sev-notice',
    warning: 'bg-sev-warning',
    anomaly: 'bg-sev-anomaly',
    critical: 'bg-sev-critical'
  }[s];
}

export function statusLabel(s: LayerStatus): string {
  return s.toUpperCase();
}

export function basename(path: string): string {
  return path.split('/').pop() ?? path;
}

export function shortHash(pinchId: string, n = 8): string {
  return pinchId.slice(0, n);
}

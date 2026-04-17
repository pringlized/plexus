import type { HealthStatus, Severity } from './types';

export function relativeTime(ts: number, now: number): string {
  const diff = Math.max(0, now - ts);
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

export function severityRing(s: Severity | HealthStatus): string {
  return {
    healthy: 'ring-sev-healthy/50',
    info: 'ring-sev-info/40',
    notice: 'ring-sev-notice/50',
    warning: 'ring-sev-warning/60',
    anomaly: 'ring-sev-anomaly/70',
    critical: 'ring-sev-critical/80'
  }[s as 'healthy'];
}

export function healthDot(h: HealthStatus): string {
  return {
    healthy: 'bg-sev-healthy',
    warning: 'bg-sev-warning',
    anomaly: 'bg-sev-anomaly',
    critical: 'bg-sev-critical'
  }[h];
}

export function healthLabel(h: HealthStatus): string {
  return h.toUpperCase();
}

export function severityRank(s: Severity): number {
  return { info: 0, notice: 1, warning: 2, anomaly: 3, critical: 4 }[s];
}

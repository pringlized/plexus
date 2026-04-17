import type { LayerId, PlexusNode, Receptor, Severity } from './types';

export const LAYERS: { id: LayerId; name: string; blurb: string }[] = [
  { id: 'security', name: 'Security', blurb: 'Character & pattern threat detection' },
  { id: 'ingestion', name: 'Ingestion', blurb: 'Knowledge pipeline events' },
  { id: 'build', name: 'Build', blurb: 'Build chain & pipeline state' }
];

export const NODES: PlexusNode[] = [
  {
    id: 'node-001',
    name: 'glassglyph-scanner-01',
    type: 'security',
    layer: 'security',
    description: 'Sub-ms char-level scanner for invisible unicode / homoglyph attacks.'
  },
  {
    id: 'node-002',
    name: 'auth-monitor-01',
    type: 'security',
    layer: 'security',
    description: 'Watches login patterns for credential-stuffing and anomalies.'
  },
  {
    id: 'node-003',
    name: 'ma-ingestion-01',
    type: 'ingestion',
    layer: 'ingestion',
    description: 'Mens Altera ingestion pipeline — document receipt and routing.'
  },
  {
    id: 'node-004',
    name: 'embedding-pipeline-01',
    type: 'ingestion',
    layer: 'ingestion',
    description: 'Vector embedding worker. Emits per-document completions.'
  },
  {
    id: 'node-005',
    name: 'buildengine-01',
    type: 'build',
    layer: 'build',
    description: 'Build chain executor. Emits on stage transitions.'
  },
  {
    id: 'node-006',
    name: 'pipeline-monitor-01',
    type: 'pipeline',
    layer: 'build',
    description: 'Workflow state machine — tracks stalls and stage durations.'
  }
];

export const RECEPTORS: Receptor[] = [
  {
    id: 'rec-001',
    name: 'security-alerter',
    type: 'alerter',
    listensTo: ['node-001', 'node-002'],
    firesOn: ['warning', 'anomaly', 'critical'],
    description: 'Dispatches security notifications to Vector/Telegram.',
    action: 'alert dispatched'
  },
  {
    id: 'rec-002',
    name: 'health-aggregator',
    type: 'health-aggregator',
    listensTo: '*',
    firesOn: '*',
    description: 'Rolls node signals into system-layer health status.',
    action: 'layer updated'
  },
  {
    id: 'rec-003',
    name: 'logger',
    type: 'logger',
    listensTo: '*',
    firesOn: '*',
    description: 'Structured log output. Every signal is recorded.',
    action: 'logged'
  },
  {
    id: 'rec-004',
    name: 'agent-invoker',
    type: 'agent-invoker',
    listensTo: ['node-001'],
    firesOn: ['critical'],
    description: 'Dispatches a specialist agent when a critical security signal fires.',
    action: 'agent dispatched'
  }
];

// ---- Payload templates -------------------------------------------------

const DOC_IDS = ['doc-8819', 'doc-8820', 'doc-8821', 'doc-8822', 'doc-8823', 'doc-8824', 'doc-8825'];
const pickDoc = () => DOC_IDS[Math.floor(Math.random() * DOC_IDS.length)];

export function glassglyphPayload(sev: Severity) {
  if (sev === 'critical') {
    return {
      threat_category: 'invisible_unicode_encoding',
      severity: 'critical',
      action_taken: 'block',
      findings: [
        {
          range: 'U+FE01-U+FE0F',
          name: 'Variation selectors',
          description: 'Glassworm substitution cipher detected',
          character_ranges: [[65024, 65039]]
        }
      ],
      document_id: pickDoc(),
      source: 'ma-ingestion-pipeline',
      scan_duration_ms: +(0.3 + Math.random() * 0.3).toFixed(2)
    };
  }
  if (sev === 'anomaly' || sev === 'warning') {
    return {
      threat_category: 'bidi_override',
      severity: sev === 'anomaly' ? 'high' : 'medium',
      action_taken: 'strip',
      findings: [
        {
          range: 'U+202E',
          name: 'Right-to-left override',
          description: 'Bidi control character removed'
        }
      ],
      document_id: pickDoc(),
      scan_duration_ms: +(0.2 + Math.random() * 0.3).toFixed(2)
    };
  }
  return {
    threat_category: null,
    severity: 'info',
    action_taken: 'none',
    findings: [],
    document_id: pickDoc(),
    scan_duration_ms: +(0.1 + Math.random() * 0.2).toFixed(2)
  };
}

export function authPayload(sev: Severity) {
  if (sev === 'warning') {
    return {
      event: 'unusual_pattern',
      user_id: `u-${Math.floor(Math.random() * 9000 + 1000)}`,
      source_ip: `10.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
      attempts: Math.floor(Math.random() * 6 + 4),
      window_s: 60
    };
  }
  return {
    event: 'session_ok',
    user_id: `u-${Math.floor(Math.random() * 9000 + 1000)}`
  };
}

export function ingestionPayload(sev: Severity) {
  if (sev === 'anomaly') {
    return {
      event: 'pipeline_stall',
      stage: 'chunking',
      stalled_ms: 4200 + Math.floor(Math.random() * 2000),
      queue_depth: Math.floor(Math.random() * 40 + 20)
    };
  }
  return {
    event: 'document.received',
    document_id: pickDoc(),
    bytes: Math.floor(Math.random() * 800 + 200) * 1024
  };
}

export function embeddingPayload() {
  return {
    event: 'document.embedded',
    document_id: pickDoc(),
    model: 'voyage-3-large',
    vectors: Math.floor(Math.random() * 40 + 8),
    ms: Math.floor(Math.random() * 250 + 40)
  };
}

export function buildPayload(sev: Severity) {
  const stages = ['deps', 'compile', 'test', 'package'];
  const stage = stages[Math.floor(Math.random() * stages.length)];
  if (sev === 'warning') {
    return {
      event: 'stage.slow',
      stage,
      expected_ms: 800,
      observed_ms: 1800 + Math.floor(Math.random() * 1200)
    };
  }
  return {
    event: 'dependency.resolved',
    stage,
    ms: Math.floor(Math.random() * 500 + 80)
  };
}

export function pipelinePayload() {
  const stages = ['queued', 'running', 'completed'];
  return {
    event: 'stage.transition',
    from: stages[Math.floor(Math.random() * stages.length)],
    to: stages[Math.floor(Math.random() * stages.length)],
    feature_id: Math.floor(Math.random() * 500 + 100)
  };
}

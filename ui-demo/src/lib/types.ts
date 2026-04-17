export type Severity = 'info' | 'notice' | 'warning' | 'anomaly' | 'critical';

// ---- Wire envelope from Python hub ------------------------------------

export interface ActionResult {
  batch: string | null;
  actions_fired: string[];
  ok: boolean;
  detail?: string | null;
}

export interface SignalEvent {
  pinch_id: string;
  name: string | null;
  layer: string | null;
  severity: Severity;
  source_file: string;
  source_line: number;
  source_function: string;
  payload: Record<string, unknown>;
  timestamp: string; // ISO 8601
  action: string | null;
  action_result: ActionResult | null;
  received_at: number; // set by client store on receipt
}

// ---- Derived view models ----------------------------------------------

export interface NodeSummary {
  pinch_id: string;
  name: string | null;
  layer: string | null;
  source_file: string;
  source_function: string;
  last_severity: Severity;
  last_seen: number;
  signal_count: number;
}

// ---- Action / batch config from plexus-actions.yaml -------------------

export interface ActionConfig {
  name: string;
  enabled: boolean;
  [key: string]: unknown;
}

export interface BatchConfig {
  name: string;
  actions: string[];
}

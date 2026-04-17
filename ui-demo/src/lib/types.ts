export type NodeType = 'security' | 'ingestion' | 'build' | 'agent' | 'health' | 'pipeline';
export type Severity = 'info' | 'notice' | 'warning' | 'anomaly' | 'critical';
export type HealthStatus = 'healthy' | 'warning' | 'anomaly' | 'critical';

export interface NodeConfig {
  uuid: string;
  type: NodeType;
  layer: string;
  description: string;
}

export interface ReceptorConfig {
  uuid: string;
  type: string;
  description: string;
  listens_to: string[];
  config: {
    severity_filter?: string[];
    alert_label?: string;
    [key: string]: unknown;
  };
}

export interface PlexusConfig {
  nodes: Record<string, NodeConfig>;
  receptors: Record<string, ReceptorConfig>;
}

export interface LayerSummary {
  name: string;
  description: string;
  nodes: Array<{ shortId: string; config: NodeConfig }>;
}

// ---- Signal event (from PlexusHub via POST /api/signal) ------------------

export interface SignalData {
  signal_id: string;
  node_short_id: string;
  node_uuid: string;
  node_type: string;
  node_layer: string;
  node_description: string;
  timestamp: string; // ISO 8601
  severity: Severity;
  category: string;
  payload: Record<string, unknown>;
  sequence: number;
  source_file: string | null;
  source_line: number | null;
  source_function: string | null;
}

export interface ReceptorResultData {
  receptor_id: string;
  receptor_type: string;
  action: 'discard' | 'flag' | 'flag+action';
  flag_reason: string | null;
}

export interface SignalEvent {
  signal: SignalData;
  receptor_results: ReceptorResultData[];
  received_at: number; // Date.now() set by the API route on receipt
}

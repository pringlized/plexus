export type Severity = 'info' | 'notice' | 'warning' | 'anomaly' | 'critical';
export type LayerId = 'security' | 'ingestion' | 'build';
export type LayerHealth = 'healthy' | 'warning' | 'anomaly' | 'critical';
export type NodeType = 'security' | 'ingestion' | 'build' | 'agent' | 'health' | 'pipeline';
export type ReceptorType =
  | 'alerter'
  | 'logger'
  | 'health-aggregator'
  | 'agent-invoker'
  | 'threshold-watcher';

export interface PlexusNode {
  id: string;
  name: string;
  type: NodeType;
  layer: LayerId;
  description: string;
}

export interface Receptor {
  id: string;
  name: string;
  type: ReceptorType;
  listensTo: string[] | '*'; // node ids or '*' for all
  firesOn: Severity[] | '*';
  description: string;
  action?: string;
}

export interface Signal {
  signal_id: string;
  node_id: string;
  node_type: NodeType;
  timestamp: number;
  severity: Severity;
  category: string;
  payload: Record<string, unknown>;
  system_layer: LayerId;
  sequence: number;
}

export interface Receipt {
  id: string;
  receptor_id: string;
  signal_id: string;
  node_id: string;
  severity: Severity;
  timestamp: number;
  ok: boolean;
  summary: string;
}

export type ActionStatus = 'pending' | 'completed' | 'failed';

export interface ReceptorAction {
  id: string;
  receptor_id: string;
  signal_id: string;
  node_id: string;
  timestamp: number;
  action: string;
  status: ActionStatus;
  detail: string;
  duration_ms?: number;
}

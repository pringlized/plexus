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

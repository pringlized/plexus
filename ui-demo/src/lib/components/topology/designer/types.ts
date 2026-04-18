export interface DesignerNode {
  pinch_id: string;
  name: string;
  layer: string;
  source_function: string;
  last_severity: 'info' | 'notice' | 'warning' | 'anomaly' | 'critical';
}

export interface DesignerAction {
  name: string;
  enabled: boolean;
}

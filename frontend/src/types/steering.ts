export interface SteeringStatus {
  active: boolean;
  preset: string | null;
  alpha: number | null;
  layer: number | null;
  vector_norm: number | null;
}

export interface Preset {
  name: string;
  description: string;
  default_alpha: number;
  target_layer: number | null;
}

export interface CompareResult {
  unsteered: string;
  steered: string;
  metrics: {
    unsteered_tokens: number;
    steered_tokens: number;
    token_delta_percentage: number;
    unsteered_latency_ms: number;
    steered_latency_ms: number;
  };
}

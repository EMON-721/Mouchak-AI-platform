export type Lang = "bn" | "en";
export type User = {
  id: string;
  email: string;
  name: string;
  role: string;
  verified: boolean;
  mfa_enabled: boolean;
  language: string;
};
export type Column = {
  key: string;
  bn: string;
  en: string;
  type: string;
  help_bn?: string;
  help_en?: string;
  placeholder_bn?: string;
  placeholder_en?: string;
};
export type FieldSpec = Column & {
  optional?: boolean;
  options?: string[];
  columns?: Column[];
};
export type Tool = {
  name: string;
  slug: string;
  category: string;
  number: number;
  inputs: string;
  outputs: string;
  safety: string;
  signature: string;
  ai: string;
  engine: string;
  logo: string;
  description_en: string;
  description_bn: string;
  release_status: string;
  enabled?: boolean;
  execution_mode?: "queued" | "synchronous";
  fields?: FieldSpec[];
  presentation_base?: {
    name: string;
    logo: string;
    description_bn: string;
    description_en: string;
    fields?: FieldSpec[];
  };
};
export type RunResult = {
  id: string;
  module: string;
  method: string;
  model_version: string;
  status: string;
  facts: Record<string, unknown>;
  details: unknown;
  uncertainties: string[];
  references: Record<string, unknown>[];
  latency_ms?: number;
  created_at: string;
  full_module_complete: boolean;
};
export type Workspace = { id: string; name: string };

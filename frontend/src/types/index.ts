export interface Domain {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  version: string;
  is_default: boolean;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Subject {
  id: number;
  domain_id: number;
  name: string;
  display_name: string;
  description: string | null;
  age_min: number | null;
  age_max: number | null;
  difficulty_min: number | null;
  difficulty_max: number | null;
  sort_order: number;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface Concept {
  id: number;
  domain_id: number;
  subject_id: number;
  concept_id: string;
  name: string;
  description: string | null;
  age_min: number | null;
  age_max: number | null;
  difficulty: number | null;
  evidence_criteria: string | null;
  assessment_prompt: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ConceptPrerequisite {
  concept_id: number;
  prerequisite_id: number;
  weight: number;
}

export interface ConceptDetail extends Concept {
  prerequisites: ConceptPrerequisite[];
  dependents: ConceptPrerequisite[];
}

export interface ConceptListResponse {
  concepts: Concept[];
  total: number;
}

export interface DomainListResponse {
  domains: Domain[];
  total: number;
}

export interface GraphNode {
  id: number;
  concept_id: string;
  name: string;
  subject_id: number;
  difficulty: number | null;
}

export interface GraphEdge {
  source: number;
  target: number;
  weight: number;
}

export interface ConceptGraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ChildProfile {
  id: number;
  user_id: string;
  name: string;
  birth_date: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface ChildProfileListResponse {
  profiles: ChildProfile[];
  total: number;
}

export type ProgressState = 'not_started' | 'learning' | 'known' | 'assessed';

export interface ConceptProgress {
  id: number;
  child_profile_id: number;
  concept_id: number;
  state: ProgressState;
  evidence_notes: string | null;
  assessed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProgressListResponse {
  progress: ConceptProgress[];
  total: number;
}

export interface UserInfo {
  sub: string;
  email: string | null;
  name: string | null;
  roles: string[];
}

export interface TokenData {
  sub: string;
  email: string | null;
  roles: string[];
  aud: string | null;
}
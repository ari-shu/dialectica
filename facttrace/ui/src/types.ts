export interface Case {
  id: number;
  name: string;
  mutation_type: string;
  claim: string;
  truth: string;
}

export interface Setup {
  name: string;
  description: string;
  agents: string[];
  mode: string;
  synthesis: string | null;
}

export interface AgentInfo {
  name: string;
  color: string;
  role: string;
}

export interface AgentVerdict {
  agent_name: string;
  color: string;
  verdict: 'faithful' | 'mutation' | 'uncertain';
  confidence: number;
  reasoning: string;
  evidence: string[];
}

export interface AgentResponse {
  agent_name: string;
  color: string;
  response: string;
}

export interface FinalVerdict {
  verdict: 'faithful' | 'mutation' | 'uncertain';
  confidence: number;
  reasoning: string;
  mutation_type: string | null;
  dissenting?: string[];
}

export type DebateEvent =
  | { type: 'case'; data: Case }
  | { type: 'setup'; data: { name: string; description: string } }
  | { type: 'agents'; data: AgentInfo[] }
  | { type: 'phase'; data: string }
  | { type: 'status'; data: string }
  | { type: 'agent_thinking'; data: { agent_name: string; color: string } }
  | { type: 'agent_verdict'; data: AgentVerdict }
  | { type: 'debate_round'; data: number }
  | { type: 'agent_response'; data: AgentResponse }
  | { type: 'final_verdict'; data: FinalVerdict }
  | { type: 'done'; data: null };

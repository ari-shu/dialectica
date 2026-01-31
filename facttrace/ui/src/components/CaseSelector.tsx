import { Card, Select, Button, Typography, Segmented } from 'antd';
import { PlayCircleOutlined, PauseOutlined } from '@ant-design/icons';
import type { Case, Setup } from '../types';

const { Text } = Typography;

interface CaseSelectorProps {
  cases: Case[];
  setups: Record<string, Setup>;
  selectedCase: number | null;
  selectedSetup: string;
  selectedModel: string;
  onCaseChange: (caseId: number) => void;
  onSetupChange: (setup: string) => void;
  onModelChange: (model: string) => void;
  onStart: () => void;
  onStop: () => void;
  isRunning: boolean;
}

const AGENT_DETAILS: Record<string, { color: string; role: string; methodology: string; checks: string[] }> = {
  literalist: {
    color: '#ff4d4f',
    role: 'Pedantic Fact-Checker',
    methodology: 'Strict textual comparison. Any deviation in hard facts is a potential mutation.',
    checks: ['Exact numbers & dates', 'Temporal markers', 'Precise wording'],
  },
  contextualist: {
    color: '#1890ff',
    role: 'Context Analyzer',
    methodology: 'Evaluates if the claim preserves the spirit and implications of the source.',
    checks: ['Missing caveats', 'Omitted qualifiers', 'Shifted implications'],
  },
  statistician: {
    color: '#52c41a',
    role: 'Numerical Expert',
    methodology: 'Analyzes numerical presentation and whether framing is fair.',
    checks: ['Rounding accuracy', 'Date shifts', 'Statistical framing'],
  },
};

const SETUP_INFO: Record<string, { title: string; description: string }> = {
  single: {
    title: 'Single Agent',
    description: 'One general-purpose agent analyzes the claim. Fast but less thorough.',
  },
  'jury-vote': {
    title: '3-Agent Jury (Vote)',
    description: 'Three specialized agents analyze independently. Final verdict by confidence-weighted majority vote.',
  },
  'jury-llm': {
    title: '3-Agent Jury (LLM Judge)',
    description: 'Three specialized agents analyze independently. An LLM judge synthesizes the final verdict.',
  },
  'jury-deliberate': {
    title: '3-Agent Jury (Deliberation)',
    description: 'Agents analyze, then respond to each other before final synthesis. Most thorough.',
  },
};

export function CaseSelector({
  cases,
  setups,
  selectedCase,
  selectedSetup,
  selectedModel,
  onCaseChange,
  onSetupChange,
  onModelChange,
  onStart,
  onStop,
  isRunning,
}: CaseSelectorProps) {
  const currentSetup = setups[selectedSetup];
  const setupInfo = SETUP_INFO[selectedSetup];
  const isMultiAgent = selectedSetup !== 'single';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* Case */}
      <Card size="small" styles={{ body: { padding: 16 } }}>
        <Text type="secondary" style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', marginBottom: 8 }}>
          Test Case
        </Text>
        <Select
          style={{ width: '100%' }}
          value={selectedCase}
          onChange={onCaseChange}
          disabled={isRunning}
          options={cases.map((c) => ({
            value: c.id,
            label: `${c.id}. ${c.name}`,
          }))}
        />
      </Card>

      {/* Setup */}
      <Card size="small" styles={{ body: { padding: 16 } }}>
        <Text type="secondary" style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', marginBottom: 8 }}>
          Setup
        </Text>
        <Select
          style={{ width: '100%' }}
          value={selectedSetup}
          onChange={onSetupChange}
          disabled={isRunning}
          options={Object.keys(setups).map((key) => ({
            value: key,
            label: SETUP_INFO[key]?.title || key,
          }))}
        />

        {/* Setup Description */}
        {setupInfo && (
          <div style={{ marginTop: 12, padding: 12, background: '#f9f9f9', borderRadius: 6 }}>
            <Text style={{ fontSize: 12, lineHeight: 1.5 }}>{setupInfo.description}</Text>
          </div>
        )}
      </Card>

      {/* Agents (for multi-agent setups) */}
      {isMultiAgent && currentSetup?.agents && (
        <Card size="small" styles={{ body: { padding: 16 } }}>
          <Text type="secondary" style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', marginBottom: 12 }}>
            The Jury
          </Text>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {currentSetup.agents.map((agentKey) => {
              const agent = AGENT_DETAILS[agentKey];
              if (!agent) return null;
              return (
                <div
                  key={agentKey}
                  style={{
                    padding: 10,
                    background: '#fff',
                    borderRadius: 6,
                    border: '1px solid #f0f0f0',
                    borderLeft: `3px solid ${agent.color}`,
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
                    <Text strong style={{ fontSize: 12, textTransform: 'capitalize' }}>{agentKey}</Text>
                    <Text type="secondary" style={{ fontSize: 10 }}>· {agent.role}</Text>
                  </div>
                  <Text style={{ fontSize: 11, color: '#666', display: 'block', marginBottom: 6 }}>
                    {agent.methodology}
                  </Text>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                    {agent.checks.map((check, i) => (
                      <span
                        key={i}
                        style={{
                          fontSize: 9,
                          padding: '2px 6px',
                          background: '#f5f5f5',
                          borderRadius: 3,
                          color: '#888',
                        }}
                      >
                        {check}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Model */}
      <Card size="small" styles={{ body: { padding: 16 } }}>
        <Text type="secondary" style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', marginBottom: 8 }}>
          Model
        </Text>
        <Segmented
          block
          value={selectedModel}
          onChange={(v) => onModelChange(v as string)}
          disabled={isRunning}
          options={[
            { label: 'Fast', value: 'mini' },
            { label: 'Best', value: 'full' },
          ]}
        />
      </Card>

      {/* Action */}
      {isRunning ? (
        <Button
          block
          size="large"
          icon={<PauseOutlined />}
          onClick={onStop}
          style={{ background: '#ff4d4f', color: '#fff', border: 'none', height: 48 }}
        >
          Stop Debate
        </Button>
      ) : (
        <Button
          block
          size="large"
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={onStart}
          disabled={!selectedCase}
          style={{ background: '#000', border: 'none', height: 48 }}
        >
          Start Debate
        </Button>
      )}
    </div>
  );
}

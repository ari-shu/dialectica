import { Card, Select, Button, Typography, Segmented } from 'antd';
import { PlayCircleOutlined, PauseOutlined } from '@ant-design/icons';
import type { Case } from '../types';

const { Text } = Typography;

interface CaseSelectorProps {
  cases: Case[];
  selectedCase: number | null;
  selectedModel: string;
  onCaseChange: (caseId: number) => void;
  onModelChange: (model: string) => void;
  onStart: () => void;
  onStop: () => void;
  isRunning: boolean;
}

const AGENTS = [
  {
    key: 'numerical_hawk',
    name: 'The Numerical Hawk',
    color: '#1890ff',
    icon: '🔢',
    role: 'Numerical Precision',
    description: '"Numbers don\'t lie, but rounding can kill." Flags ANY numerical discrepancy.',
  },
  {
    key: 'temporal_detective',
    name: 'The Temporal Detective',
    color: '#52c41a',
    icon: '⏰',
    role: 'Temporal Precision',
    description: '"In a pandemic, yesterday\'s truth is today\'s lie." Catches time-related distortions.',
  },
  {
    key: 'spirit_defender',
    name: 'The Spirit Defender',
    color: '#722ed1',
    icon: '⚖️',
    role: 'Contextual Equivalence',
    description: '"Would a reasonable person be misled?" Argues for practical equivalence.',
  },
  {
    key: 'harm_assessor',
    name: 'The Harm Assessor',
    color: '#eb2f96',
    icon: '🏥',
    role: 'Consequence Analysis',
    description: '"Facts shape behavior." Evaluates real-world consequences of mutations.',
  },
  {
    key: 'devils_advocate',
    name: 'The Devil\'s Advocate',
    color: '#ff4d4f',
    icon: '😈',
    role: 'Adversarial',
    description: '"You\'re agreeing too fast!" Stress-tests the emerging consensus.',
    isAdversarial: true,
  },
];

export function CaseSelector({
  cases,
  selectedCase,
  selectedModel,
  onCaseChange,
  onModelChange,
  onStart,
  onStop,
  isRunning,
}: CaseSelectorProps) {
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

      {/* The Tribunal */}
      <Card size="small" styles={{ body: { padding: 16 } }}>
        <Text type="secondary" style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: 0.5, display: 'block', marginBottom: 12, color: '#5B4B8A' }}>
          The Tribunal
        </Text>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {AGENTS.map((agent) => (
            <div
              key={agent.key}
              style={{
                padding: 10,
                background: agent.isAdversarial ? '#fff8f8' : '#fff',
                borderRadius: 8,
                border: agent.isAdversarial ? '1px solid #ffccc7' : '1px solid #f0f0f0',
                borderLeft: `3px solid ${agent.color}`,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                <span style={{ fontSize: 16 }}>{agent.icon}</span>
                <Text strong style={{ fontSize: 12 }}>{agent.name}</Text>
                {agent.isAdversarial && (
                  <span style={{
                    fontSize: 9,
                    padding: '1px 5px',
                    background: '#ff4d4f',
                    color: '#fff',
                    borderRadius: 3,
                    fontWeight: 600,
                  }}>
                    ADVERSARIAL
                  </span>
                )}
              </div>
              <Text style={{ fontSize: 11, color: '#666', display: 'block' }}>
                {agent.description}
              </Text>
            </div>
          ))}
        </div>

        {/* Paradigm info */}
        <div style={{ marginTop: 12, padding: 10, background: '#F8F6FC', borderRadius: 6 }}>
          <Text style={{ fontSize: 11, color: '#5B4B8A', display: 'block', marginBottom: 4 }}>
            6-Agent Debate (3-5 Rounds)
          </Text>
          <Text style={{ fontSize: 11, color: '#666' }}>
            Minimum 3 rounds, consensus (80%) can stop early. The Synthesis Judge renders the final verdict.
          </Text>
        </div>
      </Card>

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
          style={{ background: '#cf4444', color: '#fff', border: 'none', height: 48 }}
        >
          Stop Investigation
        </Button>
      ) : (
        <Button
          block
          size="large"
          type="primary"
          icon={<PlayCircleOutlined />}
          onClick={onStart}
          disabled={!selectedCase}
          style={{ background: '#5B4B8A', border: 'none', height: 48 }}
        >
          Start Investigation
        </Button>
      )}
    </div>
  );
}

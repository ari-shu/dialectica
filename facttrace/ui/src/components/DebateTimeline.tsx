import { Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import type { AgentVerdict, AgentResponse, FinalVerdict, AgentInfo } from '../types';
import { AgentCard } from './AgentCard';
import { VerdictCard } from './VerdictCard';

const { Text } = Typography;

interface TimelineEvent {
  type: string;
  data: unknown;
  timestamp: Date;
}

interface DebateTimelineProps {
  events: TimelineEvent[];
  currentPhase: string;
  thinkingAgent: string | null;
}

export function DebateTimeline({ events, currentPhase, thinkingAgent }: DebateTimelineProps) {
  const agents = events.find((e) => e.type === 'agents')?.data as AgentInfo[] | undefined;
  const verdicts = events.filter((e) => e.type === 'agent_verdict').map((e) => e.data as AgentVerdict);
  const responses = events.filter((e) => e.type === 'agent_response').map((e) => e.data as AgentResponse);
  const finalVerdict = events.find((e) => e.type === 'final_verdict')?.data as FinalVerdict | undefined;

  return (
    <div>
      {/* Current Phase */}
      {currentPhase && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 8,
          padding: '10px 14px',
          background: '#f5f5f5',
          borderRadius: 8,
          marginBottom: 20,
        }}>
          <LoadingOutlined style={{ fontSize: 12 }} />
          <Text style={{ fontSize: 13 }}>{currentPhase}</Text>
        </div>
      )}

      {/* Agents */}
      {agents && agents.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <Text type="secondary" style={{
            fontSize: 11,
            textTransform: 'uppercase',
            letterSpacing: 0.5,
            display: 'block',
            marginBottom: 12
          }}>
            Jury Analysis
          </Text>
          {agents.map((agent) => {
            const verdict = verdicts.find((v) => v.agent_name === agent.name);
            const isThinking = thinkingAgent === agent.name && !verdict;
            return (
              <AgentCard
                key={agent.name}
                name={agent.name}
                color={agent.color}
                role={agent.role}
                verdict={verdict}
                isThinking={isThinking}
              />
            );
          })}
        </div>
      )}

      {/* Single Agent */}
      {!agents && verdicts.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <Text type="secondary" style={{
            fontSize: 11,
            textTransform: 'uppercase',
            letterSpacing: 0.5,
            display: 'block',
            marginBottom: 12
          }}>
            Analysis
          </Text>
          {verdicts.map((verdict) => (
            <AgentCard
              key={verdict.agent_name}
              name={verdict.agent_name}
              color={verdict.color}
              verdict={verdict}
            />
          ))}
        </div>
      )}

      {/* Deliberation */}
      {responses.length > 0 && (
        <div style={{ marginBottom: 20 }}>
          <Text type="secondary" style={{
            fontSize: 11,
            textTransform: 'uppercase',
            letterSpacing: 0.5,
            display: 'block',
            marginBottom: 12
          }}>
            Deliberation
          </Text>
          {responses.map((response, i) => (
            <AgentCard
              key={i}
              name={response.agent_name}
              color={response.color}
              response={response.response}
            />
          ))}
        </div>
      )}

      {/* Final Verdict */}
      {finalVerdict && (
        <div>
          <Text type="secondary" style={{
            fontSize: 11,
            textTransform: 'uppercase',
            letterSpacing: 0.5,
            display: 'block',
            marginBottom: 12
          }}>
            Final Verdict
          </Text>
          <VerdictCard verdict={finalVerdict} />
        </div>
      )}
    </div>
  );
}

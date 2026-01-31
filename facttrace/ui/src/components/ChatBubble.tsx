import { Tag, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import type { AgentVerdict } from '../types';

const { Text } = Typography;

interface ChatBubbleProps {
  name: string;
  color: string;
  verdict?: AgentVerdict;
  isThinking?: boolean;
  response?: string;
  isAdversarial?: boolean;
}

const AGENT_ICONS: Record<string, string> = {
  'Data Scientist': '📊',
  'Philosopher': '🎭',
  'Physicist': '🔬',
  'Historian': '📜',
  'Proponent': '✓',
  'Opponent': '✗',
  'Proposer': '📝',
  'Critic': '🔍',
  'Synthesizer': '⚖️',
  'Judge': '👨‍⚖️',
};

const getVerdictStyle = (v: string) => {
  switch (v) {
    case 'faithful': return { bg: '#f6ffed', color: '#52c41a', text: '✓ FAITHFUL', emoji: '✅' };
    case 'mutation': return { bg: '#fff2f0', color: '#ff4d4f', text: '✗ MUTATION', emoji: '❌' };
    default: return { bg: '#fffbe6', color: '#faad14', text: '? UNCERTAIN', emoji: '🤔' };
  }
};

export function ChatBubble({ name, color, verdict, isThinking, response, isAdversarial }: ChatBubbleProps) {
  const icon = AGENT_ICONS[name] || '🤖';
  const isPhilosopher = name === 'Philosopher';

  return (
    <div
      style={{
        display: 'flex',
        gap: 12,
        marginBottom: 16,
        animation: 'fadeInUp 0.3s ease-out',
      }}
      className="chat-bubble-container"
    >
      {/* Avatar */}
      <div
        style={{
          width: 44,
          height: 44,
          borderRadius: '50%',
          background: isPhilosopher ? '#fff2f0' : `${color}15`,
          border: `2px solid ${color}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: 20,
          flexShrink: 0,
          boxShadow: isPhilosopher ? '0 0 0 3px rgba(255,77,79,0.2)' : 'none',
        }}
      >
        {icon}
      </div>

      {/* Bubble */}
      <div style={{ flex: 1, maxWidth: 'calc(100% - 56px)' }}>
        {/* Name and thinking indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
          <Text strong style={{
            fontSize: 13,
            color: color,
          }}>
            {name}
          </Text>
          {isAdversarial && (
            <Tag color="red" style={{ fontSize: 9, padding: '0 4px', margin: 0, lineHeight: '16px' }}>
              ADVERSARIAL
            </Tag>
          )}
          {isThinking && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 4,
              color: '#999',
              fontSize: 12,
            }}>
              <LoadingOutlined />
              <span>thinking...</span>
            </div>
          )}
        </div>

        {/* Message bubble */}
        {(verdict || response || isThinking) && (
          <div
            style={{
              background: isPhilosopher ? '#fff8f8' : '#fff',
              border: `1px solid ${isPhilosopher ? '#ffccc7' : '#E8E4F0'}`,
              borderRadius: '4px 16px 16px 16px',
              padding: 14,
              boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
              position: 'relative',
            }}
          >
            {/* Thinking state */}
            {isThinking && !verdict && !response && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div className="typing-indicator">
                  <span style={{
                    display: 'inline-block',
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: color,
                    opacity: 0.4,
                    animation: 'bounce 1.4s infinite ease-in-out both',
                    animationDelay: '0s',
                  }} />
                  <span style={{
                    display: 'inline-block',
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: color,
                    opacity: 0.4,
                    marginLeft: 4,
                    animation: 'bounce 1.4s infinite ease-in-out both',
                    animationDelay: '0.16s',
                  }} />
                  <span style={{
                    display: 'inline-block',
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    background: color,
                    opacity: 0.4,
                    marginLeft: 4,
                    animation: 'bounce 1.4s infinite ease-in-out both',
                    animationDelay: '0.32s',
                  }} />
                </div>
                <Text type="secondary" style={{ fontSize: 12 }}>Analyzing claim...</Text>
              </div>
            )}

            {/* Verdict */}
            {verdict && (
              <>
                {/* Verdict badge */}
                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  padding: '4px 10px',
                  borderRadius: 6,
                  background: getVerdictStyle(verdict.verdict).bg,
                  marginBottom: 10,
                }}>
                  <span style={{ fontSize: 14 }}>{getVerdictStyle(verdict.verdict).emoji}</span>
                  <Text strong style={{
                    fontSize: 12,
                    color: getVerdictStyle(verdict.verdict).color,
                    letterSpacing: 0.5,
                  }}>
                    {getVerdictStyle(verdict.verdict).text}
                  </Text>
                </div>

                {/* Reasoning */}
                <Text style={{
                  fontSize: 14,
                  lineHeight: 1.7,
                  display: 'block',
                  color: '#333',
                }}>
                  {verdict.reasoning}
                </Text>

                {/* Evidence tags */}
                {verdict.evidence?.length > 0 && (
                  <div style={{
                    marginTop: 12,
                    paddingTop: 12,
                    borderTop: '1px dashed #E8E4F0',
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 6,
                  }}>
                    <Text type="secondary" style={{ fontSize: 10, width: '100%', marginBottom: 4 }}>
                      KEY EVIDENCE:
                    </Text>
                    {verdict.evidence.slice(0, 4).map((e, i) => (
                      <div key={i} style={{
                        fontSize: 11,
                        color: '#5B4B8A',
                        padding: '3px 8px',
                        background: '#F8F6FC',
                        borderRadius: 4,
                        border: '1px solid #E8E4F0',
                      }}>
                        {e}
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}

            {/* Response (for deliberation) */}
            {response && (
              <Text style={{ fontSize: 14, lineHeight: 1.7, color: '#333' }}>
                {response}
              </Text>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

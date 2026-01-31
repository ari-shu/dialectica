import { Tag, Typography } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import type { AgentVerdict } from '../types';

const { Text } = Typography;

interface AgentCardProps {
  name: string;
  color: string;
  role?: string;
  verdict?: AgentVerdict;
  isThinking?: boolean;
  response?: string;
}

const colorMap: Record<string, string> = {
  red: '#ff4d4f',
  blue: '#1890ff',
  green: '#52c41a',
  gold: '#faad14',
};

export function AgentCard({ name, color, role, verdict, isThinking, response }: AgentCardProps) {
  const accentColor = colorMap[color] || '#1890ff';

  const getVerdictStyle = (v: string) => {
    switch (v) {
      case 'faithful': return { bg: '#f6ffed', color: '#52c41a', text: 'Faithful' };
      case 'mutation': return { bg: '#fff2f0', color: '#ff4d4f', text: 'Mutation' };
      default: return { bg: '#fffbe6', color: '#faad14', text: 'Uncertain' };
    }
  };

  return (
    <div
      style={{
        padding: 16,
        background: '#fff',
        borderRadius: 10,
        border: '1px solid #f0f0f0',
        marginBottom: 12,
      }}
      className="fade-in"
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: verdict || response ? 12 : 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: accentColor,
          }} />
          <Text strong style={{ fontSize: 14 }}>{name}</Text>
          {isThinking && <LoadingOutlined style={{ color: '#999', fontSize: 12 }} className="pulse" />}
        </div>

        {verdict && (
          <Tag
            style={{
              background: getVerdictStyle(verdict.verdict).bg,
              color: getVerdictStyle(verdict.verdict).color,
              border: 'none',
              fontWeight: 500,
              fontSize: 12,
            }}
          >
            {getVerdictStyle(verdict.verdict).text} · {Math.round(verdict.confidence * 100)}%
          </Tag>
        )}
      </div>

      {/* Role (when no verdict yet) */}
      {role && !verdict && !response && !isThinking && (
        <Text type="secondary" style={{ fontSize: 12 }}>{role}</Text>
      )}

      {/* Thinking */}
      {isThinking && (
        <Text type="secondary" style={{ fontSize: 13 }}>Analyzing...</Text>
      )}

      {/* Verdict */}
      {verdict && (
        <>
          <Text style={{ fontSize: 13, lineHeight: 1.6, display: 'block' }}>
            {verdict.reasoning}
          </Text>
          {verdict.evidence?.length > 0 && (
            <div style={{ marginTop: 12 }}>
              {verdict.evidence.slice(0, 2).map((e, i) => (
                <div key={i} style={{
                  fontSize: 12,
                  color: '#666',
                  padding: '4px 8px',
                  background: '#fafafa',
                  borderRadius: 4,
                  marginTop: 4,
                }}>
                  {e}
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {/* Response */}
      {response && (
        <Text style={{ fontSize: 13, lineHeight: 1.6, fontStyle: 'italic', color: '#666' }}>
          "{response}"
        </Text>
      )}
    </div>
  );
}

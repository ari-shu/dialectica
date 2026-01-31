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
  purple: '#5B4B8A',
  magenta: '#5B4B8A',
  cyan: '#9B8BC8',
  yellow: '#faad14',
};

export function AgentCard({ name, color, role, verdict, isThinking, response }: AgentCardProps) {
  // Support both named colors and hex colors
  const accentColor = color.startsWith('#') ? color : (colorMap[color] || '#5B4B8A');

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
        borderRadius: 12,
        border: '1px solid #E8E4F0',
        borderLeft: `4px solid ${accentColor}`,
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)',
      }}
      className="fade-in"
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: verdict || response ? 12 : 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            background: `${accentColor}15`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}>
            <div style={{
              width: 10,
              height: 10,
              borderRadius: '50%',
              background: accentColor,
            }} />
          </div>
          <Text strong style={{ fontSize: 14, color: '#2D2255' }}>{name}</Text>
          {isThinking && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              padding: '2px 8px',
              background: '#F8F6FC',
              borderRadius: 4,
            }}>
              <LoadingOutlined style={{ color: '#5B4B8A', fontSize: 11 }} />
              <Text type="secondary" style={{ fontSize: 11 }}>Analyzing</Text>
            </div>
          )}
        </div>

        {verdict && (
          <Tag
            style={{
              background: getVerdictStyle(verdict.verdict).bg,
              color: getVerdictStyle(verdict.verdict).color,
              border: `1px solid ${getVerdictStyle(verdict.verdict).color}30`,
              fontWeight: 600,
              fontSize: 12,
              padding: '2px 10px',
              borderRadius: 6,
            }}
          >
            {getVerdictStyle(verdict.verdict).text}
          </Tag>
        )}
      </div>

      {/* Role (when no verdict yet) */}
      {role && !verdict && !response && !isThinking && (
        <Text type="secondary" style={{ fontSize: 12, marginLeft: 42 }}>{role}</Text>
      )}

      {/* Verdict */}
      {verdict && (
        <div style={{ marginLeft: 42 }}>
          <Text style={{ fontSize: 13, lineHeight: 1.7, display: 'block', color: '#444' }}>
            {verdict.reasoning}
          </Text>
          {verdict.evidence?.length > 0 && (
            <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {verdict.evidence.slice(0, 3).map((e, i) => (
                <div key={i} style={{
                  fontSize: 11,
                  color: '#5B4B8A',
                  padding: '4px 10px',
                  background: '#F8F6FC',
                  borderRadius: 4,
                  border: '1px solid #E8E4F0',
                }}>
                  {e}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Response */}
      {response && (
        <div style={{ marginLeft: 42 }}>
          <Text style={{ fontSize: 13, lineHeight: 1.6, fontStyle: 'italic', color: '#666' }}>
            "{response}"
          </Text>
        </div>
      )}
    </div>
  );
}

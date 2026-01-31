import { Typography, Tag } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';
import type { FinalVerdict } from '../types';

const { Text } = Typography;

interface VerdictCardProps {
  verdict: FinalVerdict;
}

export function VerdictCard({ verdict }: VerdictCardProps) {
  const config = {
    faithful: {
      icon: <CheckCircleOutlined />,
      title: 'Faithful',
      color: '#52c41a',
      bg: '#f6ffed',
    },
    mutation: {
      icon: <CloseCircleOutlined />,
      title: 'Mutation',
      color: '#ff4d4f',
      bg: '#fff2f0',
    },
    uncertain: {
      icon: <QuestionCircleOutlined />,
      title: 'Uncertain',
      color: '#faad14',
      bg: '#fffbe6',
    },
  }[verdict.verdict] || {
    icon: <QuestionCircleOutlined />,
    title: 'Unknown',
    color: '#999',
    bg: '#fafafa',
  };

  return (
    <div
      className="fade-in"
      style={{
        padding: 24,
        background: config.bg,
        borderRadius: 12,
        border: `1px solid ${config.color}20`,
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
        <span style={{ fontSize: 32, color: config.color }}>
          {config.icon}
        </span>
        <div>
          <div style={{ fontSize: 20, fontWeight: 600, color: config.color }}>
            {config.title}
          </div>
          <Text type="secondary" style={{ fontSize: 13 }}>
            {Math.round(verdict.confidence * 100)}% confidence
          </Text>
        </div>
      </div>

      {/* Reasoning */}
      <Text style={{ fontSize: 14, lineHeight: 1.6, display: 'block' }}>
        {verdict.reasoning}
      </Text>

      {/* Mutation Type */}
      {verdict.mutation_type && (
        <Tag
          style={{
            marginTop: 12,
            background: '#fff',
            border: `1px solid ${config.color}40`,
            color: config.color,
          }}
        >
          {verdict.mutation_type}
        </Tag>
      )}
    </div>
  );
}

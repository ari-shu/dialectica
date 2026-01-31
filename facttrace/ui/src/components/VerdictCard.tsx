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
      bg: 'linear-gradient(135deg, #f6ffed 0%, #d9f7be 100%)',
      borderColor: '#b7eb8f',
    },
    mutation: {
      icon: <CloseCircleOutlined />,
      title: 'Mutation Detected',
      color: '#ff4d4f',
      bg: 'linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%)',
      borderColor: '#ffa39e',
    },
    uncertain: {
      icon: <QuestionCircleOutlined />,
      title: 'Uncertain',
      color: '#faad14',
      bg: 'linear-gradient(135deg, #fffbe6 0%, #fff1b8 100%)',
      borderColor: '#ffe58f',
    },
  }[verdict.verdict] || {
    icon: <QuestionCircleOutlined />,
    title: 'Unknown',
    color: '#999',
    bg: '#fafafa',
    borderColor: '#d9d9d9',
  };

  return (
    <div
      className="fade-in"
      style={{
        padding: 24,
        background: config.bg,
        borderRadius: 16,
        border: `2px solid ${config.borderColor}`,
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <div style={{
            width: 56,
            height: 56,
            borderRadius: 16,
            background: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
          }}>
            <span style={{ fontSize: 28, color: config.color }}>
              {config.icon}
            </span>
          </div>
          <div>
            <div style={{ fontSize: 22, fontWeight: 700, color: config.color }}>
              {config.title}
            </div>
            <Text type="secondary" style={{ fontSize: 13 }}>
              Judge's final ruling
            </Text>
          </div>
        </div>

      </div>

      {/* Reasoning */}
      <div style={{
        padding: 16,
        background: 'rgba(255,255,255,0.7)',
        borderRadius: 10,
        marginBottom: verdict.mutation_type || verdict.dissenting?.length ? 16 : 0,
      }}>
        <Text style={{ fontSize: 14, lineHeight: 1.7, display: 'block' }}>
          {verdict.reasoning}
        </Text>
      </div>

      {/* Mutation Type & Dissenting */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
        {verdict.mutation_type && (
          <Tag
            style={{
              background: '#fff',
              border: `1px solid ${config.color}60`,
              color: config.color,
              fontWeight: 500,
              padding: '4px 12px',
              borderRadius: 6,
            }}
          >
            Type: {verdict.mutation_type}
          </Tag>
        )}
        {verdict.dissenting && verdict.dissenting.length > 0 && (
          <Tag
            style={{
              background: '#fff',
              border: '1px solid #d9d9d9',
              color: '#666',
              padding: '4px 12px',
              borderRadius: 6,
            }}
          >
            {verdict.dissenting.length} dissenting view{verdict.dissenting.length > 1 ? 's' : ''}
          </Tag>
        )}
      </div>
    </div>
  );
}

import { Typography, Button, Card, Row, Col } from 'antd';
import { ArrowRightOutlined, TeamOutlined, CheckCircleOutlined, CloseCircleOutlined, ExperimentOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface LandingPageProps {
  onEnter: () => void;
}

const AGENTS = [
  {
    name: 'Literalist',
    color: '#ff4d4f',
    role: 'Pedantic Fact-Checker',
    description: 'Strict textual comparison. Checks exact numbers, dates, and precise wording.',
  },
  {
    name: 'Contextualist',
    color: '#1890ff',
    role: 'Context Analyzer',
    description: 'Evaluates if important context is preserved. Detects missing caveats and shifted implications.',
  },
  {
    name: 'Statistician',
    color: '#52c41a',
    role: 'Numerical Expert',
    description: 'Analyzes numerical framing. Checks rounding accuracy and date attribution.',
  },
];

export function LandingPage({ onEnter }: LandingPageProps) {
  return (
    <div style={{ minHeight: '100vh', background: '#fff' }}>
      {/* Hero Section */}
      <div style={{
        padding: '80px 24px',
        textAlign: 'center',
        background: 'linear-gradient(180deg, #fafafa 0%, #fff 100%)',
        borderBottom: '1px solid #f0f0f0',
      }}>
        <div style={{ maxWidth: 800, margin: '0 auto' }}>
          <div style={{ fontSize: 64, marginBottom: 24 }}>⚖️</div>
          <Title level={1} style={{ fontSize: 48, fontWeight: 700, marginBottom: 16 }}>
            FactTrace
          </Title>
          <Paragraph style={{ fontSize: 20, color: '#666', marginBottom: 32 }}>
            A jury of AI agents that debates whether claims are faithful
            representations of source facts — or mutations.
          </Paragraph>
          <Button
            type="primary"
            size="large"
            icon={<ArrowRightOutlined />}
            onClick={onEnter}
            style={{
              height: 56,
              paddingInline: 40,
              fontSize: 16,
              background: '#000',
              border: 'none',
              borderRadius: 8,
            }}
          >
            Start Verifying
          </Button>
        </div>
      </div>

      {/* Problem Section */}
      <div style={{ padding: '64px 24px', maxWidth: 1000, margin: '0 auto' }}>
        <Row gutter={48} align="middle">
          <Col xs={24} md={12}>
            <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
              The Problem
            </Text>
            <Title level={2} style={{ marginTop: 8, marginBottom: 16 }}>
              Subtle misinformation is hard to detect
            </Title>
            <Paragraph style={{ fontSize: 16, color: '#666', lineHeight: 1.8 }}>
              A claim can be "technically true" while completely distorting the meaning.
              Small changes in numbers, dates, or missing context can flip the narrative.
            </Paragraph>
          </Col>
          <Col xs={24} md={12}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <Card size="small" style={{ borderLeft: '3px solid #ff4d4f' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
                  <Text strong>Temporal Shift</Text>
                </div>
                <Text type="secondary" style={{ fontSize: 13 }}>
                  "as of Feb 13" → "after Feb 13"
                </Text>
              </Card>
              <Card size="small" style={{ borderLeft: '3px solid #faad14' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CloseCircleOutlined style={{ color: '#faad14' }} />
                  <Text strong>Missing Caveat</Text>
                </div>
                <Text type="secondary" style={{ fontSize: 13 }}>
                  Dropping "official figures may not have counted..."
                </Text>
              </Card>
              <Card size="small" style={{ borderLeft: '3px solid #1890ff' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CloseCircleOutlined style={{ color: '#1890ff' }} />
                  <Text strong>Numerical Rounding</Text>
                </div>
                <Text type="secondary" style={{ fontSize: 13 }}>
                  "374,000 on March 23" → "375,000 by March 24"
                </Text>
              </Card>
            </div>
          </Col>
        </Row>
      </div>

      {/* Solution Section */}
      <div style={{ padding: '64px 24px', background: '#fafafa' }}>
        <div style={{ maxWidth: 1000, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
              Our Approach
            </Text>
            <Title level={2} style={{ marginTop: 8, marginBottom: 8 }}>
              A jury of specialized agents
            </Title>
            <Paragraph style={{ fontSize: 16, color: '#666', maxWidth: 600, margin: '0 auto' }}>
              Instead of one AI making a binary decision, multiple experts analyze the claim
              from different angles and debate to reach a verdict.
            </Paragraph>
          </div>

          <Row gutter={24}>
            {AGENTS.map((agent) => (
              <Col xs={24} md={8} key={agent.name}>
                <Card
                  style={{
                    height: '100%',
                    borderTop: `3px solid ${agent.color}`,
                    borderRadius: 12,
                  }}
                >
                  <div style={{
                    width: 40,
                    height: 40,
                    borderRadius: 8,
                    background: `${agent.color}15`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 16,
                  }}>
                    <TeamOutlined style={{ fontSize: 20, color: agent.color }} />
                  </div>
                  <Title level={4} style={{ marginBottom: 4 }}>{agent.name}</Title>
                  <Text type="secondary" style={{ fontSize: 12 }}>{agent.role}</Text>
                  <Paragraph style={{ marginTop: 12, marginBottom: 0, color: '#666', fontSize: 14 }}>
                    {agent.description}
                  </Paragraph>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      </div>

      {/* How It Works */}
      <div style={{ padding: '64px 24px', maxWidth: 1000, margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: 48 }}>
          <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: 1 }}>
            How It Works
          </Text>
          <Title level={2} style={{ marginTop: 8 }}>
            Three-phase deliberation
          </Title>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {[
            {
              step: '01',
              title: 'Independent Analysis',
              description: 'Each agent analyzes the claim against the source from their unique perspective.',
            },
            {
              step: '02',
              title: 'Deliberation',
              description: 'Agents review each other\'s findings and respond to points of agreement or disagreement.',
            },
            {
              step: '03',
              title: 'Verdict Synthesis',
              description: 'A judge synthesizes all opinions into a final verdict with confidence score and reasoning.',
            },
          ].map((item) => (
            <div key={item.step} style={{ display: 'flex', gap: 24, alignItems: 'flex-start' }}>
              <div style={{
                width: 48,
                height: 48,
                borderRadius: 12,
                background: '#f5f5f5',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                color: '#999',
                flexShrink: 0,
              }}>
                {item.step}
              </div>
              <div>
                <Title level={5} style={{ marginBottom: 4 }}>{item.title}</Title>
                <Text type="secondary">{item.description}</Text>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA Section */}
      <div style={{
        padding: '64px 24px',
        textAlign: 'center',
        background: '#000',
        color: '#fff',
      }}>
        <div style={{ maxWidth: 600, margin: '0 auto' }}>
          <ExperimentOutlined style={{ fontSize: 40, marginBottom: 16, opacity: 0.8 }} />
          <Title level={2} style={{ color: '#fff', marginBottom: 16 }}>
            Try it yourself
          </Title>
          <Paragraph style={{ color: 'rgba(255,255,255,0.7)', marginBottom: 32, fontSize: 16 }}>
            Watch the agents debate in real-time as they analyze claims from our test cases.
          </Paragraph>
          <Button
            size="large"
            icon={<ArrowRightOutlined />}
            onClick={onEnter}
            style={{
              height: 52,
              paddingInline: 36,
              fontSize: 15,
              background: '#fff',
              color: '#000',
              border: 'none',
              borderRadius: 8,
            }}
          >
            Launch Demo
          </Button>
        </div>
      </div>

      {/* Footer */}
      <div style={{ padding: '24px', textAlign: 'center', borderTop: '1px solid #f0f0f0' }}>
        <Text type="secondary" style={{ fontSize: 13 }}>
          Built for the Cambridge FactTrace Hackathon
        </Text>
      </div>
    </div>
  );
}

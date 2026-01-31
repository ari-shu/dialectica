import { Typography, Button, Card, Row, Col } from 'antd';
import { ArrowRightOutlined, CloseCircleOutlined, ExperimentOutlined, TeamOutlined, SyncOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;

interface LandingPageProps {
  onEnter: () => void;
}

const JURORS = [
  {
    name: 'The Numerical Hawk',
    color: '#1890ff',
    icon: '🔢',
    description: '"Numbers don\'t lie, but rounding can kill." Obsesses over quantitative precision. Will die on the hill of "87 ≠ 70".',
    discipline: 'Statistics & Data Science',
  },
  {
    name: 'The Temporal Detective',
    color: '#52c41a',
    icon: '⏰',
    description: '"In a pandemic, yesterday\'s truth is today\'s lie." Catches "as of" vs "after" vs "by" distortions.',
    discipline: 'History & Temporal Logic',
  },
  {
    name: 'The Spirit Defender',
    color: '#722ed1',
    icon: '⚖️',
    description: '"Would a reasonable person be misled?" Argues for practical equivalence when claims are directionally correct.',
    discipline: 'Law & Pragmatics',
  },
  {
    name: 'The Harm Assessor',
    color: '#eb2f96',
    icon: '🏥',
    description: '"Facts shape behavior." Evaluates real-world consequences—understating deaths vs overstating cases.',
    discipline: 'Ethics & Public Health',
  },
  {
    name: 'The Devil\'s Advocate',
    color: '#ff4d4f',
    icon: '😈',
    description: '"You\'re agreeing too fast!" Stress-tests consensus. If others say Faithful, argues Mutation.',
    discipline: 'Dialectics & Rhetoric',
    isAdversarial: true,
  },
  {
    name: 'The Synthesis Judge',
    color: '#faad14',
    icon: '👨‍⚖️',
    description: 'Grounds verdicts in cybernetics and epistemic pluralism. Truth emerges from the dance between perspectives.',
    discipline: 'Philosophy & Systems Theory',
    isJudge: true,
  },
];

export function LandingPage({ onEnter }: LandingPageProps) {
  return (
    <div style={{ minHeight: '100vh', background: '#fff' }}>
      {/* Hero Section */}
      <div style={{
        padding: '80px 24px',
        textAlign: 'center',
        background: 'linear-gradient(180deg, #F8F6FC 0%, #fff 100%)',
        borderBottom: '1px solid #E8E4F0',
      }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <div style={{ fontSize: 64, marginBottom: 24 }}>⚖️</div>
          <Title level={1} style={{ fontSize: 52, fontWeight: 700, marginBottom: 16, color: '#2D2255' }}>
            Dialectica
          </Title>
          <Paragraph style={{ fontSize: 22, color: '#444', marginBottom: 16, fontWeight: 500 }}>
            An interdisciplinary jury of AI agents that uses dialectical reasoning to argue, negotiate, and reach verdicts about truth in the fight against misinformation.
          </Paragraph>
          <Paragraph style={{ fontSize: 16, color: '#666', marginBottom: 32, maxWidth: 700, margin: '0 auto 32px' }}>
            Our platform runs a 6-agent debate until consensus, where agents deliberate over multiple rounds until they reach 80% agreement. The Synthesis Judge renders the final verdict grounded in <strong>cybernetics</strong> and <strong>epistemic pluralism</strong>.
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
              background: '#5B4B8A',
              border: 'none',
              borderRadius: 8,
            }}
          >
            Start Investigation
          </Button>
        </div>
      </div>

      {/* Problem Section */}
      <div style={{ padding: '64px 24px', maxWidth: 1000, margin: '0 auto' }}>
        <Row gutter={48} align="middle">
          <Col xs={24} md={12}>
            <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: 1, color: '#5B4B8A' }}>
              The Challenge
            </Text>
            <Title level={2} style={{ marginTop: 8, marginBottom: 16, color: '#2D2255' }}>
              Misinformation hides in subtle distortions
            </Title>
            <Paragraph style={{ fontSize: 16, color: '#666', lineHeight: 1.8 }}>
              Small changes in numbers, dates, or context can completely alter the truth.
              A single-perspective fact-checker misses nuances that emerge only through interdisciplinary debate.
            </Paragraph>
          </Col>
          <Col xs={24} md={12}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              <Card size="small" style={{ borderLeft: '3px solid #5B4B8A' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CloseCircleOutlined style={{ color: '#5B4B8A' }} />
                  <Text strong>Temporal Shift</Text>
                </div>
                <Text type="secondary" style={{ fontSize: 13 }}>
                  "as of Feb 13" → "after Feb 13"
                </Text>
              </Card>
              <Card size="small" style={{ borderLeft: '3px solid #7B6BA8' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CloseCircleOutlined style={{ color: '#7B6BA8' }} />
                  <Text strong>Missing Caveat</Text>
                </div>
                <Text type="secondary" style={{ fontSize: 13 }}>
                  Dropping "official figures may not have counted..."
                </Text>
              </Card>
              <Card size="small" style={{ borderLeft: '3px solid #9B8BC8' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CloseCircleOutlined style={{ color: '#9B8BC8' }} />
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

      {/* Agents Section */}
      <div style={{ padding: '64px 24px', background: '#F8F6FC' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: 1, color: '#5B4B8A' }}>
              The Interdisciplinary Jury
            </Text>
            <Title level={2} style={{ marginTop: 8, marginBottom: 8, color: '#2D2255' }}>
              Six agents with distinct disciplinary lenses
            </Title>
            <Paragraph style={{ fontSize: 16, color: '#666', maxWidth: 750, margin: '0 auto' }}>
              Each agent brings theories and methodologies from different fields—statistics, law, ethics, philosophy—creating a meaningful interdisciplinary debate that surfaces truth through dialectical reasoning.
            </Paragraph>
          </div>

          <Row gutter={[16, 16]}>
            {JURORS.map((juror) => (
              <Col xs={24} sm={12} md={8} key={juror.name}>
                <Card
                  style={{
                    height: '100%',
                    borderTop: `4px solid ${juror.color}`,
                    borderRadius: 12,
                    background: juror.isAdversarial ? '#fff5f5' : juror.isJudge ? '#fffbe6' : '#fff',
                  }}
                >
                  <div style={{
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    background: `${juror.color}15`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    marginBottom: 16,
                    fontSize: 24,
                  }}>
                    {juror.icon}
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4, flexWrap: 'wrap' }}>
                    <Title level={5} style={{ marginBottom: 0, color: juror.color }}>{juror.name}</Title>
                    {juror.isAdversarial && (
                      <span style={{ fontSize: 9, padding: '2px 6px', background: '#ff4d4f', color: '#fff', borderRadius: 4, fontWeight: 600 }}>
                        ADVERSARIAL
                      </span>
                    )}
                    {juror.isJudge && (
                      <span style={{ fontSize: 9, padding: '2px 6px', background: '#faad14', color: '#fff', borderRadius: 4, fontWeight: 600 }}>
                        JUDGE
                      </span>
                    )}
                  </div>
                  <Text style={{ fontSize: 11, color: juror.color, display: 'block', marginBottom: 8 }}>
                    {juror.discipline}
                  </Text>
                  <Paragraph style={{ marginTop: 0, marginBottom: 0, color: '#666', fontSize: 13 }}>
                    {juror.description}
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
          <Text type="secondary" style={{ fontSize: 12, textTransform: 'uppercase', letterSpacing: 1, color: '#5B4B8A' }}>
            The Process
          </Text>
          <Title level={2} style={{ marginTop: 8, color: '#2D2255' }}>
            Dialectical reasoning through debate
          </Title>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {[
            {
              step: '01',
              title: 'Initial Positions',
              description: 'Each agent examines the claim through their disciplinary lens and renders an independent assessment.',
              icon: <TeamOutlined />,
            },
            {
              step: '02',
              title: 'Dialectical Debate',
              description: 'Agents argue, challenge, and negotiate over 3-5 rounds until 80% consensus emerges. The Devil\'s Advocate ensures no groupthink.',
              icon: <SyncOutlined />,
            },
            {
              step: '03',
              title: 'Synthesis & Verdict',
              description: 'The Synthesis Judge summarizes the debate, explains the consensus, highlights areas of divergence, and renders a verdict grounded in cybernetics and epistemic pluralism.',
              icon: <ExperimentOutlined />,
            },
          ].map((item) => (
            <div key={item.step} style={{ display: 'flex', gap: 24, alignItems: 'flex-start' }}>
              <div style={{
                width: 48,
                height: 48,
                borderRadius: 12,
                background: '#F0EBF8',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 700,
                color: '#5B4B8A',
                flexShrink: 0,
              }}>
                {item.step}
              </div>
              <div>
                <Title level={5} style={{ marginBottom: 4, color: '#2D2255' }}>{item.title}</Title>
                <Text type="secondary">{item.description}</Text>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Theory Section */}
      <div style={{ padding: '64px 24px', background: '#F8F6FC' }}>
        <div style={{ maxWidth: 900, margin: '0 auto' }}>
          <Row gutter={[32, 32]}>
            <Col xs={24} md={12}>
              <Card style={{ height: '100%', borderRadius: 12 }}>
                <Title level={4} style={{ color: '#5B4B8A', marginBottom: 16 }}>
                  🔄 Cybernetics
                </Title>
                <Paragraph style={{ color: '#666', marginBottom: 0 }}>
                  The debate is a <strong>self-regulating feedback system</strong>. Each agent's perspective corrects and refines understanding.
                  Disagreement is signal, not noise—it reveals blind spots. Truth emerges through iterative cycles of claim, counter-claim, and synthesis.
                </Paragraph>
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card style={{ height: '100%', borderRadius: 12 }}>
                <Title level={4} style={{ color: '#5B4B8A', marginBottom: 16 }}>
                  🌐 Epistemic Pluralism
                </Title>
                <Paragraph style={{ color: '#666', marginBottom: 0 }}>
                  We honor <strong>multiple valid ways of knowing</strong>: quantitative precision, temporal logic, pragmatic equivalence,
                  consequentialist ethics, and dialectical reasoning. Truth is multi-dimensional—it survives scrutiny from multiple epistemic lenses.
                </Paragraph>
              </Card>
            </Col>
          </Row>
        </div>
      </div>

      {/* CTA Section */}
      <div style={{
        padding: '64px 24px',
        textAlign: 'center',
        background: 'linear-gradient(135deg, #2D2255 0%, #5B4B8A 100%)',
        color: '#fff',
      }}>
        <div style={{ maxWidth: 700, margin: '0 auto' }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🔭</div>
          <Title level={2} style={{ color: '#fff', marginBottom: 16 }}>
            Tested on the Galileo Dataset
          </Title>
          <Paragraph style={{ color: 'rgba(255,255,255,0.85)', marginBottom: 16, fontSize: 16 }}>
            Just like Galileo's telescope in the 17th century and NASA's Galileo space mission in 1989,
            our system aims to revolutionize the search for truth and meaning.
          </Paragraph>
          <Paragraph style={{ color: 'rgba(255,255,255,0.7)', marginBottom: 32, fontSize: 14 }}>
            Watch the interdisciplinary jury debate in real-time as they scrutinize claims against evidence.
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
              color: '#2D2255',
              border: 'none',
              borderRadius: 8,
            }}
          >
            Begin Investigation
          </Button>
        </div>
      </div>

      {/* Footer */}
      <div style={{ padding: '24px', textAlign: 'center', borderTop: '1px solid #E8E4F0' }}>
        <Text type="secondary" style={{ fontSize: 13 }}>
          "Truth emerges from the cybernetic dance between perspectives." — Built for the Cambridge Hackathon
        </Text>
      </div>
    </div>
  );
}

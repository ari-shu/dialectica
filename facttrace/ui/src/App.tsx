import { useState, useEffect, useCallback, useRef } from 'react';
import { Layout, Typography, Card, Row, Col, Alert, ConfigProvider, Tag, Button } from 'antd';
import { ReloadOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { LandingPage } from './components/LandingPage';
import { CaseSelector } from './components/CaseSelector';
import { DebateTimeline } from './components/DebateTimeline';
import type { Case, Setup, DebateEvent } from './types';
import './App.css';

const { Content } = Layout;
const { Title, Text } = Typography;

const API_BASE = 'http://localhost:8000';

interface TimelineEvent {
  type: string;
  data: unknown;
  timestamp: Date;
}

function App() {
  const [showLanding, setShowLanding] = useState(true);
  const [cases, setCases] = useState<Case[]>([]);
  const [setups, setSetups] = useState<Record<string, Setup>>({});
  const [selectedCase, setSelectedCase] = useState<number | null>(null);
  const [selectedSetup, setSelectedSetup] = useState('jury-llm');
  const [selectedModel, setSelectedModel] = useState('mini');
  const [isRunning, setIsRunning] = useState(false);
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [currentPhase, setCurrentPhase] = useState('');
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [currentCase, setCurrentCase] = useState<Case | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/cases`).then((r) => r.json()),
      fetch(`${API_BASE}/api/setups`).then((r) => r.json()),
    ])
      .then(([casesData, setupsData]) => {
        setCases(casesData.cases);
        setSetups(setupsData.setups);
        setIsConnected(true);
        if (casesData.cases.length > 0) {
          setSelectedCase(casesData.cases[0].id);
        }
      })
      .catch(() => {
        setError(`Cannot connect to API at ${API_BASE}`);
        setIsConnected(false);
      });
  }, []);

  const stopDebate = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsRunning(false);
    setCurrentPhase('');
    setThinkingAgent(null);
  }, []);

  const startDebate = useCallback(() => {
    if (!selectedCase) return;
    stopDebate();

    setIsRunning(true);
    setEvents([]);
    setCurrentPhase('Connecting...');
    setThinkingAgent(null);
    setError(null);
    setCurrentCase(null);

    const eventSource = new EventSource(
      `${API_BASE}/api/debate/stream?case_id=${selectedCase}&setup=${selectedSetup}&model=${selectedModel}`
    );
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as DebateEvent;
        setEvents((prev) => [...prev, { type: data.type, data: data.data, timestamp: new Date() }]);

        switch (data.type) {
          case 'case':
            setCurrentCase(data.data);
            break;
          case 'phase':
            setCurrentPhase(data.data);
            setThinkingAgent(null);
            break;
          case 'agent_thinking':
            setThinkingAgent(data.data.agent_name);
            break;
          case 'agent_verdict':
          case 'agent_response':
            setThinkingAgent(null);
            break;
          case 'status':
            setCurrentPhase(data.data);
            break;
          case 'done':
            setIsRunning(false);
            setCurrentPhase('');
            eventSource.close();
            eventSourceRef.current = null;
            break;
        }
      } catch (err) {
        console.error('Failed to parse event:', err);
      }
    };

    eventSource.onerror = () => {
      setError('Connection lost');
      setIsRunning(false);
      setCurrentPhase('');
      eventSource.close();
      eventSourceRef.current = null;
    };
  }, [selectedCase, selectedSetup, selectedModel, stopDebate]);

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const resetDebate = () => {
    setEvents([]);
    setCurrentCase(null);
    setCurrentPhase('');
  };

  // Show landing page
  if (showLanding) {
    return (
      <ConfigProvider
        theme={{
          token: {
            colorPrimary: '#000',
            borderRadius: 8,
            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif',
          },
        }}
      >
        <LandingPage onEnter={() => setShowLanding(false)} />
      </ConfigProvider>
    );
  }

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#000',
          borderRadius: 8,
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, sans-serif',
        },
      }}
    >
      <Layout style={{ minHeight: '100vh', width: '100vw', background: '#f5f5f5' }}>
        {/* Header */}
        <div style={{
          padding: '12px 24px',
          background: '#fff',
          borderBottom: '1px solid #eee',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <Button
              type="text"
              icon={<ArrowLeftOutlined />}
              onClick={() => setShowLanding(true)}
              style={{ marginRight: 8 }}
            >
              Back
            </Button>
            <div>
              <Title level={4} style={{ margin: 0, fontWeight: 600 }}>FactTrace</Title>
            </div>
          </div>
          <Tag color={isConnected ? 'success' : 'error'}>
            {isConnected ? 'Connected' : 'Offline'}
          </Tag>
        </div>

        <Content style={{ padding: 24 }}>
          {error && (
            <Alert
              message={error}
              type="error"
              closable
              onClose={() => setError(null)}
              style={{ marginBottom: 16 }}
            />
          )}

          <Row gutter={20}>
            {/* Left Panel - Configuration */}
            <Col xs={24} md={8} lg={6} xl={5}>
              <CaseSelector
                cases={cases}
                setups={setups}
                selectedCase={selectedCase}
                selectedSetup={selectedSetup}
                selectedModel={selectedModel}
                onCaseChange={setSelectedCase}
                onSetupChange={setSelectedSetup}
                onModelChange={setSelectedModel}
                onStart={startDebate}
                onStop={stopDebate}
                isRunning={isRunning}
              />
            </Col>

            {/* Right Panel - Debate */}
            <Col xs={24} md={16} lg={18} xl={19}>
              <Card
                title={
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span>
                      {currentCase ? (
                        <>Case {currentCase.id}: {currentCase.name}</>
                      ) : (
                        'Debate Arena'
                      )}
                    </span>
                    {events.length > 0 && !isRunning && (
                      <Button size="small" icon={<ReloadOutlined />} onClick={resetDebate} type="text">
                        Clear
                      </Button>
                    )}
                  </div>
                }
                style={{ minHeight: 500 }}
              >
                {currentCase && (
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr 1fr',
                    gap: 16,
                    marginBottom: 20,
                    padding: 16,
                    background: '#fafafa',
                    borderRadius: 8
                  }}>
                    <div>
                      <Text type="secondary" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                        Claim
                      </Text>
                      <div style={{ marginTop: 6, fontSize: 13, lineHeight: 1.6 }}>
                        {currentCase.claim}
                      </div>
                    </div>
                    <div>
                      <Text type="secondary" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                        Source Truth
                      </Text>
                      <div style={{ marginTop: 6, fontSize: 13, lineHeight: 1.6 }}>
                        {currentCase.truth}
                      </div>
                    </div>
                  </div>
                )}

                {events.length > 0 ? (
                  <DebateTimeline
                    events={events}
                    currentPhase={currentPhase}
                    thinkingAgent={thinkingAgent}
                  />
                ) : (
                  <div style={{ textAlign: 'center', padding: '80px 20px' }}>
                    <div style={{ fontSize: 48, marginBottom: 16 }}>⚖️</div>
                    <Title level={5} style={{ fontWeight: 500, marginBottom: 8 }}>
                      Ready to Verify
                    </Title>
                    <Text type="secondary">
                      Configure the setup and click Start Debate
                    </Text>
                  </div>
                )}
              </Card>
            </Col>
          </Row>
        </Content>
      </Layout>
    </ConfigProvider>
  );
}

export default App;

import { Typography, Tag } from 'antd';
import { LoadingOutlined, CheckCircleOutlined, SwapOutlined } from '@ant-design/icons';
import type { AgentVerdict, AgentResponse, FinalVerdict, AgentInfo } from '../types';
import { ChatBubble } from './ChatBubble';
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

interface RoundData {
  round: number;
  verdicts: AgentVerdict[];
  isComplete: boolean;
}

export function DebateTimeline({ events, currentPhase, thinkingAgent }: DebateTimelineProps) {
  const agents = events.find((e) => e.type === 'agents')?.data as AgentInfo[] | undefined;
  const setup = events.find((e) => e.type === 'setup')?.data as { name: string; paradigm: string } | undefined;
  const allVerdicts = events.filter((e) => e.type === 'agent_verdict').map((e) => e.data as AgentVerdict);
  const responses = events.filter((e) => e.type === 'agent_response').map((e) => e.data as AgentResponse);
  const finalVerdict = events.find((e) => e.type === 'final_verdict')?.data as FinalVerdict | undefined;
  const statusEvents = events.filter((e) => e.type === 'status').map((e) => e.data as string);

  const paradigm = setup?.paradigm || 'baseline';
  const isIterative = paradigm === 'iterative';
  const isAdversarial = paradigm === 'adversarial';
  const isCriticProposer = paradigm === 'critic-proposer';

  // Group verdicts by round for iterative paradigm
  const groupVerdictsByRound = (): RoundData[] => {
    if (!agents || agents.length === 0) return [];

    const rounds: RoundData[] = [];
    const agentCount = agents.length;
    let currentRound = 1;
    let roundVerdicts: AgentVerdict[] = [];

    for (const verdict of allVerdicts) {
      roundVerdicts.push(verdict);
      if (roundVerdicts.length === agentCount) {
        rounds.push({
          round: currentRound,
          verdicts: [...roundVerdicts],
          isComplete: true,
        });
        currentRound++;
        roundVerdicts = [];
      }
    }

    // Add incomplete round if any verdicts remain
    if (roundVerdicts.length > 0) {
      rounds.push({
        round: currentRound,
        verdicts: roundVerdicts,
        isComplete: false,
      });
    }

    return rounds;
  };

  // Calculate consensus for a round
  const getConsensus = (verdicts: AgentVerdict[]): { agreed: boolean; verdict: string; count: number } => {
    const counts: Record<string, number> = {};
    verdicts.forEach((v) => {
      counts[v.verdict] = (counts[v.verdict] || 0) + 1;
    });
    const maxVerdict = Object.entries(counts).sort((a, b) => b[1] - a[1])[0];
    return {
      agreed: maxVerdict[1] === verdicts.length,
      verdict: maxVerdict[0],
      count: maxVerdict[1],
    };
  };

  const rounds = isIterative ? groupVerdictsByRound() : [];

  return (
    <div>
      {/* Phase Header */}
      {currentPhase && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '12px 16px',
          background: 'linear-gradient(135deg, #F8F6FC 0%, #fff 100%)',
          borderRadius: 10,
          marginBottom: 20,
          border: '1px solid #E8E4F0',
        }}>
          <LoadingOutlined style={{ fontSize: 14, color: '#5B4B8A' }} />
          <Text strong style={{ fontSize: 14, color: '#2D2255' }}>{currentPhase}</Text>
        </div>
      )}

      {/* Chat Container */}
      <div style={{
        background: '#fafafa',
        borderRadius: 16,
        padding: 20,
        minHeight: 200,
        border: '1px solid #E8E4F0',
      }}>
        {/* ====== ITERATIVE PARADIGM - Round-by-Round Chat ====== */}
        {isIterative && rounds.length > 0 && (
          <div>
            {rounds.map((round, idx) => {
              const consensus = getConsensus(round.verdicts);
              const isLastRound = idx === rounds.length - 1;

              return (
                <div key={round.round}>
                  {/* Round Header */}
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '16px 0',
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 10,
                      padding: '6px 16px',
                      background: '#fff',
                      borderRadius: 20,
                      border: '1px solid #E8E4F0',
                      boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
                    }}>
                      <div style={{
                        width: 24,
                        height: 24,
                        borderRadius: '50%',
                        background: round.isComplete ? '#5B4B8A' : '#E8E4F0',
                        color: round.isComplete ? '#fff' : '#5B4B8A',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontWeight: 700,
                        fontSize: 12,
                      }}>
                        {round.round}
                      </div>
                      <Text strong style={{ fontSize: 13, color: '#2D2255' }}>
                        Round {round.round}
                      </Text>
                      {round.isComplete && (
                        <>
                          {consensus.agreed ? (
                            <Tag color="success" style={{ margin: 0, fontSize: 11 }}>
                              <CheckCircleOutlined /> Consensus
                            </Tag>
                          ) : (
                            <Tag color="warning" style={{ margin: 0, fontSize: 11 }}>
                              <SwapOutlined /> Split {consensus.count}/{round.verdicts.length}
                            </Tag>
                          )}
                        </>
                      )}
                    </div>
                  </div>

                  {/* Chat Bubbles for this round */}
                  <div style={{ marginBottom: 8 }}>
                    {round.verdicts.map((verdict) => {
                      const agent = agents?.find((a) => a.name === verdict.agent_name);
                      return (
                        <ChatBubble
                          key={`${round.round}-${verdict.agent_name}`}
                          name={verdict.agent_name}
                          color={agent?.color || '#5B4B8A'}
                          verdict={verdict}
                          isAdversarial={verdict.agent_name.includes('Devil')}
                        />
                      );
                    })}

                    {/* Show thinking bubbles for agents not yet responded */}
                    {!round.isComplete && agents && agents
                      .filter((a) => !round.verdicts.find((v) => v.agent_name === a.name))
                      .map((agent) => (
                        <ChatBubble
                          key={`${round.round}-${agent.name}-thinking`}
                          name={agent.name}
                          color={agent.color}
                          isThinking={thinkingAgent === agent.name}
                          isAdversarial={agent.name.includes('Devil')}
                        />
                      ))}
                  </div>

                  {/* Round transition */}
                  {!isLastRound && round.isComplete && (
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      padding: '12px 0',
                      color: '#9B8BC8',
                    }}>
                      <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 8,
                        padding: '6px 12px',
                        background: '#F8F6FC',
                        borderRadius: 12,
                        fontSize: 12,
                      }}>
                        <SwapOutlined />
                        <span>Agents reviewing positions...</span>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}

            {/* Consensus Status */}
            {statusEvents.length > 0 && (
              <div style={{
                textAlign: 'center',
                marginTop: 16,
              }}>
                <div style={{
                  display: 'inline-block',
                  padding: '8px 16px',
                  background: '#fff',
                  borderRadius: 8,
                  border: '1px solid #E8E4F0',
                }}>
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {statusEvents[statusEvents.length - 1]}
                  </Text>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ====== ADVERSARIAL PARADIGM ====== */}
        {isAdversarial && allVerdicts.length > 0 && (
          <div>
            {/* VS Header */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 20,
            }}>
              <div style={{
                padding: '8px 20px',
                background: 'linear-gradient(135deg, #2D2255 0%, #5B4B8A 100%)',
                color: '#fff',
                borderRadius: 20,
                fontWeight: 700,
                fontSize: 13,
              }}>
                ⚔️ Adversarial Debate
              </div>
            </div>

            {/* Chat bubbles */}
            {allVerdicts.map((verdict) => {
              const agent = agents?.find((a) => a.name === verdict.agent_name);
              return (
                <ChatBubble
                  key={verdict.agent_name}
                  name={verdict.agent_name}
                  color={agent?.color || '#5B4B8A'}
                  verdict={verdict}
                  isAdversarial={verdict.agent_name.includes('Devil') || verdict.agent_name === 'Opponent'}
                />
              );
            })}
          </div>
        )}

        {/* ====== CRITIC-PROPOSER PARADIGM ====== */}
        {isCriticProposer && allVerdicts.length > 0 && (
          <div>
            {/* Pipeline indicator */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              marginBottom: 20,
              flexWrap: 'wrap',
            }}>
              {['Proposer', 'Critic', 'Synthesizer'].map((step, idx) => {
                const verdict = allVerdicts.find((v) => v.agent_name === step);
                const isComplete = !!verdict;
                const isActive = !isComplete && allVerdicts.length === idx;

                return (
                  <div key={step} style={{ display: 'flex', alignItems: 'center' }}>
                    <div style={{
                      padding: '6px 14px',
                      background: isComplete ? '#5B4B8A' : isActive ? '#F8F6FC' : '#fff',
                      color: isComplete ? '#fff' : '#666',
                      borderRadius: 16,
                      fontSize: 12,
                      fontWeight: 500,
                      border: '1px solid #E8E4F0',
                    }}>
                      {isComplete && <CheckCircleOutlined style={{ marginRight: 6 }} />}
                      {isActive && <LoadingOutlined style={{ marginRight: 6 }} />}
                      {step}
                    </div>
                    {idx < 2 && (
                      <span style={{ margin: '0 8px', color: '#ccc' }}>→</span>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Chat bubbles */}
            {allVerdicts.map((verdict) => {
              const agent = agents?.find((a) => a.name === verdict.agent_name);
              return (
                <ChatBubble
                  key={verdict.agent_name}
                  name={verdict.agent_name}
                  color={agent?.color || '#5B4B8A'}
                  verdict={verdict}
                  isAdversarial={verdict.agent_name.includes('Devil') || verdict.agent_name === 'Critic'}
                />
              );
            })}
          </div>
        )}

        {/* ====== DEFAULT/JURY PARADIGM ====== */}
        {!isIterative && !isAdversarial && !isCriticProposer && agents && agents.length > 0 && (
          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 20,
            }}>
              <div style={{
                padding: '6px 16px',
                background: '#fff',
                borderRadius: 16,
                border: '1px solid #E8E4F0',
                fontSize: 12,
                color: '#5B4B8A',
                fontWeight: 500,
              }}>
                🏛️ Tribunal Analysis
              </div>
            </div>

            {/* Chat bubbles for each agent */}
            {agents.map((agent) => {
              const verdict = allVerdicts.find((v) => v.agent_name === agent.name);
              const isThinking = thinkingAgent === agent.name && !verdict;
              return (
                <ChatBubble
                  key={agent.name}
                  name={agent.name}
                  color={agent.color}
                  verdict={verdict}
                  isThinking={isThinking}
                  isAdversarial={agent.name.includes('Devil')}
                />
              );
            })}
          </div>
        )}

        {/* Single Agent fallback */}
        {!agents && allVerdicts.length > 0 && !isIterative && (
          <div>
            {allVerdicts.map((verdict) => (
              <ChatBubble
                key={verdict.agent_name}
                name={verdict.agent_name}
                color={verdict.color || '#5B4B8A'}
                verdict={verdict}
              />
            ))}
          </div>
        )}

        {/* Deliberation Responses */}
        {responses.length > 0 && (
          <div style={{ marginTop: 20 }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: 16,
            }}>
              <div style={{
                padding: '6px 16px',
                background: '#fff',
                borderRadius: 16,
                border: '1px solid #E8E4F0',
                fontSize: 12,
                color: '#5B4B8A',
                fontWeight: 500,
              }}>
                💬 Cross-Examination
              </div>
            </div>
            {responses.map((response, i) => (
              <ChatBubble
                key={i}
                name={response.agent_name}
                color={response.color}
                response={response.response}
              />
            ))}
          </div>
        )}

        {/* No messages yet */}
        {allVerdicts.length === 0 && !currentPhase && (
          <div style={{
            textAlign: 'center',
            padding: '40px 20px',
            color: '#999',
          }}>
            <div style={{ fontSize: 32, marginBottom: 12 }}>💬</div>
            <Text type="secondary">
              Agents will appear here once the investigation starts
            </Text>
          </div>
        )}
      </div>

      {/* Final Verdict */}
      {finalVerdict && (
        <div style={{ marginTop: 20 }}>
          {/* Judge announcement */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: 16,
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '10px 20px',
              background: 'linear-gradient(135deg, #2D2255 0%, #5B4B8A 100%)',
              borderRadius: 20,
              color: '#fff',
            }}>
              <span style={{ fontSize: 18 }}>⚖️</span>
              <Text strong style={{ color: '#fff', fontSize: 14 }}>
                Final Verdict
              </Text>
            </div>
          </div>

          <VerdictCard verdict={finalVerdict} />
        </div>
      )}
    </div>
  );
}

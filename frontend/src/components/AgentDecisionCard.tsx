import { AgentDecision } from '../types';
import { formatDistanceToNow } from 'date-fns';
import { Bot, CheckCircle, XCircle } from 'lucide-react';

interface AgentDecisionCardProps {
  decision: AgentDecision;
  onApprove?: (id: string) => void;
  onOverride?: (id: string) => void;
}

export default function AgentDecisionCard({
  decision,
  onApprove,
  onOverride,
}: AgentDecisionCardProps) {
  const getStatusBadge = (status: string) => {
    const styles = {
      pending: 'badge-pending',
      approved: 'badge-success',
      rejected: 'badge-critical',
      overridden: 'badge-high',
    };
    return styles[status as keyof typeof styles] || 'badge-pending';
  };

  const getConfidenceBadge = (score: number) => {
    if (score >= 0.8) return 'badge-success';
    if (score >= 0.6) return 'badge-medium';
    return 'badge-high';
  };

  return (
    <div className="card">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-purple-600/10 rounded-lg">
            <Bot className="text-purple-500" size={20} />
          </div>
          <div>
            <h4 className="font-semibold text-white">{decision.agent_name}</h4>
            <p className="text-sm text-dark-muted">{decision.decision_type}</p>
          </div>
        </div>
        <span className={`badge ${getStatusBadge(decision.status)}`}>
          {decision.status}
        </span>
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-sm text-dark-muted mb-1">Confidence Score</p>
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-dark-bg rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${decision.confidence_score * 100}%` }}
              />
            </div>
            <span className={`badge ${getConfidenceBadge(decision.confidence_score)}`}>
              {(decision.confidence_score * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        <div>
          <p className="text-sm text-dark-muted mb-1">Reasoning</p>
          <p className="text-sm text-white">{decision.reasoning}</p>
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-dark-border">
          <p className="text-xs text-dark-muted">
            {formatDistanceToNow(new Date(decision.created_at), { addSuffix: true })}
          </p>

          {decision.status === 'pending' && (
            <div className="flex gap-2">
              <button
                onClick={() => onApprove?.(decision.id)}
                className="btn btn-success text-sm flex items-center gap-1"
              >
                <CheckCircle size={16} />
                Approve
              </button>
              <button
                onClick={() => onOverride?.(decision.id)}
                className="btn btn-danger text-sm flex items-center gap-1"
              >
                <XCircle size={16} />
                Override
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

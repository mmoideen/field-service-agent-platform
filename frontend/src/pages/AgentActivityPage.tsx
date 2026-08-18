import { useCallback, useEffect, useState } from 'react';
import Layout from '../components/Layout';
import AgentDecisionCard from '../components/AgentDecisionCard';
import { AgentDecision } from '../types';
import { decisionsApi } from '../services/api';

export default function AgentActivityPage() {
  const [decisions, setDecisions] = useState<AgentDecision[]>([]);
  const [filter, setFilter] = useState<string>('');

  const loadDecisions = useCallback(async () => {
    try {
      const response = await decisionsApi.list(filter) as { decisions: AgentDecision[] };
      setDecisions(response.decisions);
    } catch (error) {
      console.error('Failed to load decisions:', error);
    }
  }, [filter]);

  useEffect(() => {
    loadDecisions();
  }, [loadDecisions]);

  const handleApprove = async (id: string) => {
    try {
      await decisionsApi.approve(id, 'dashboard_user');
      loadDecisions();
    } catch (error) {
      console.error('Failed to approve decision:', error);
    }
  };

  const handleOverride = async (id: string) => {
    const reason = prompt('Enter override reason:');
    if (!reason) return;

    try {
      await decisionsApi.override(id, {
        override_reason: reason,
        overridden_by: 'dashboard_user',
      });
      loadDecisions();
    } catch (error) {
      console.error('Failed to override decision:', error);
    }
  };

  return (
    <Layout title="Agent Activity">
      <div className="space-y-6">
        <div className="flex gap-4">
          <button
            onClick={() => setFilter('')}
            className={`btn ${!filter ? 'btn-primary' : 'btn-secondary'}`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`btn ${filter === 'pending' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Pending
          </button>
          <button
            onClick={() => setFilter('approved')}
            className={`btn ${filter === 'approved' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Approved
          </button>
          <button
            onClick={() => setFilter('overridden')}
            className={`btn ${filter === 'overridden' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Overridden
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {decisions.map((decision) => (
            <AgentDecisionCard
              key={decision.id}
              decision={decision}
              onApprove={handleApprove}
              onOverride={handleOverride}
            />
          ))}

          {decisions.length === 0 && (
            <p className="text-dark-muted col-span-full text-center py-8">
              No agent decisions found
            </p>
          )}
        </div>
      </div>
    </Layout>
  );
}

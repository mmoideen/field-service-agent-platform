import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import StatCard from '../components/StatCard';
import AgentDecisionCard from '../components/AgentDecisionCard';
import { Wrench, Users, FileCheck, Package, Clock, TrendingUp } from 'lucide-react';
import { decisionsApi } from '../services/api';
import { AgentDecision } from '../types';

export default function Dashboard() {
  const [recentDecisions, setRecentDecisions] = useState<AgentDecision[]>([]);

  useEffect(() => {
    loadRecentDecisions();
  }, []);

  const loadRecentDecisions = async () => {
    try {
      const response = await decisionsApi.list() as { decisions: AgentDecision[] };
      setRecentDecisions(response.decisions.slice(0, 5));
    } catch (error) {
      console.error('Failed to load decisions:', error);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await decisionsApi.approve(id, 'dashboard_user');
      loadRecentDecisions();
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
      loadRecentDecisions();
    } catch (error) {
      console.error('Failed to override decision:', error);
    }
  };

  return (
    <Layout title="Operations Dashboard">
      <div className="space-y-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Open Tickets"
            value={12}
            icon={Wrench}
            trend={{ value: 8, positive: false }}
          />
          <StatCard
            title="Available Technicians"
            value="15/20"
            icon={Users}
            subtitle="75% utilization"
          />
          <StatCard
            title="Pending Warranty Claims"
            value={8}
            icon={FileCheck}
            trend={{ value: 12, positive: true }}
          />
          <StatCard
            title="Low Stock Parts"
            value={5}
            icon={Package}
            trend={{ value: 3, positive: true }}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <Clock size={20} className="text-blue-500" />
              Response Time Metrics
            </h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-dark-muted">Average Response Time</span>
                  <span className="text-white font-medium">2.4 hours</span>
                </div>
                <div className="bg-dark-bg rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: '76%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-dark-muted">SLA Compliance</span>
                  <span className="text-white font-medium">94%</span>
                </div>
                <div className="bg-dark-bg rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: '94%' }} />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-dark-muted">First Call Resolution</span>
                  <span className="text-white font-medium">87%</span>
                </div>
                <div className="bg-dark-bg rounded-full h-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: '87%' }} />
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <TrendingUp size={20} className="text-green-500" />
              Agent Performance
            </h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">Dispatch Optimizer</p>
                  <p className="text-xs text-dark-muted">Avg confidence: 89%</p>
                </div>
                <span className="badge badge-success">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">Warranty Triage</p>
                  <p className="text-xs text-dark-muted">Avg confidence: 92%</p>
                </div>
                <span className="badge badge-success">Active</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                <div>
                  <p className="text-sm font-medium text-white">Parts Procurement</p>
                  <p className="text-xs text-dark-muted">Avg confidence: 85%</p>
                </div>
                <span className="badge badge-success">Active</span>
              </div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-white mb-4">Recent Agent Decisions</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {recentDecisions.length === 0 ? (
              <p className="text-dark-muted col-span-full text-center py-8">
                No recent agent decisions
              </p>
            ) : (
              recentDecisions.map((decision) => (
                <AgentDecisionCard
                  key={decision.id}
                  decision={decision}
                  onApprove={handleApprove}
                  onOverride={handleOverride}
                />
              ))
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}

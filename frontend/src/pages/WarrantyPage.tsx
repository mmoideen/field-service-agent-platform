import { useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { WarrantyClaim } from '../types';
import { warrantyApi } from '../services/api';
import { formatDistanceToNow } from 'date-fns';
import { FileCheck, DollarSign, TrendingUp } from 'lucide-react';

export default function WarrantyPage() {
  const [claims, setClaims] = useState<WarrantyClaim[]>([]);
  const [filter, setFilter] = useState<string>('');

  useEffect(() => {
    loadClaims();
  }, [filter]);

  const loadClaims = async () => {
    try {
      const response = await warrantyApi.list(filter) as { claims: WarrantyClaim[] };
      setClaims(response.claims);
    } catch (error) {
      console.error('Failed to load warranty claims:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      pending: 'badge-pending',
      approved: 'badge-success',
      rejected: 'badge-critical',
      expired: 'badge-high',
    };
    return styles[status as keyof typeof styles] || 'badge-pending';
  };

  return (
    <Layout title="Warranty Claims">
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
            onClick={() => setFilter('rejected')}
            className={`btn ${filter === 'rejected' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Rejected
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {claims.map((claim) => (
            <div key={claim.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-600/10 rounded-lg">
                    <FileCheck className="text-blue-500" size={20} />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">{claim.product_model}</h4>
                    <p className="text-sm text-dark-muted">SN: {claim.product_serial}</p>
                  </div>
                </div>
                <span className={`badge ${getStatusBadge(claim.status)}`}>
                  {claim.status}
                </span>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                  <div className="flex items-center gap-2">
                    <TrendingUp size={16} className="text-green-500" />
                    <span className="text-sm text-dark-muted">Coverage</span>
                  </div>
                  <span className="text-white font-medium">
                    {claim.coverage_percentage}%
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                  <div className="flex items-center gap-2">
                    <DollarSign size={16} className="text-yellow-500" />
                    <span className="text-sm text-dark-muted">Estimated Cost</span>
                  </div>
                  <span className="text-white font-medium">
                    ${claim.estimated_cost.toFixed(2)}
                  </span>
                </div>

                {claim.approved_amount !== undefined && claim.approved_amount !== null && (
                  <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                    <div className="flex items-center gap-2">
                      <DollarSign size={16} className="text-green-500" />
                      <span className="text-sm text-dark-muted">Approved Amount</span>
                    </div>
                    <span className="text-green-500 font-medium">
                      ${claim.approved_amount.toFixed(2)}
                    </span>
                  </div>
                )}

                <div className="pt-3 border-t border-dark-border">
                  <p className="text-xs text-dark-muted">
                    Filed {formatDistanceToNow(new Date(claim.created_at), { addSuffix: true })}
                  </p>
                </div>
              </div>
            </div>
          ))}

          {claims.length === 0 && (
            <p className="text-dark-muted col-span-full text-center py-8">
              No warranty claims found
            </p>
          )}
        </div>
      </div>
    </Layout>
  );
}

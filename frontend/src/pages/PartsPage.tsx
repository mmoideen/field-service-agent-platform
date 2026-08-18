import { useCallback, useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { Part } from '../types';
import { partsApi } from '../services/api';
import { Package, AlertTriangle, TrendingDown, DollarSign } from 'lucide-react';

export default function PartsPage() {
  const [parts, setParts] = useState<Part[]>([]);
  const [showLowStockOnly, setShowLowStockOnly] = useState(false);

  const loadParts = useCallback(async () => {
    try {
      const response = await partsApi.list(showLowStockOnly) as { parts: Part[] };
      setParts(response.parts);
    } catch (error) {
      console.error('Failed to load parts:', error);
    }
  }, [showLowStockOnly]);

  useEffect(() => {
    loadParts();
  }, [loadParts]);

  const handleCheckProcurement = async (partId: string) => {
    try {
      const result = await partsApi.checkProcurement(partId);
      alert(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('Failed to check procurement:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      in_stock: 'badge-success',
      low_stock: 'badge-high',
      out_of_stock: 'badge-critical',
    };
    return styles[status as keyof typeof styles] || 'badge-pending';
  };

  return (
    <Layout title="Parts Inventory">
      <div className="space-y-6">
        <div className="flex gap-4">
          <button
            onClick={() => setShowLowStockOnly(false)}
            className={`btn ${!showLowStockOnly ? 'btn-primary' : 'btn-secondary'}`}
          >
            All Parts
          </button>
          <button
            onClick={() => setShowLowStockOnly(true)}
            className={`btn ${showLowStockOnly ? 'btn-primary' : 'btn-secondary'}`}
          >
            Low Stock Only
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
          {parts.map((part) => (
            <div key={part.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-purple-600/10 rounded-lg">
                    <Package className="text-purple-500" size={20} />
                  </div>
                  <div>
                    <h4 className="font-semibold text-white">{part.name}</h4>
                    <p className="text-sm text-dark-muted">{part.part_number}</p>
                  </div>
                </div>
                <span className={`badge ${getStatusBadge(part.status)}`}>
                  {part.status.replace('_', ' ')}
                </span>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                  <div className="flex items-center gap-2">
                    <Package size={16} className="text-blue-500" />
                    <span className="text-sm text-dark-muted">In Stock</span>
                  </div>
                  <span className="text-white font-medium">
                    {part.quantity_in_stock} units
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                  <div className="flex items-center gap-2">
                    <TrendingDown size={16} className="text-yellow-500" />
                    <span className="text-sm text-dark-muted">Reorder Point</span>
                  </div>
                  <span className="text-white font-medium">
                    {part.reorder_point} units
                  </span>
                </div>

                <div className="flex items-center justify-between p-3 bg-dark-bg rounded-lg">
                  <div className="flex items-center gap-2">
                    <DollarSign size={16} className="text-green-500" />
                    <span className="text-sm text-dark-muted">Unit Price</span>
                  </div>
                  <span className="text-white font-medium">
                    ${part.unit_price.toFixed(2)}
                  </span>
                </div>

                {part.quantity_in_stock < part.reorder_point && (
                  <button
                    onClick={() => handleCheckProcurement(part.id)}
                    className="btn btn-primary w-full text-sm flex items-center justify-center gap-2"
                  >
                    <AlertTriangle size={16} />
                    Check Procurement
                  </button>
                )}
              </div>
            </div>
          ))}

          {parts.length === 0 && (
            <p className="text-dark-muted col-span-full text-center py-8">
              No parts found
            </p>
          )}
        </div>
      </div>
    </Layout>
  );
}

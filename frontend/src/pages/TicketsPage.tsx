import { useCallback, useEffect, useState } from 'react';
import Layout from '../components/Layout';
import { ServiceTicket } from '../types';
import { ticketApi } from '../services/api';
import { MapPin, Clock, User } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function TicketsPage() {
  const [tickets, setTickets] = useState<ServiceTicket[]>([]);
  const [filter, setFilter] = useState<string>('');

  const loadTickets = useCallback(async () => {
    try {
      const response = await ticketApi.list(filter) as { tickets: ServiceTicket[] };
      setTickets(response.tickets);
    } catch (error) {
      console.error('Failed to load tickets:', error);
    }
  }, [filter]);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  const getPriorityBadge = (priority: string) => {
    const styles = {
      critical: 'badge-critical',
      high: 'badge-high',
      medium: 'badge-medium',
      low: 'badge-low',
    };
    return styles[priority as keyof typeof styles] || 'badge-medium';
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      open: 'badge-high',
      assigned: 'badge-medium',
      in_progress: 'badge-medium',
      completed: 'badge-success',
      cancelled: 'badge-pending',
    };
    return styles[status as keyof typeof styles] || 'badge-pending';
  };

  return (
    <Layout title="Service Tickets">
      <div className="space-y-6">
        <div className="flex gap-4">
          <button
            onClick={() => setFilter('')}
            className={`btn ${!filter ? 'btn-primary' : 'btn-secondary'}`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('open')}
            className={`btn ${filter === 'open' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Open
          </button>
          <button
            onClick={() => setFilter('in_progress')}
            className={`btn ${filter === 'in_progress' ? 'btn-primary' : 'btn-secondary'}`}
          >
            In Progress
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`btn ${filter === 'completed' ? 'btn-primary' : 'btn-secondary'}`}
          >
            Completed
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {tickets.map((ticket) => (
            <div key={ticket.id} className="card">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="text-lg font-semibold text-white">{ticket.title}</h4>
                  <p className="text-sm text-dark-muted mt-1">{ticket.description}</p>
                </div>
                <div className="flex gap-2">
                  <span className={`badge ${getPriorityBadge(ticket.priority)}`}>
                    {ticket.priority}
                  </span>
                  <span className={`badge ${getStatusBadge(ticket.status)}`}>
                    {ticket.status}
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div className="flex items-center gap-2 text-dark-muted">
                  <User size={16} />
                  <span>{ticket.customer_name}</span>
                </div>
                <div className="flex items-center gap-2 text-dark-muted">
                  <MapPin size={16} />
                  <span>{ticket.location?.city}, {ticket.location?.state}</span>
                </div>
                <div className="flex items-center gap-2 text-dark-muted">
                  <Clock size={16} />
                  <span>{formatDistanceToNow(new Date(ticket.created_at), { addSuffix: true })}</span>
                </div>
              </div>
            </div>
          ))}

          {tickets.length === 0 && (
            <p className="text-dark-muted text-center py-8">No tickets found</p>
          )}
        </div>
      </div>
    </Layout>
  );
}

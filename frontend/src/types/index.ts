export interface ServiceTicket {
  id: string;
  title: string;
  description: string;
  service_type: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
  customer_name: string;
  location: {
    address: string;
    city: string;
    state: string;
    latitude: number;
    longitude: number;
  };
  assigned_technician_id?: string;
  created_at: string;
  updated_at: string;
}

export interface Technician {
  id: string;
  name: string;
  email: string;
  phone: string;
  is_available: boolean;
  skills: {
    skills: Array<{
      name: string;
      category: string;
      level: string;
    }>;
  };
  home_location: {
    latitude: number;
    longitude: number;
    address: string;
  };
}

export interface WarrantyClaim {
  id: string;
  ticket_id: string;
  product_model: string;
  product_serial: string;
  status: 'pending' | 'approved' | 'rejected' | 'expired';
  coverage_percentage: number;
  estimated_cost: number;
  approved_amount?: number;
  created_at: string;
}

export interface Part {
  id: string;
  part_number: string;
  name: string;
  category: string;
  quantity_in_stock: number;
  reorder_point: number;
  status: 'in_stock' | 'low_stock' | 'out_of_stock';
  unit_price: number;
}

export interface AgentDecision {
  id: string;
  agent_name: string;
  decision_type: string;
  entity_id: string;
  entity_type: string;
  reasoning: string;
  confidence_score: number;
  recommendation: Record<string, unknown>;
  status: 'pending' | 'approved' | 'rejected' | 'overridden';
  created_at: string;
  human_override_reason?: string;
  overridden_by?: string;
}

export interface DashboardStats {
  total_tickets_open: number;
  total_tickets_today: number;
  technicians_available: number;
  technicians_total: number;
  warranty_claims_pending: number;
  parts_low_stock: number;
  average_response_time_hours: number;
}

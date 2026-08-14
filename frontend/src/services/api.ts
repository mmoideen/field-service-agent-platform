const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = {
  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`);
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },

  async patch<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }
    return response.json();
  },
};

export const ticketApi = {
  list: (status?: string) =>
    api.get(`/api/tickets${status ? `?status=${status}` : ''}`),
  get: (id: string) => api.get(`/api/tickets/${id}`),
  create: (data: unknown) => api.post('/api/tickets/', data),
  update: (id: string, data: unknown) => api.patch(`/api/tickets/${id}`, data),
};

export const technicianApi = {
  list: (availableOnly = false) =>
    api.get(`/api/technicians${availableOnly ? '?available_only=true' : ''}`),
  get: (id: string) => api.get(`/api/technicians/${id}`),
};

export const warrantyApi = {
  list: (status?: string) =>
    api.get(`/api/warranty${status ? `?status=${status}` : ''}`),
  get: (id: string) => api.get(`/api/warranty/${id}`),
  create: (data: unknown) => api.post('/api/warranty/', data),
};

export const partsApi = {
  list: (lowStockOnly = false) =>
    api.get(`/api/parts${lowStockOnly ? '?low_stock_only=true' : ''}`),
  get: (id: string) => api.get(`/api/parts/${id}`),
  checkProcurement: (id: string) => api.post(`/api/parts/${id}/check-procurement`, {}),
};

export const decisionsApi = {
  list: (status?: string) =>
    api.get(`/api/decisions${status ? `?status=${status}` : ''}`),
  get: (id: string) => api.get(`/api/decisions/${id}`),
  override: (id: string, data: unknown) =>
    api.post(`/api/decisions/${id}/override`, data),
  approve: (id: string, approvedBy: string) =>
    api.post(`/api/decisions/${id}/approve?approved_by=${approvedBy}`, {}),
};

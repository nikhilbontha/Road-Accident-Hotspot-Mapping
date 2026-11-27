const isLocal = typeof window !== 'undefined' && (
  window.location.hostname === 'localhost' ||
  window.location.hostname === '127.0.0.1' ||
  window.location.hostname === '0.0.0.0'
);

export const API_BASE = (
  ((import.meta as any).env?.VITE_API_BASE_URL as string) ||
  (isLocal ? '/api/v1' : 'https://road-accident-hotspot-mapping.onrender.com/api/v1')
).replace(/\/$/, '');

export function getApiUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  const cleanPath = path.replace(/^\/api\/v1/, '').replace(/^\//, '');
  return `${API_BASE}/${cleanPath}`;
}

export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('rah_token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    (headers as any)['Authorization'] = `Bearer ${token}`;
  }

  const url = getApiUrl(endpoint);

  const response = await fetch(url, {
    ...options,
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const errorMsg = data?.detail || data?.message || 'An unexpected error occurred';
    throw new Error(errorMsg);
  }

  return data as T;
}

export const authApi = {
  register: (payload: any) =>
    apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  login: (email: string, password: string) =>
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => apiRequest('/auth/me'),

  logout: () => apiRequest('/auth/logout', { method: 'POST' }),
};

export const usersApi = {
  list: (params?: { role?: string; status?: string; search?: string }) => {
    const query = new URLSearchParams();
    if (params?.role) query.set('role', params.role);
    if (params?.status) query.set('status', params.status);
    if (params?.search) query.set('search', params.search);
    return apiRequest(`/users?${query.toString()}`);
  },

  create: (payload: any) =>
    apiRequest('/users', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  update: (id: string, payload: any) =>
    apiRequest(`/users/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    }),

  approve: (id: string) =>
    apiRequest(`/users/${id}/approve`, {
      method: 'POST',
    }),

  reject: (id: string) =>
    apiRequest(`/users/${id}/reject`, {
      method: 'POST',
    }),

  deactivate: (id: string) =>
    apiRequest(`/users/${id}/deactivate`, {
      method: 'POST',
    }),
};

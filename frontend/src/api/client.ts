import axios from 'axios';

const API_BASE = '/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

let accessToken: string | null = null;

export function setAuthToken(token: string | null) {
  accessToken = token;
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      setAuthToken(null);
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const domainsApi = {
  list: (params?: { limit?: number; offset?: number }) =>
    api.get<{ domains: any[]; total: number }>('/domains', { params }),
  get: (id: number) => api.get<any>(`/domains/${id}`),
  create: (data: any) => api.post<any>('/domains', data),
};

export const conceptsApi = {
  search: (params: {
    q?: string;
    domain_id?: number;
    subject_id?: number;
    age_min?: number;
    age_max?: number;
    difficulty_min?: number;
    difficulty_max?: number;
    limit?: number;
    offset?: number;
  }) => api.get<{ concepts: any[]; total: number }>('/concepts', { params }),
  get: (id: number) => api.get<any>(`/concepts/${id}`),
  getGraph: (id: number, depth?: number) =>
    api.get<any>(`/concepts/${id}/graph`, { params: { depth } }),
};

export const progressApi = {
  listProfiles: (userId: string, params?: { limit?: number; offset?: number }) =>
    api.get<{ profiles: any[]; total: number }>('/profiles', { params: { user_id: userId, ...params } }),
  getProfile: (id: number) => api.get<any>(`/profiles/${id}`),
  createProfile: (userId: string, data: any) =>
    api.post<any>('/profiles', data, { params: { user_id: userId } }),
  updateProfile: (id: number, data: any) => api.patch<any>(`/profiles/${id}`, data),
  deleteProfile: (id: number) => api.delete(`/profiles/${id}`),
  getProgress: (profileId: number, params?: {
    state?: string;
    domain_id?: number;
    subject_id?: number;
    limit?: number;
    offset?: number;
  }) => api.get<{ progress: any[]; total: number }>(`/profiles/${profileId}/progress`, { params }),
  upsertProgress: (profileId: number, data: any) =>
    api.post<any>(`/profiles/${profileId}/progress`, data),
};

export const authApi = {
  me: () => api.get<any>('/auth/me'),
  login: () => api.get<{ url: string }>('/auth/login'),
};

export const importApi = {
  importTaxonomy: (file: File, domainName: string, domainDisplayName: string) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post<any>('/import/taxonomy', formData, {
      params: { domain_name: domainName, domain_display_name: domainDisplayName },
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

export default api;
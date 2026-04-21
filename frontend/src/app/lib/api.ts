import type {
  CommentRead,
  EventCategoryOptionsResponse,
  EventCreateBody,
  EventFilterParams,
  EventRead,
  EventWithInteractionsRead,
  PartnerSubmissionCreateBody,
  PartnerSubmissionRead,
  SuccessResponse,
  TokenPair,
  TrendEntryRead,
  UserRead,
} from './contracts';
import { getAccessToken } from './storage';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

interface RequestOptions extends RequestInit {
  auth?: boolean;
  authToken?: string;
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { auth = false, authToken, headers, ...rest } = options;
  const nextHeaders = new Headers(headers ?? {});
  nextHeaders.set('Content-Type', 'application/json');
  if (auth) {
    const token = authToken ?? getAccessToken();
    if (token) {
      nextHeaders.set('Authorization', `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: nextHeaders,
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const payload = await response.json();
      if (typeof payload?.detail === 'string') {
        message = payload.detail;
      }
    } catch {
      // Keep fallback message when body cannot be parsed.
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return {} as T;
  }
  return (await response.json()) as T;
}

export function login(email: string, password: string): Promise<TokenPair> {
  return request<TokenPair>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export function register(name: string, email: string, password: string): Promise<TokenPair> {
  return request<TokenPair>('/api/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      name,
      email,
      password,
      city_location: 'san diego',
    }),
  });
}

export function getMe(accessToken?: string): Promise<UserRead> {
  return request<UserRead>('/api/auth/me', {
    auth: true,
    authToken: accessToken,
  });
}

export function listEventsWithInteractions(
  filters: EventFilterParams = {}
): Promise<EventWithInteractionsRead[]> {
  const query = new URLSearchParams();
  query.set('region', 'san diego');
  if (filters.category && filters.category !== 'All Categories') {
    query.set('category', filters.category);
  }
  if (filters.neighborhood) {
    query.set('neighborhood', filters.neighborhood);
  }
  if (filters.starts_after) {
    query.set('starts_after', filters.starts_after);
  }
  if (filters.starts_before) {
    query.set('starts_before', filters.starts_before);
  }
  return request<EventWithInteractionsRead[]>(`/api/interactions?${query.toString()}`);
}

export function listTrends(): Promise<TrendEntryRead[]> {
  return request<TrendEntryRead[]>('/api/trends?region=san%20diego');
}

export function listCategories(): Promise<EventCategoryOptionsResponse> {
  return request<EventCategoryOptionsResponse>('/api/events/categories');
}

export function getEvent(id: number): Promise<EventRead> {
  return request<EventRead>(`/api/events/${id}`);
}

export function createEvent(payload: EventCreateBody): Promise<EventRead> {
  return request<EventRead>('/api/events', {
    method: 'POST',
    auth: true,
    body: JSON.stringify(payload),
  });
}

export function deleteEvent(id: number): Promise<SuccessResponse> {
  return request<SuccessResponse>(`/api/events/${id}`, {
    method: 'DELETE',
    auth: true,
  });
}

export function addAttending(eventId: number): Promise<SuccessResponse> {
  return request<SuccessResponse>(`/api/interactions/events/${eventId}/attending`, {
    method: 'PUT',
    auth: true,
  });
}

export function removeAttending(eventId: number): Promise<SuccessResponse> {
  return request<SuccessResponse>(`/api/interactions/events/${eventId}/attending`, {
    method: 'DELETE',
    auth: true,
  });
}

export function addComment(eventId: number, text: string): Promise<CommentRead> {
  return request<CommentRead>(`/api/interactions/events/${eventId}/comments`, {
    method: 'PUT',
    auth: true,
    body: JSON.stringify({ text }),
  });
}

export function submitPartnerEvent(payload: PartnerSubmissionCreateBody): Promise<PartnerSubmissionRead> {
  return request<PartnerSubmissionRead>('/api/partner-submissions', {
    method: 'POST',
    auth: true,
    body: JSON.stringify(payload),
  });
}

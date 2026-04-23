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
import {
  clearAuthTokens,
  getAccessToken,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
} from './storage';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

interface RequestOptions extends RequestInit {
  auth?: boolean;
  authToken?: string;
}

class ApiRequestError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiRequestError';
    this.status = status;
  }
}

export function isAuthError(error: unknown): boolean {
  return error instanceof ApiRequestError && error.status === 401;
}

async function parse_error_message(response: Response): Promise<string> {
  let message = `Request failed (${response.status})`;
  try {
    const payload = (await response.json()) as { detail?: string };
    if (typeof payload?.detail === 'string') {
      message = payload.detail;
    }
  } catch {
    // Keep fallback message when body cannot be parsed.
  }
  return message;
}

function parse_refreshed_token(payload: unknown): string | null {
  if (!payload || typeof payload !== 'object') {
    return null;
  }
  const tokenValue = (payload as { access_token?: unknown; accessToken?: unknown }).access_token
    ?? (payload as { access_token?: unknown; accessToken?: unknown }).accessToken;
  return typeof tokenValue === 'string' && tokenValue.trim() ? tokenValue : null;
}

function parse_refresh_fallback_token(payload: unknown): string | null {
  if (!payload || typeof payload !== 'object') {
    return null;
  }
  const refreshValue = (payload as { refresh_token?: unknown; refreshToken?: unknown }).refresh_token
    ?? (payload as { refresh_token?: unknown; refreshToken?: unknown }).refreshToken;
  return typeof refreshValue === 'string' && refreshValue.trim() ? refreshValue : null;
}

async function try_refresh_with_options(path: string, init: RequestInit): Promise<string | null> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    credentials: 'include',
  });
  if (!response.ok) {
    return null;
  }
  const payload = response.status === 204 ? null : ((await response.json()) as unknown);
  const nextAccessToken = parse_refreshed_token(payload);
  if (!nextAccessToken) {
    return null;
  }
  setAccessToken(nextAccessToken);
  const nextRefreshToken = parse_refresh_fallback_token(payload);
  if (nextRefreshToken) {
    setRefreshToken(nextRefreshToken);
  }
  return nextAccessToken;
}

async function refresh_access_token(): Promise<string | null> {
  const refreshPaths = ['/api/auth/refresh', '/api/auth/refresh-token'];

  for (const path of refreshPaths) {
    const cookieRefreshToken = await try_refresh_with_options(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (cookieRefreshToken) {
      return cookieRefreshToken;
    }
  }

  const fallbackRefreshToken = getRefreshToken();
  if (!fallbackRefreshToken) {
    return null;
  }

  for (const path of refreshPaths) {
    const bodyRefreshToken = await try_refresh_with_options(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: fallbackRefreshToken }),
    });
    if (bodyRefreshToken) {
      return bodyRefreshToken;
    }
  }

  return null;
}

async function request<T>(path: string, options: RequestOptions = {}, alreadyRetried = false): Promise<T> {
  const { auth = false, authToken, headers, ...rest } = options;
  const nextHeaders = new Headers(headers ?? {});
  if (rest.body && !nextHeaders.has('Content-Type')) {
    nextHeaders.set('Content-Type', 'application/json');
  }
  if (auth) {
    const token = authToken ?? getAccessToken();
    if (token) {
      nextHeaders.set('Authorization', `Bearer ${token}`);
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: nextHeaders,
    credentials: 'include',
  });

  if (!response.ok) {
    if (auth && response.status === 401 && !alreadyRetried) {
      const refreshedAccessToken = await refresh_access_token();
      if (refreshedAccessToken) {
        return request<T>(
          path,
          {
            ...options,
            authToken: refreshedAccessToken,
          },
          true
        );
      }
      clearAuthTokens();
      throw new ApiRequestError('Session expired. Please sign in again.', 401);
    }
    throw new ApiRequestError(await parse_error_message(response), response.status);
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

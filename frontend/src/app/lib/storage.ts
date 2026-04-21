import type { AppSession, UserRead } from './contracts';

const STORAGE_KEY = 'citypulse_session';
const PROFILE_OVERRIDES_KEY = 'citypulse_profile_overrides';

export interface ProfileOverride {
  displayName: string;
  bio: string;
  avatarUrl: string;
}

function defaultSession(): AppSession | null {
  return null;
}

export function getStorageData(): AppSession | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return defaultSession();
    }
    const parsed = JSON.parse(raw) as AppSession;
    if (!parsed?.accessToken || !parsed?.refreshToken || !parsed?.currentUser) {
      return defaultSession();
    }
    if (!Array.isArray(parsed.attendingEventIds)) {
      parsed.attendingEventIds = [];
    }
    return parsed;
  } catch (error) {
    console.error('Error reading from localStorage:', error);
    return defaultSession();
  }
}

export function saveStorageData(data: AppSession | null): void {
  try {
    if (data === null) {
      localStorage.removeItem(STORAGE_KEY);
      return;
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch (error) {
    console.error('Error writing to localStorage:', error);
  }
}

export function setSession(payload: { accessToken: string; refreshToken: string; currentUser: UserRead }): void {
  saveStorageData({
    accessToken: payload.accessToken,
    refreshToken: payload.refreshToken,
    currentUser: payload.currentUser,
    attendingEventIds: [],
  });
}

export function clearSession(): void {
  saveStorageData(null);
}

export function getAccessToken(): string | null {
  return getStorageData()?.accessToken ?? null;
}

export function getCurrentUser(): UserRead | null {
  return getStorageData()?.currentUser ?? null;
}

export function setCurrentUser(user: UserRead | null): void {
  const session = getStorageData();
  if (!session || !user) {
    clearSession();
    return;
  }
  saveStorageData({
    ...session,
    currentUser: user,
  });
}

export function isAttending(eventId: number): boolean {
  const session = getStorageData();
  return session?.attendingEventIds.includes(eventId) ?? false;
}

export function rememberAttending(eventId: number, attending: boolean): void {
  const session = getStorageData();
  if (!session) {
    return;
  }
  const existing = new Set(session.attendingEventIds);
  if (attending) {
    existing.add(eventId);
  } else {
    existing.delete(eventId);
  }
  saveStorageData({
    ...session,
    attendingEventIds: Array.from(existing),
  });
}

function getProfileOverridesData(): Record<string, ProfileOverride> {
  try {
    const raw = localStorage.getItem(PROFILE_OVERRIDES_KEY);
    if (!raw) {
      return {};
    }
    const parsed = JSON.parse(raw) as Record<string, ProfileOverride>;
    if (!parsed || typeof parsed !== 'object') {
      return {};
    }
    return parsed;
  } catch (error) {
    console.error('Error reading profile overrides from localStorage:', error);
    return {};
  }
}

function saveProfileOverridesData(data: Record<string, ProfileOverride>): void {
  try {
    localStorage.setItem(PROFILE_OVERRIDES_KEY, JSON.stringify(data));
  } catch (error) {
    console.error('Error writing profile overrides to localStorage:', error);
  }
}

export function getProfileOverride(userId: number): ProfileOverride | null {
  const allOverrides = getProfileOverridesData();
  return allOverrides[String(userId)] ?? null;
}

export function setProfileOverride(userId: number, override: ProfileOverride): void {
  const allOverrides = getProfileOverridesData();
  allOverrides[String(userId)] = override;
  saveProfileOverridesData(allOverrides);
}
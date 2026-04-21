import { User, Comment, Event } from './mockData';

interface StorageData {
  currentUser: User | null;
  attendingEvents: string[];
  comments: Comment[];
  customEvents: Event[];
}

const STORAGE_KEY = 'citypulse_data';

export function getStorageData(): StorageData {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (data) {
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('Error reading from localStorage:', error);
  }
  
  return {
    currentUser: null,
    attendingEvents: [],
    comments: [],
    customEvents: [],
  };
}

export function saveStorageData(data: Partial<StorageData>): void {
  try {
    const currentData = getStorageData();
    const newData = { ...currentData, ...data };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newData));
  } catch (error) {
    console.error('Error writing to localStorage:', error);
  }
}

export function getCurrentUser(): User | null {
  return getStorageData().currentUser;
}

export function setCurrentUser(user: User | null): void {
  saveStorageData({ currentUser: user });
}

export function isAttending(eventId: string): boolean {
  const data = getStorageData();
  return data.attendingEvents.includes(eventId);
}

export function toggleAttendance(eventId: string): boolean {
  const data = getStorageData();
  const isCurrentlyAttending = data.attendingEvents.includes(eventId);
  
  if (isCurrentlyAttending) {
    data.attendingEvents = data.attendingEvents.filter(id => id !== eventId);
  } else {
    data.attendingEvents.push(eventId);
  }
  
  saveStorageData({ attendingEvents: data.attendingEvents });
  return !isCurrentlyAttending;
}

export function getComments(eventId: string): Comment[] {
  const data = getStorageData();
  return data.comments.filter(comment => comment.eventId === eventId);
}

export function addComment(eventId: string, text: string): Comment | null {
  const user = getCurrentUser();
  if (!user) return null;
  
  const data = getStorageData();
  const newComment: Comment = {
    id: Date.now().toString(),
    eventId,
    userId: user.id,
    user,
    text,
    timestamp: new Date().toISOString(),
  };
  
  data.comments.push(newComment);
  saveStorageData({ comments: data.comments });
  return newComment;
}

export function getCustomEvents(): Event[] {
  return getStorageData().customEvents;
}

export function addCustomEvent(event: Event): void {
  const data = getStorageData();
  data.customEvents.push(event);
  saveStorageData({ customEvents: data.customEvents });
}

export function removeCustomEvent(eventId: string): void {
  const data = getStorageData();
  data.customEvents = data.customEvents.filter(event => event.id !== eventId);
  saveStorageData({ customEvents: data.customEvents });
}

export function updateCustomEvent(event: Event): void {
  const data = getStorageData();
  data.customEvents = data.customEvents.map(e => e.id === event.id ? event : e);
  saveStorageData({ customEvents: data.customEvents });
}
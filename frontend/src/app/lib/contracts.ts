export interface TokenPair {
  access_token: string;
  refresh_token?: string | null;
  token_type: string;
}

export interface UserRead {
  id: number;
  name: string;
  email: string;
  city_location: string | null;
  created_at: string;
}

export interface EventRead {
  id: number;
  region_id: number;
  user_id: number | null;
  user_name?: string;
  title: string;
  category: string;
  content: string | null;
  source_id: number | null;
  source_name: string | null;
  organizer_name: string | null;
  origin_type: string;
  external_id: string | null;
  external_url: string | null;
  canonical_url: string | null;
  event_image_url: string | null;
  event_start_at: string | null;
  event_end_at: string | null;
  timezone: string;
  venue_name: string | null;
  venue_address: string | null;
  neighborhood: string | null;
  city: string;
  price_info: string | null;
  promo_summary: string | null;
  tags_json: string | null;
  source_confidence: number | null;
  last_seen_at: string | null;
  created_at: string;
}

export interface CommentRead {
  id: number;
  user_id: number;
  event_id: number;
  user_name?: string;
  text: string;
  created_at: string;
}

export interface EventWithInteractionsRead extends EventRead {
  likes_count: number;
  comments_count: number;
  attendance_count: number;
  comments: CommentRead[];
}

export interface TrendEntryRead {
  event_id: number;
  rank: number;
  title: string;
  attendance_count: number;
  comments_count: number;
  likes_count: number;
  updated_at: string;
}

export interface EventCategoryOptionsResponse {
  options: string[];
}

export interface EventCreateBody {
  user_id: number;
  title: string;
  category: string;
  content?: string;
  event_start_at?: string;
  event_end_at?: string;
  timezone?: string;
  venue_name?: string;
  venue_address?: string;
  neighborhood?: string;
  price_info?: string;
  event_image_url?: string;
}

export interface EventUpdateBody {
  title?: string;
  category?: string;
  content?: string;
  event_start_at?: string;
  event_end_at?: string;
  timezone?: string;
  venue_name?: string;
  venue_address?: string;
  neighborhood?: string;
  price_info?: string;
  event_image_url?: string;
}

export interface SuccessResponse {
  success: boolean;
}

export interface EventImageUploadResponse {
  url: string;
}

export interface AppSession {
  accessToken: string;
  refreshToken?: string | null;
  currentUser: UserRead;
  attendingEventIds: number[];
}

export interface FeedEvent extends EventWithInteractionsRead {
  trending: boolean;
}

export interface EventFilterParams {
  category?: string;
  neighborhood?: string;
  starts_after?: string;
  starts_before?: string;
}

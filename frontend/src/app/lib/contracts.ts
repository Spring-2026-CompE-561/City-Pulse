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
  title: string;
  category: string;
  content: string | null;
  source_id: number | null;
  source_name: string | null;
  origin_type: string;
  external_id: string | null;
  external_url: string | null;
  canonical_url: string | null;
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
}

export interface SuccessResponse {
  success: boolean;
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

export interface PartnerSubmissionCreateBody {
  organizer_name: string;
  organizer_contact?: string;
  instagram_handle?: string;
  instagram_post_url?: string;
  external_event_url?: string;
  title: string;
  description?: string;
  category: string;
  neighborhood?: string;
  venue_name?: string;
  venue_address?: string;
  event_start_at?: string;
  event_end_at?: string;
}

export interface PartnerSubmissionRead {
  id: number;
  region_id: number;
  submitted_by_user_id: number | null;
  organizer_name: string;
  organizer_contact: string | null;
  instagram_handle: string | null;
  instagram_post_url: string | null;
  external_event_url: string | null;
  title: string;
  description: string | null;
  category: string;
  neighborhood: string | null;
  venue_name: string | null;
  venue_address: string | null;
  event_start_at: string | null;
  event_end_at: string | null;
  moderation_status: string;
  moderation_notes: string | null;
  published_event_id: number | null;
  created_at: string;
  reviewed_at: string | null;
}

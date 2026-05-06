export const CATEGORY_IMAGES: Record<string, string> = {
  'Environment': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&h=600&fit=crop',
  'Music': 'https://images.unsplash.com/photo-1514525253344-9914f2777e8d?w=800&h=600&fit=crop',
  'Food & Drink': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&h=600&fit=crop',
  'Arts & Culture': 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800&h=600&fit=crop',
  'Entertainment': 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&h=600&fit=crop',
  'Business': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=600&fit=crop',
  'Health & Wellness': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&h=600&fit=crop',
  'Nightlife': 'https://images.unsplash.com/photo-1566417713940-fe7c737a9ef2?w=800&h=600&fit=crop',
  'Charity & Causes': 'https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=800&h=600&fit=crop',
  'Community': 'https://images.unsplash.com/photo-1529156069898-19953cC87?w=800&h=600&fit=crop',
  'Technology': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&h=600&fit=crop',
  'Sports': 'https://images.unsplash.com/photo-1461896836934-ffe607ca82b3?w=800&h=600&fit=crop',
};

export const DEFAULT_CATEGORY_IMAGE = CATEGORY_IMAGES['Entertainment'];

export function getCategoryImage(category: string): string {
  return CATEGORY_IMAGES[category] || DEFAULT_CATEGORY_IMAGE;
}
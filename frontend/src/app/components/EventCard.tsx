import Link from 'next/link';
import type { FeedEvent } from '../lib/contracts';
import { Badge } from './ui/badge';
import { Card, CardContent, CardFooter, CardHeader } from './ui/card';
import { Calendar, ExternalLink, MapPin, TrendingUp, Users } from 'lucide-react';

interface EventCardProps {
  event: FeedEvent;
}

export function EventCard({ event }: EventCardProps) {
  const eventDate = new Date(event.event_start_at ?? event.created_at);
  const categoryImages: Record<string, string> = {
    Environment: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=200&fit=crop',
    Music: 'https://images.unsplash.com/photo-1514525253344-9914f2777e8d?w=400&h=200&fit=crop',
    Food: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=200&fit=crop',
    Arts: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=200&fit=crop',
    Sports: 'https://images.unsplash.com/photo-1461896836934-ffe607ca82b3?w=400&h=200&fit=crop',
    Technology: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=200&fit=crop',
    Community: 'https://images.unsplash.com/photo-1529156069898-19953cC87?w=400&h=200&fit=crop',
  };
  const eventImage = categoryImages[event.category] || 'https://images.unsplash.com/photo-1501281668745-f7f57925c73d?w=400&h=200&fit=crop';

  const sourceLabel = event.source_name
    ? `Imported from ${event.source_name}`
    : event.origin_type === 'user'
      ? `Posted by user #${event.user_id ?? 'unknown'}`
      : 'Imported listing';

  return (
    <Link href={`/event/${event.id}`}>
      <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
         <div className="relative h-32 overflow-hidden">
           <img src={eventImage} alt={event.title} className="w-full h-full object-cover" />
           {event.trending && (
             <Badge className="absolute top-3 right-3 bg-orange-500 text-white">
               <TrendingUp className="w-3 h-3 mr-1" />
               Trending
             </Badge>
           )}
         </div>
        
        <CardHeader>
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1">
              <h3 className="font-semibold line-clamp-2">{event.title}</h3>
              <Badge variant="secondary" className="mt-2">
                {event.category}
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="w-4 h-4" />
            <span>{eventDate.toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric',
            })}</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="w-4 h-4" />
            <span className="line-clamp-1">
              {event.neighborhood ? `${event.neighborhood}, ` : ''}{event.city}
            </span>
          </div>

          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Users className="w-4 h-4" />
            <span>
              {event.attendance_count} {event.attendance_count === 1 ? 'person' : 'people'} attending
            </span>
          </div>
          {event.external_url && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <ExternalLink className="w-4 h-4" />
              <span className="line-clamp-1">Source link available</span>
            </div>
          )}
        </CardContent>

        <CardFooter className="border-t pt-4">
          <div className="text-sm text-muted-foreground">
            {sourceLabel}
          </div>
        </CardFooter>
      </Card>
    </Link>
  );
}

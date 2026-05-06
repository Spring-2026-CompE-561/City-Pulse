import Link from 'next/link';
import type { FeedEvent } from '../lib/contracts';
import { build_media_url } from '../lib/api';
import { CATEGORY_IMAGES, DEFAULT_CATEGORY_IMAGE } from '../lib/constants';
import { Badge } from './ui/badge';
import { Card, CardContent, CardFooter, CardHeader } from './ui/card';
import { Calendar, ExternalLink, FileText, MapPin, TrendingUp, Users } from 'lucide-react';

interface EventCardProps {
  event: FeedEvent;
}

export function EventCard({ event }: EventCardProps) {
  const eventDate = new Date(event.event_start_at ?? event.created_at);
  const uploadedImage = event.event_image_url ? build_media_url(event.event_image_url) : null;
  const isPdfMedia = uploadedImage?.toLowerCase().endsWith('.pdf') ?? false;
  const eventImage = !isPdfMedia
    ? (uploadedImage ?? CATEGORY_IMAGES[event.category] ?? DEFAULT_CATEGORY_IMAGE)
    : null;

  const organizerLabel = event.origin_type === 'user'
    ? (event.user_name ?? `user #${event.user_id ?? 'unknown'}`)
    : (event.organizer_name ?? event.venue_name ?? event.user_name ?? 'Event Organizer');

  return (
    <Link href={`/event/${event.id}`}>
      <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
         <div className="relative h-32 overflow-hidden">
           {eventImage ? (
             <img src={eventImage} alt={event.title} className="w-full h-full object-cover" />
           ) : (
             <div className="w-full h-full bg-slate-100 flex items-center justify-center text-slate-700">
               <div className="flex items-center gap-2 text-sm font-medium">
                 <FileText className="w-4 h-4" />
                 PDF Flyer
               </div>
             </div>
           )}
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
            Organizer: {organizerLabel}
          </div>
        </CardFooter>
      </Card>
    </Link>
  );
}

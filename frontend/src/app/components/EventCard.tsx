import Link from 'next/link';
import type { FeedEvent } from '../lib/contracts';
import { build_media_url } from '../lib/api';
import { parse_api_datetime } from '../lib/datetime';
import { CATEGORY_IMAGES, DEFAULT_CATEGORY_IMAGE, normalizeEventCategory } from '../lib/constants';
import { getProfileOverride } from '../lib/storage';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Card, CardContent, CardFooter, CardHeader } from './ui/card';
import { Calendar, ExternalLink, FileText, MapPin, TrendingUp, Users } from 'lucide-react';

interface EventCardProps {
  event: FeedEvent;
}

export function EventCard({ event }: EventCardProps) {
  const eventDate = parse_api_datetime(event.event_start_at ?? event.created_at) ?? new Date();
  const displayCategory = normalizeEventCategory(event.category, event.venue_name);
  const uploadedImage = event.event_image_url ? build_media_url(event.event_image_url) : null;
  const isPdfMedia = uploadedImage?.toLowerCase().endsWith('.pdf') ?? false;
  const eventImage = !isPdfMedia
    ? (uploadedImage ?? CATEGORY_IMAGES[displayCategory] ?? DEFAULT_CATEGORY_IMAGE)
    : null;
  const organizerOverride = event.user_id ? getProfileOverride(event.user_id) : null;

  const organizerLabel = event.organizer_name
    ?? organizerOverride?.displayName
    ?? event.user_name
    ?? event.venue_name
    ?? `user #${event.user_id ?? 'unknown'}`;

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
                {displayCategory}
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
              {event.city}
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
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Avatar className="w-7 h-7">
              <AvatarImage src={organizerOverride?.avatarUrl || ''} alt={organizerLabel} />
              <AvatarFallback>{organizerLabel[0] ?? 'O'}</AvatarFallback>
            </Avatar>
            <span>Organizer: {organizerLabel}</span>
          </div>
        </CardFooter>
      </Card>
    </Link>
  );
}

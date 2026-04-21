import { Link } from 'react-router';
import type { FeedEvent } from '../lib/contracts';
import { Badge } from './ui/badge';
import { Card, CardContent, CardFooter, CardHeader } from './ui/card';
import { Calendar, ExternalLink, MapPin, TrendingUp, Users } from 'lucide-react';

interface EventCardProps {
  event: FeedEvent;
}

export function EventCard({ event }: EventCardProps) {
  const eventDate = new Date(event.event_start_at ?? event.created_at);
  const sourceLabel = event.source_name
    ? `Imported from ${event.source_name}`
    : event.origin_type === 'user'
      ? `Posted by user #${event.user_id ?? 'unknown'}`
      : 'Imported listing';

  return (
    <Link to={`/event/${event.id}`}>
      <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
        <div className="relative h-12 bg-gradient-to-r from-blue-50 to-orange-50">
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

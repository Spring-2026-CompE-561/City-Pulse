import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Separator } from '../components/ui/separator';
import {
  addAttending,
  addComment as addCommentRequest,
  deleteEvent,
  getEvent,
  isAuthError,
  listEventsWithInteractions,
  listTrends,
  removeAttending,
} from '../lib/api';
import type { EventWithInteractionsRead, UserRead } from '../lib/contracts';
import { clearSession, getCurrentUser, isAttending, rememberAttending } from '../lib/storage';
import { ArrowLeft, Calendar, MapPin, Users, TrendingUp, Check, MessageCircle, Send, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

export function EventDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const eventId = Number(id);
  const [user, setUser] = useState<UserRead | null>(null);
  const [attending, setAttending] = useState(false);
  const [eventData, setEventData] = useState<EventWithInteractionsRead | null>(null);
  const [trending, setTrending] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    const currentUser = getCurrentUser();
    if (!currentUser) {
      navigate('/');
      return;
    }
    setUser(currentUser);
  }, [navigate]);

  useEffect(() => {
    if (!user || !id || Number.isNaN(eventId)) {
      return;
    }
    let isMounted = true;
    const loadEvent = async () => {
      setLoadError(null);
      setLoading(true);
      try {
        const [event, interactionRows, trendRows] = await Promise.all([
          getEvent(eventId),
          listEventsWithInteractions(),
          listTrends(),
        ]);
        if (!isMounted) {
          return;
        }
        const interactionEvent = interactionRows.find((row) => row.id === eventId);
        setEventData(
          interactionEvent ?? {
            ...event,
            likes_count: 0,
            comments_count: 0,
            attendance_count: 0,
            comments: [],
          }
        );
        setTrending(trendRows.some((entry) => entry.event_id === eventId));
        setAttending(isAttending(eventId));
      } catch (error) {
        if (isAuthError(error)) {
          clearSession();
          toast.error(error.message);
          navigate('/');
          return;
        }
        const message = error instanceof Error ? error.message : 'Failed to load event';
        setLoadError(message);
        toast.error(message);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    loadEvent();
    return () => {
      isMounted = false;
    };
  }, [id, eventId, navigate, user]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 grid place-items-center">
        <p className="text-muted-foreground">Loading event details...</p>
      </div>
    );
  }

  if (!eventData || !user) {
    if (loadError) {
      return (
        <div className="min-h-screen bg-gray-50 grid place-items-center">
          <div className="text-center space-y-4">
            <p className="text-muted-foreground">{loadError}</p>
            <Button onClick={() => navigate('/feed')}>Back to Feed</Button>
          </div>
        </div>
      );
    }
    return null;
  }

  const handleToggleAttendance = async () => {
    try {
      if (attending) {
        await removeAttending(eventId);
        rememberAttending(eventId, false);
        setAttending(false);
        setEventData({
          ...eventData,
          attendance_count: Math.max(0, eventData.attendance_count - 1),
        });
        toast.info('Removed from your events');
      } else {
        await addAttending(eventId);
        rememberAttending(eventId, true);
        setAttending(true);
        setEventData({
          ...eventData,
          attendance_count: eventData.attendance_count + 1,
        });
        toast.success("You're attending this event!");
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unable to update attendance');
    }
  };

  const handleAddComment = async () => {
    if (!newComment.trim()) {
      return;
    }
    try {
      const comment = await addCommentRequest(eventId, newComment.trim());
      setEventData({
        ...eventData,
        comments: [...eventData.comments, comment],
        comments_count: eventData.comments_count + 1,
      });
      setNewComment('');
      toast.success('Comment posted!');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to post comment');
    }
  };

  const handleDeleteEvent = async () => {
    if (!window.confirm('Are you sure you want to delete this event?')) {
      return;
    }
    try {
      await deleteEvent(eventId);
      toast.success('Event deleted!');
      navigate('/feed');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to delete event');
    }
  };

  const isUserEvent = eventData.user_id === user.id;
  const createdDate = new Date(eventData.created_at);
  const startDate = eventData.event_start_at ? new Date(eventData.event_start_at) : null;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/feed')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Events
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="relative h-96 rounded-xl overflow-hidden mb-8">
          <img
            src="https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=1200&h=800&fit=crop"
            alt={eventData.title}
            className="w-full h-full object-cover"
          />
          {trending && (
            <Badge className="absolute top-4 right-4 bg-orange-500 text-white">
              <TrendingUp className="w-4 h-4 mr-1" />
              Trending
            </Badge>
          )}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            <div>
              <Badge variant="secondary" className="mb-3">
                {eventData.category}
              </Badge>
              <h1 className="text-4xl font-bold mb-4">{eventData.title}</h1>
              <p className="text-lg text-muted-foreground">
                {eventData.content ?? 'No event description provided.'}
              </p>
            </div>

            <Separator />

            <div className="grid sm:grid-cols-2 gap-4">
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  <div>
                    <div className="text-sm text-muted-foreground">Start time</div>
                    <div className="font-semibold">
                      {startDate ? startDate.toLocaleString() : createdDate.toLocaleString()}
                    </div>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 flex items-center gap-3">
                  <MapPin className="w-5 h-5 text-green-600" />
                  <div>
                    <div className="text-sm text-muted-foreground">Location</div>
                    <div className="font-semibold">
                      {eventData.venue_name ?? 'San Diego Venue'}
                      {eventData.neighborhood ? ` · ${eventData.neighborhood}` : ''}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {eventData.external_url && (
              <a
                href={eventData.external_url}
                target="_blank"
                rel="noreferrer"
                className="text-sm text-blue-600 underline"
              >
                View original source listing
              </a>
            )}

            <Separator />

            <div>
              <div className="flex items-center gap-2 mb-4">
                <MessageCircle className="w-5 h-5" />
                <h2 className="text-2xl font-bold">Discussion</h2>
              </div>

              <Card className="mb-4">
                <CardContent className="p-4 space-y-2">
                  <Textarea
                    placeholder="Share your thoughts..."
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    rows={3}
                  />
                  <div className="flex justify-end">
                    <Button onClick={handleAddComment} disabled={!newComment.trim()}>
                      <Send className="w-4 h-4 mr-2" />
                      Post Comment
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <div className="space-y-4">
                {eventData.comments.length === 0 ? (
                  <Card>
                    <CardContent className="p-8 text-center text-muted-foreground">
                      Be the first to comment and start a discussion!
                    </CardContent>
                  </Card>
                ) : (
                  eventData.comments.map((comment) => (
                    <Card key={comment.id}>
                      <CardContent className="p-4 flex gap-3">
                        <Avatar className="w-10 h-10">
                          <AvatarFallback>U{comment.user_id}</AvatarFallback>
                        </Avatar>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="font-semibold">User #{comment.user_id}</span>
                            <span className="text-sm text-muted-foreground">
                              {new Date(comment.created_at).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-muted-foreground">{comment.text}</p>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <Card className="sticky top-24">
              <CardContent className="p-6 space-y-4">
                <Button onClick={handleToggleAttendance} className="w-full" variant={attending ? 'secondary' : 'default'}>
                  {attending ? (
                    <>
                      <Check className="w-4 h-4 mr-2" />
                      You're Attending
                    </>
                  ) : (
                    'Attend Event'
                  )}
                </Button>
                <Separator />
                <div className="flex items-center gap-2">
                  <Users className="w-5 h-5 text-muted-foreground" />
                  <span className="font-semibold">
                    {eventData.attendance_count} {eventData.attendance_count === 1 ? 'person' : 'people'} attending
                  </span>
                </div>
              </CardContent>
            </Card>

            {isUserEvent && (
              <Card>
                <CardContent className="p-6">
                  <Button onClick={handleDeleteEvent} className="w-full" variant="destructive">
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Event
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
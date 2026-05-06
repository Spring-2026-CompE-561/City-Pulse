import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Avatar, AvatarFallback } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';
import { Separator } from '../components/ui/separator';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '../components/ui/dialog';
import {
  addAttending,
  addComment as addCommentRequest,
  build_media_url,
  deleteEvent,
  getEvent,
  isAuthError,
  listCategories,
  listEventsWithInteractions,
  listTrends,
  removeAttending,
  updateEvent as updateEventRequest,
} from '../lib/api';
import type { EventWithInteractionsRead, UserRead } from '../lib/contracts';
import { CATEGORY_IMAGES, DEFAULT_CATEGORY_IMAGE } from '../lib/constants';
import { clearSession, getCurrentUser, isAttending, rememberAttending } from '../lib/storage';
import { ArrowLeft, Calendar, MapPin, Users, TrendingUp, Check, MessageCircle, Send, Trash2, Pencil, Save, X } from 'lucide-react';
import { toast } from 'sonner';

function datetime_to_input_value(value: string | null): string {
  if (!value) {
    return '';
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return '';
  }
  const localDate = new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
  return localDate.toISOString().slice(0, 16);
}

export function EventDetail() {
  const router = useRouter();
  const id = typeof router.query.id === 'string' ? router.query.id : undefined;
  const eventId = Number(id);
  const [user, setUser] = useState<UserRead | null>(null);
  const [attending, setAttending] = useState(false);
  const [eventData, setEventData] = useState<EventWithInteractionsRead | null>(null);
  const [trending, setTrending] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [categoryOptions, setCategoryOptions] = useState<string[]>([
    'Technology',
    'Arts & Culture',
    'Environment',
    'Entertainment',
    'Business',
    'Food & Drink',
    'Health & Wellness',
    'Music',
  ]);
  const [editForm, setEditForm] = useState({
    title: '',
    category: '',
    content: '',
    neighborhood: '',
    venueName: '',
    venueAddress: '',
    priceInfo: '',
    eventStartDate: '',
    eventEndDate: '',
  });

  useEffect(() => {
    const currentUser = getCurrentUser();
    if (!currentUser) {
      router.push('/');
      return;
    }
    setUser(currentUser);
  }, [router]);

  useEffect(() => {
    listCategories()
      .then((response) => {
        setCategoryOptions(response.options.filter((value) => value !== 'All Categories'));
      })
      .catch(() => {
        // Keep fallback categories if request fails.
      });
  }, []);

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
          router.push('/');
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
  }, [id, eventId, router, user]);

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
            <Button onClick={() => router.push('/feed')}>Back to Feed</Button>
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
      router.push('/feed');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to delete event');
    }
  };

  const handleStartEdit = () => {
    if (!eventData) {
      return;
    }
    setEditForm({
      title: eventData.title,
      category: eventData.category,
      content: eventData.content ?? '',
      neighborhood: eventData.neighborhood ?? '',
      venueName: eventData.venue_name ?? '',
      venueAddress: eventData.venue_address ?? '',
      priceInfo: eventData.price_info ?? '',
      eventStartDate: datetime_to_input_value(eventData.event_start_at),
      eventEndDate: datetime_to_input_value(eventData.event_end_at),
    });
    setIsEditDialogOpen(true);
  };

  const handleCancelEdit = () => {
    setIsEditDialogOpen(false);
  };

  const handleEditFieldChange = (field: keyof typeof editForm, value: string) => {
    setEditForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSaveEdit = async () => {
    if (!editForm.title.trim() || !editForm.category.trim()) {
      toast.error('Please provide at least a title and category');
      return;
    }
    setIsSaving(true);
    try {
      const nextStartAt = editForm.eventStartDate
        ? new Date(editForm.eventStartDate).toISOString()
        : null;
      const nextEndAt = editForm.eventEndDate
        ? new Date(editForm.eventEndDate).toISOString()
        : null;
      await updateEventRequest(eventId, {
        title: editForm.title.trim(),
        category: editForm.category.trim(),
        content: editForm.content.trim() || undefined,
        neighborhood: editForm.neighborhood.trim() || undefined,
        venue_name: editForm.venueName.trim() || undefined,
        venue_address: editForm.venueAddress.trim() || undefined,
        price_info: editForm.priceInfo.trim() || undefined,
        event_start_at: nextStartAt ?? undefined,
        event_end_at: nextEndAt ?? undefined,
      });
      setIsEditDialogOpen(false);
      toast.success('Event updated!');
      await router.replace(router.asPath);
    } catch (error) {
      if (isAuthError(error)) {
        clearSession();
        toast.error(error.message);
        router.push('/');
        return;
      }
      toast.error(error instanceof Error ? error.message : 'Failed to update event');
    } finally {
      setIsSaving(false);
    }
  };

  const isUserEvent = eventData.user_id === user.id;
  const createdDate = new Date(eventData.created_at);
  const startDate = eventData.event_start_at ? new Date(eventData.event_start_at) : null;
  const uploadedImage = eventData.event_image_url ? build_media_url(eventData.event_image_url) : null;
  const isPdfMedia = uploadedImage?.toLowerCase().endsWith('.pdf') ?? false;
  const eventImage = !isPdfMedia
    ? (uploadedImage ?? CATEGORY_IMAGES[eventData.category] ?? DEFAULT_CATEGORY_IMAGE)
    : null;

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <Button variant="ghost" size="sm" onClick={() => router.push('/feed')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Events
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="relative h-96 rounded-xl overflow-hidden mb-8">
          {eventImage ? (
            <img
              src={eventImage}
              alt={eventData.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-slate-100 flex items-center justify-center text-slate-700">
              Flyer preview unavailable
            </div>
          )}
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
              <p className="text-sm text-muted-foreground mb-2">
                Organizer: {eventData.organizer_name ?? eventData.venue_name ?? eventData.user_name ?? 'Event Organizer'}
              </p>
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
                      {startDate ? startDate.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) : createdDate.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
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
               <Card>
                 <CardContent className="p-0 overflow-hidden h-64 bg-gray-200 flex items-center justify-center relative">
                   <div className="text-center p-4">
                     <MapPin className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                     <p className="text-sm text-muted-foreground mb-4">Map view unavailable without API key</p>
                     <Button 
                       variant="outline" 
                       size="sm" 
                       onClick={() => window.open(`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
                         (eventData.venue_name ?? 'San Diego') + (eventData.neighborhood ? `, ${eventData.neighborhood}` : '')
                       )}`, '_blank')}
                     >
                       View on Google Maps
                     </Button>
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
                            <span className="font-semibold">{comment.user_name ?? `User #${comment.user_id}`}</span>
                            <span className="text-sm text-muted-foreground">
                               {new Date(comment.created_at).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}
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
              <Card className="space-y-0">
                <CardContent className="p-6 space-y-4">
                  <Button onClick={handleStartEdit} className="w-full" variant="outline">
                    <Pencil className="w-4 h-4 mr-2" />
                    Edit Event
                  </Button>
                  <Separator />
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
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Edit Event</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-title">Title</Label>
              <Input
                id="edit-title"
                value={editForm.title}
                onChange={(e) => handleEditFieldChange('title', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-category">Category</Label>
              <Select
                value={editForm.category}
                onValueChange={(value) => handleEditFieldChange('category', value)}
              >
                <SelectTrigger id="edit-category">
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categoryOptions.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-content">Description</Label>
              <Textarea
                id="edit-content"
                rows={3}
                value={editForm.content}
                onChange={(e) => handleEditFieldChange('content', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-neighborhood">Neighborhood</Label>
              <Input
                id="edit-neighborhood"
                value={editForm.neighborhood}
                onChange={(e) => handleEditFieldChange('neighborhood', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-venue-name">Venue Name</Label>
              <Input
                id="edit-venue-name"
                value={editForm.venueName}
                onChange={(e) => handleEditFieldChange('venueName', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-venue-address">Venue Address</Label>
              <Input
                id="edit-venue-address"
                value={editForm.venueAddress}
                onChange={(e) => handleEditFieldChange('venueAddress', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-price-info">Price / Promo</Label>
              <Input
                id="edit-price-info"
                value={editForm.priceInfo}
                onChange={(e) => handleEditFieldChange('priceInfo', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-event-start-date">Start Date & Time</Label>
              <Input
                id="edit-event-start-date"
                type="datetime-local"
                value={editForm.eventStartDate}
                onChange={(e) => handleEditFieldChange('eventStartDate', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-event-end-date">End Date & Time</Label>
              <Input
                id="edit-event-end-date"
                type="datetime-local"
                value={editForm.eventEndDate}
                onChange={(e) => handleEditFieldChange('eventEndDate', e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handleSaveEdit}
                className="flex-1"
                disabled={isSaving}
              >
                <Save className="w-4 h-4 mr-2" />
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
              <Button
                onClick={handleCancelEdit}
                variant="outline"
                disabled={isSaving}
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
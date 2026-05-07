import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Separator } from '../components/ui/separator';
import { EditEventDialog } from '../components/EditEventDialog';
import { mockEvents, mockUsers } from '../lib/mockData';
import { getCurrentUser, isAttending, toggleAttendance, getComments, addComment, getCustomEvents, removeCustomEvent } from '../lib/storage';
import { ArrowLeft, Calendar, Clock, MapPin, Users, TrendingUp, Check, MessageCircle, Send, Edit, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

export function EventDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [attending, setAttending] = useState(false);
  const [comments, setComments] = useState<any[]>([]);
  const [newComment, setNewComment] = useState('');
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [eventData, setEventData] = useState<any>(null);

  // Combine custom events with mock events
  const loadEvent = () => {
    const customEvents = getCustomEvents();
    const allEvents = [...customEvents, ...mockEvents];
    const foundEvent = allEvents.find(e => e.id === id);
    setEventData(foundEvent);
  };

  useEffect(() => {
    loadEvent();
  }, [id]);

  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
    if (!currentUser) {
      navigate('/');
    }
  }, [navigate]);

  useEffect(() => {
    if (id) {
      setAttending(isAttending(id));
      setComments(getComments(id));
    }
  }, [id]);

  if (!eventData || !user) {
    return null;
  }

  const handleToggleAttendance = () => {
    if (!id) return;
    const newState = toggleAttendance(id);
    setAttending(newState);
    if (newState) {
      toast.success("You're attending this event!");
    } else {
      toast.info('Removed from your events');
    }
  };

  const handleAddComment = () => {
    if (!id || !newComment.trim()) return;
    
    const comment = addComment(id, newComment);
    if (comment) {
      setComments([...comments, comment]);
      setNewComment('');
      toast.success('Comment posted!');
    }
  };

  const attendees = mockUsers.filter(u => eventData.attendees.includes(u.id));
  const totalAttendees = eventData.attendees.length + (attending && !eventData.attendees.includes(user.id) ? 1 : 0);
  
  // Check if this is a custom event created by the current user
  const customEvents = getCustomEvents();
  const isUserEvent = customEvents.some(e => e.id === id && e.organizer.id === user.id);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate('/feed')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Events
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Event Hero Image */}
        <div className="relative h-96 rounded-xl overflow-hidden mb-8">
          <img
            src={eventData.image}
            alt={eventData.title}
            className="w-full h-full object-cover"
          />
          {eventData.trending && (
            <Badge className="absolute top-4 right-4 bg-orange-500 text-white">
              <TrendingUp className="w-4 h-4 mr-1" />
              Trending
            </Badge>
          )}
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            <div>
              <Badge variant="secondary" className="mb-3">
                {eventData.category}
              </Badge>
              <h1 className="text-4xl font-bold mb-4">{eventData.title}</h1>
              <p className="text-lg text-muted-foreground">{eventData.description}</p>
            </div>

            <Separator />

            {/* Event Details */}
            <div className="space-y-4">
              <h2 className="text-2xl font-bold">Event Details</h2>
              
              <div className="grid sm:grid-cols-2 gap-4">
                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Calendar className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Date</div>
                      <div className="font-semibold">
                        {new Date(eventData.date).toLocaleDateString('en-US', {
                          weekday: 'short',
                          month: 'long',
                          day: 'numeric',
                          year: 'numeric',
                        })}
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Clock className="w-5 h-5 text-purple-600" />
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Time</div>
                      <div className="font-semibold">{eventData.time}</div>
                    </div>
                  </CardContent>
                </Card>

                <Card className="sm:col-span-2">
                  <CardContent className="p-4 flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <MapPin className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Location</div>
                      <div className="font-semibold">{eventData.location}</div>
                      <div className="text-sm text-muted-foreground">{eventData.city}</div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            <Separator />

            {/* Organizer */}
            <div>
              <h2 className="text-2xl font-bold mb-4">Organized By</h2>
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center gap-4">
                    <Avatar className="w-16 h-16">
                      <AvatarImage src={eventData.organizer.avatar} alt={eventData.organizer.name} />
                      <AvatarFallback>{eventData.organizer.name[0]}</AvatarFallback>
                    </Avatar>
                    <div>
                      <h3 className="font-semibold text-lg">{eventData.organizer.name}</h3>
                      <p className="text-sm text-muted-foreground">{eventData.organizer.location}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <Separator />

            {/* Comments Section */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <MessageCircle className="w-5 h-5" />
                <h2 className="text-2xl font-bold">Discussion</h2>
              </div>

              {/* Add Comment */}
              <Card className="mb-4">
                <CardContent className="p-4">
                  <div className="flex gap-3">
                    <Avatar className="w-10 h-10">
                      <AvatarImage src={user.avatar} alt={user.name} />
                      <AvatarFallback>{user.name[0]}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1 space-y-2">
                      <Textarea
                        placeholder="Share your thoughts or make plans with others..."
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
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Comments List */}
              <div className="space-y-4">
                {comments.length === 0 ? (
                  <Card>
                    <CardContent className="p-8 text-center">
                      <MessageCircle className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                      <p className="text-muted-foreground">
                        Be the first to comment and start a discussion!
                      </p>
                    </CardContent>
                  </Card>
                ) : (
                  comments.map((comment) => (
                    <Card key={comment.id}>
                      <CardContent className="p-4">
                        <div className="flex gap-3">
                          <Avatar className="w-10 h-10">
                            <AvatarImage src={comment.user.avatar} alt={comment.user.name} />
                            <AvatarFallback>{comment.user.name[0]}</AvatarFallback>
                          </Avatar>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="font-semibold">{comment.user.name}</span>
                              <span className="text-sm text-muted-foreground">
                                {new Date(comment.timestamp).toLocaleString()}
                              </span>
                            </div>
                            <p className="text-muted-foreground">{comment.text}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Attendance Card */}
            <Card className="sticky top-24">
              <CardContent className="p-6 space-y-4">
                <Button
                  onClick={handleToggleAttendance}
                  className="w-full"
                  variant={attending ? 'secondary' : 'default'}
                >
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

                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <Users className="w-5 h-5 text-muted-foreground" />
                    <span className="font-semibold">
                      {totalAttendees} {totalAttendees === 1 ? 'person' : 'people'} attending
                    </span>
                  </div>

                  <div className="space-y-2">
                    {attendees.slice(0, 5).map((attendee) => (
                      <div key={attendee.id} className="flex items-center gap-2">
                        <Avatar className="w-8 h-8">
                          <AvatarImage src={attendee.avatar} alt={attendee.name} />
                          <AvatarFallback>{attendee.name[0]}</AvatarFallback>
                        </Avatar>
                        <span className="text-sm">{attendee.name}</span>
                      </div>
                    ))}
                    {attending && !eventData.attendees.includes(user.id) && (
                      <div className="flex items-center gap-2">
                        <Avatar className="w-8 h-8">
                          <AvatarImage src={user.avatar} alt={user.name} />
                          <AvatarFallback>{user.name[0]}</AvatarFallback>
                        </Avatar>
                        <span className="text-sm">{user.name} (You)</span>
                      </div>
                    )}
                    {totalAttendees > 6 && (
                      <p className="text-sm text-muted-foreground">
                        +{totalAttendees - 6} more
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Edit/Delete Event */}
            {isUserEvent && (
              <Card>
                <CardContent className="p-6 space-y-3">
                  <Button
                    onClick={() => setShowEditDialog(true)}
                    className="w-full"
                    variant="outline"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Edit Event
                  </Button>
                  <Button
                    onClick={() => {
                      if (window.confirm('Are you sure you want to delete this event?')) {
                        removeCustomEvent(id!);
                        navigate('/feed');
                        toast.success('Event deleted!');
                      }
                    }}
                    className="w-full"
                    variant="destructive"
                  >
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Event
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* Edit Event Dialog */}
      {isUserEvent && (
        <EditEventDialog
          open={showEditDialog}
          onOpenChange={setShowEditDialog}
          event={eventData}
          onSuccess={loadEvent}
        />
      )}
    </div>
  );
}
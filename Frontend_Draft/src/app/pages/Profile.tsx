import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader } from '../components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';
import { EditProfileDialog } from '../components/EditProfileDialog';
import { mockEvents } from '../lib/mockData';
import { getCurrentUser, getStorageData, getCustomEvents } from '../lib/storage';
import { ArrowLeft, Calendar, MapPin, TrendingUp, Check } from 'lucide-react';

export function Profile() {
  const navigate = useNavigate();
  const [user, setUser] = useState<any>(null);
  const [attendingEventIds, setAttendingEventIds] = useState<string[]>([]);
  const [showEditDialog, setShowEditDialog] = useState(false);

  const loadUserData = () => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
    if (!currentUser) {
      navigate('/');
      return;
    }
    const data = getStorageData();
    setAttendingEventIds(data.attendingEvents);
  };

  useEffect(() => {
    loadUserData();
  }, [navigate]);

  if (!user) return null;

  const customEvents = getCustomEvents();
  const allEvents = [...customEvents, ...mockEvents];

  const attendingEvents = allEvents.filter(event => 
    attendingEventIds.includes(event.id)
  );

  const organizedEvents = allEvents.filter(event => 
    event.organizer.id === user.id
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate('/feed')}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Feed
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Profile Header */}
        <Card className="mb-8">
          <CardContent className="p-8">
            <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
              <Avatar className="w-24 h-24">
                <AvatarImage src={user.avatar} alt={user.name} />
                <AvatarFallback className="text-2xl">{user.name[0]}</AvatarFallback>
              </Avatar>
              <div className="flex-1 text-center sm:text-left">
                <h1 className="text-3xl font-bold mb-2">{user.name}</h1>
                <p className="text-muted-foreground mb-4">{user.email}</p>
                <div className="flex items-center gap-2 justify-center sm:justify-start">
                  <MapPin className="w-4 h-4 text-muted-foreground" />
                  <span className="text-muted-foreground">{user.location}</span>
                </div>
              </div>
              <Button variant="outline" onClick={() => setShowEditDialog(true)}>
                Edit Profile
              </Button>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-8 pt-8 border-t">
              <div className="text-center">
                <div className="text-2xl font-bold" style={{ color: '#FF6B35' }}>{attendingEvents.length}</div>
                <div className="text-sm text-muted-foreground">Attending</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold" style={{ color: '#004E89' }}>{organizedEvents.length}</div>
                <div className="text-sm text-muted-foreground">Organized</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold" style={{ color: '#E63946' }}>
                  {getStorageData().comments.length}
                </div>
                <div className="text-sm text-muted-foreground">Comments</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Attending Events */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-4">
            <Check className="w-5 h-5" style={{ color: '#004E89' }} />
            <h2 className="text-2xl font-bold">Events You're Attending</h2>
            <Badge variant="secondary">{attendingEvents.length}</Badge>
          </div>

          {attendingEvents.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Calendar className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-xl font-semibold mb-2">No events yet</h3>
                <p className="text-muted-foreground mb-4">
                  Start exploring and attend events in your area
                </p>
                <Button onClick={() => navigate('/feed')}>
                  Discover Events
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid sm:grid-cols-2 gap-4">
              {attendingEvents.map((event) => (
                <Link key={event.id} to={`/event/${event.id}`}>
                  <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
                    <div className="relative h-32 overflow-hidden">
                      <img
                        src={event.image}
                        alt={event.title}
                        className="w-full h-full object-cover"
                      />
                      {event.trending && (
                        <Badge className="absolute top-2 right-2 bg-orange-500 text-white text-xs">
                          <TrendingUp className="w-3 h-3" />
                        </Badge>
                      )}
                    </div>
                    <CardHeader className="p-4">
                      <h3 className="font-semibold line-clamp-2">{event.title}</h3>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
                        <Calendar className="w-4 h-4" />
                        <span>
                          {new Date(event.date).toLocaleDateString('en-US', {
                            month: 'short',
                            day: 'numeric',
                          })}
                        </span>
                      </div>
                    </CardHeader>
                  </Card>
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Organized Events */}
        {organizedEvents.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5" style={{ color: '#E63946' }} />
              <h2 className="text-2xl font-bold">Events You Organized</h2>
              <Badge variant="secondary">{organizedEvents.length}</Badge>
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              {organizedEvents.map((event) => (
                <Link key={event.id} to={`/event/${event.id}`}>
                  <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
                    <div className="relative h-32 overflow-hidden">
                      <img
                        src={event.image}
                        alt={event.title}
                        className="w-full h-full object-cover"
                      />
                      {event.trending && (
                        <Badge className="absolute top-2 right-2 bg-orange-500 text-white text-xs">
                          <TrendingUp className="w-3 h-3" />
                        </Badge>
                      )}
                    </div>
                    <CardHeader className="p-4">
                      <h3 className="font-semibold line-clamp-2">{event.title}</h3>
                      <div className="flex items-center justify-between mt-2">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Calendar className="w-4 h-4" />
                          <span>
                            {new Date(event.date).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                            })}
                          </span>
                        </div>
                        <Badge variant="secondary" className="text-xs">
                          {event.attendees.length} attending
                        </Badge>
                      </div>
                    </CardHeader>
                  </Card>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Edit Profile Dialog */}
      <EditProfileDialog
        open={showEditDialog}
        onOpenChange={setShowEditDialog}
        onSuccess={loadUserData}
      />
    </div>
  );
}
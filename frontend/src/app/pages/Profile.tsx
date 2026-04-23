import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader } from '../components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Badge } from '../components/ui/badge';
import { getMe, isAuthError, listEventsWithInteractions } from '../lib/api';
import type { EventWithInteractionsRead, UserRead } from '../lib/contracts';
import { clearSession, getCurrentUser, getProfileOverride, getStorageData, setCurrentUser } from '../lib/storage';
import { ArrowLeft, Calendar, MapPin, TrendingUp, Check } from 'lucide-react';
import { toast } from 'sonner';

export function Profile() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserRead | null>(null);
  const [events, setEvents] = useState<EventWithInteractionsRead[]>([]);
  const [attendingEventIds, setAttendingEventIds] = useState<number[]>([]);
  const [displayName, setDisplayName] = useState('');
  const [profilePicture, setProfilePicture] = useState('');
  const [bio, setBio] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    const loadProfile = async () => {
      const currentUser = getCurrentUser();
      if (!currentUser) {
        if (isMounted) {
          setLoading(false);
        }
        navigate('/');
        return;
      }
      const cachedOverride = getProfileOverride(currentUser.id);
      const cachedUser = {
        ...currentUser,
        name: cachedOverride?.displayName || currentUser.name,
      };
      setUser(cachedUser);
      setDisplayName(cachedOverride?.displayName || cachedUser.name);
      setProfilePicture(cachedOverride?.avatarUrl || '');
      setBio(cachedOverride?.bio || '');
      const data = getStorageData();
      setAttendingEventIds(data?.attendingEventIds ?? []);
      try {
        const [me, interactions] = await Promise.all([getMe(), listEventsWithInteractions()]);
        if (!isMounted) {
          return;
        }
        const latestOverride = getProfileOverride(me.id);
        const mergedUser = {
          ...me,
          name: latestOverride?.displayName || me.name,
        };
        setCurrentUser(mergedUser);
        setUser(mergedUser);
        setDisplayName(latestOverride?.displayName || mergedUser.name);
        setProfilePicture(latestOverride?.avatarUrl || '');
        setBio(latestOverride?.bio || '');
        setEvents(interactions);
      } catch (error) {
        if (isAuthError(error)) {
          clearSession();
          toast.error(error.message);
          navigate('/');
          return;
        }
        // Keep locally cached user/session values if non-auth refresh fails.
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    loadProfile();
    return () => {
      isMounted = false;
    };
  }, [navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 grid place-items-center">
        <p className="text-muted-foreground">Loading your profile...</p>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const attendingEvents = events.filter((event) => attendingEventIds.includes(event.id));
  const organizedEvents = events.filter((event) => event.user_id === user.id);
  const commentsCount = events.reduce((acc, event) => acc + event.comments_count, 0);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/feed')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Feed
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="mb-8">
          <CardContent className="p-8">
            <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
              <Avatar className="w-24 h-24">
                <AvatarImage src={profilePicture} alt={displayName || user.name} />
                <AvatarFallback className="text-2xl">{(displayName || user.name)[0]}</AvatarFallback>
              </Avatar>
              <div className="flex-1 text-center sm:text-left">
                <h1 className="text-3xl font-bold mb-2">{displayName || user.name}</h1>
                <div className="flex items-center gap-2 justify-center sm:justify-start">
                  <MapPin className="w-4 h-4 text-muted-foreground" />
                  <span className="text-muted-foreground">{user.city_location ?? 'san diego'}</span>
                </div>
                {bio.trim() && (
                  <p className="text-muted-foreground mt-4 max-w-2xl">{bio}</p>
                )}
              </div>
              <Button variant="outline" onClick={() => navigate('/profile/settings')}>
                Profile Settings
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
                <div className="text-2xl font-bold" style={{ color: '#E63946' }}>{commentsCount}</div>
                <div className="text-sm text-muted-foreground">Comments</div>
              </div>
            </div>
          </CardContent>
        </Card>

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
                <p className="text-muted-foreground mb-4">Start exploring and attend events in your area</p>
                <Button onClick={() => navigate('/feed')}>Discover Events</Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid sm:grid-cols-2 gap-4">
              {attendingEvents.map((event) => (
                <Link key={event.id} to={`/event/${event.id}`}>
                  <Card className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer">
                    <div className="relative h-32 overflow-hidden">
                      <img
                        src="https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&h=600&fit=crop"
                        alt={event.title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <CardHeader className="p-4">
                      <h3 className="font-semibold line-clamp-2">{event.title}</h3>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
                        <Calendar className="w-4 h-4" />
                        <span>
                          {new Date(event.created_at).toLocaleDateString('en-US', {
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
                        src="https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&h=600&fit=crop"
                        alt={event.title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <CardHeader className="p-4">
                      <h3 className="font-semibold line-clamp-2">{event.title}</h3>
                      <div className="flex items-center justify-between mt-2">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Calendar className="w-4 h-4" />
                          <span>
                            {new Date(event.created_at).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                            })}
                          </span>
                        </div>
                        <Badge variant="secondary" className="text-xs">
                          {event.attendance_count} attending
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
    </div>
  );
}
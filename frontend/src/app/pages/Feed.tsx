import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router';
import { EventCard } from '../components/EventCard';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { getMe, listCategories, listEventsWithInteractions, listTrends } from '../lib/api';
import type { FeedEvent, UserRead } from '../lib/contracts';
import { clearSession, getCurrentUser, setCurrentUser } from '../lib/storage';
import { Search, TrendingUp, LogOut, Filter, Plus } from 'lucide-react';
import { toast } from 'sonner';
import logoImage from '../../imports/CityPulse_Logo.png';

export function Feed() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserRead | null>(null);
  const [events, setEvents] = useState<FeedEvent[]>([]);
  const [categories, setCategories] = useState<string[]>(['All Categories']);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCity, setSelectedCity] = useState('San Diego, CA');
  const [selectedCategory, setSelectedCategory] = useState('All Categories');
  const [selectedNeighborhood, setSelectedNeighborhood] = useState('All Neighborhoods');
  const [startDate, setStartDate] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [loading, setLoading] = useState(true);
  const [refreshToken, setRefreshToken] = useState(0);

  const neighborhoods = [
    'All Neighborhoods',
    'Hillcrest',
    'North Park',
    'Gaslamp',
    'Pacific Beach',
    'Little Italy',
    'Ocean Beach',
    'Mission Beach',
  ];

  useEffect(() => {
    let isMounted = true;
    const bootstrap = async () => {
      const sessionUser = getCurrentUser();
      if (!sessionUser) {
        navigate('/');
        return;
      }
      setUser(sessionUser);
      try {
        const [me, eventRows, trendRows, categoryRows] = await Promise.all([
          getMe(),
          listEventsWithInteractions({
            category: selectedCategory,
            neighborhood:
              selectedNeighborhood === 'All Neighborhoods' ? undefined : selectedNeighborhood,
            starts_after: startDate ? new Date(startDate).toISOString() : undefined,
          }),
          listTrends(),
          listCategories(),
        ]);
        if (!isMounted) {
          return;
        }
        setCurrentUser(me);
        setUser(me);
        const trendingIds = new Set(trendRows.map((item) => item.event_id));
        setEvents(
          eventRows.map((event) => ({
            ...event,
            trending: trendingIds.has(event.id),
          }))
        );
        setCategories(categoryRows.options);
      } catch (error) {
        clearSession();
        toast.error(error instanceof Error ? error.message : 'Session expired');
        navigate('/');
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };
    bootstrap();
    return () => {
      isMounted = false;
    };
  }, [navigate, refreshToken, selectedCategory, selectedNeighborhood, startDate]);

  const handleLogout = () => {
    clearSession();
    toast.success('Logged out successfully');
    navigate('/');
  };

  const filteredEvents = events.filter((event) => {
    const matchesSearch = event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (event.content ?? '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCity = selectedCity === 'San Diego, CA' || event.city === selectedCity;
    return matchesSearch && matchesCity;
  });

  const trendingEvents = filteredEvents.filter((event) => event.trending);

  if (!user || loading) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link to="/feed" className="flex items-center gap-3">
              <img src={logoImage} alt="CityPulse Logo" className="w-8 h-8" />
              <span className="text-2xl font-bold" style={{ 
                background: 'linear-gradient(135deg, #FF6B35 0%, #004E89 50%, #E63946 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                CityPulse
              </span>
            </Link>

            <div className="flex items-center gap-4">
              <Link to="/profile">
                <Button variant="ghost" size="sm" className="gap-2">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src="" alt={user.name} />
                    <AvatarFallback>{user.name[0]}</AvatarFallback>
                  </Avatar>
                  <span className="hidden sm:inline">{user.name}</span>
                </Button>
              </Link>
              <Button variant="ghost" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome back, {user.name}!
            </h1>
            <p className="text-muted-foreground">
              Discover events happening in {user.city_location ?? 'san diego'}
            </p>
          </div>
          <Button onClick={() => navigate('/create')} className="gap-2">
            <Plus className="w-4 h-4" />
            <span className="hidden sm:inline">Create Event</span>
          </Button>
          <Button variant="outline" onClick={() => navigate('/submit-partner-event')}>
            Submit Public Event
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-lg p-6 mb-8 shadow-sm border">
          <div className="flex flex-col gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-5 h-5" />
              <Input
                placeholder="Search events..."
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
                className="gap-2"
              >
                <Filter className="w-4 h-4" />
                Filters
              </Button>
              {(selectedCategory !== 'All Categories' || selectedNeighborhood !== 'All Neighborhoods' || startDate) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSelectedCategory('All Categories');
                    setSelectedNeighborhood('All Neighborhoods');
                    setStartDate('');
                    setRefreshToken((value) => value + 1);
                  }}
                >
                  Clear Filters
                </Button>
              )}
            </div>

            {showFilters && (
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t">
                <div className="space-y-2">
                  <label className="text-sm font-medium">City</label>
                  <Select value={selectedCity} disabled>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="San Diego, CA">San Diego, CA</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Category</label>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Neighborhood</label>
                  <Select value={selectedNeighborhood} onValueChange={setSelectedNeighborhood}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {neighborhoods.map((neighborhood) => (
                        <SelectItem key={neighborhood} value={neighborhood}>
                          {neighborhood}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Start Date</label>
                  <Input
                    type="date"
                    value={startDate}
                    onChange={(event) => setStartDate(event.target.value)}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Trending Section */}
        {trendingEvents.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-5 h-5 text-orange-500" />
              <h2 className="text-2xl font-bold">Trending Now</h2>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {trendingEvents.slice(0, 3).map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>
          </div>
        )}

        {/* All Events */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold">
              {selectedCategory !== 'All Categories' ? 'Filtered Events' : 'All Events'}
            </h2>
            <Badge variant="secondary">
              {filteredEvents.length} {filteredEvents.length === 1 ? 'Event' : 'Events'}
            </Badge>
          </div>

          {filteredEvents.length === 0 ? (
            <div className="bg-white rounded-lg p-12 text-center shadow-sm border">
              <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No events found</h3>
              <p className="text-muted-foreground mb-4">
                Try adjusting your search or filters
              </p>
              <Button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('All Categories');
                }}
              >
                Clear All Filters
              </Button>
            </div>
          ) : (
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredEvents.map((event) => (
                <EventCard key={event.id} event={event} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { EventCard } from '../components/EventCard';
import { ThemeToggle } from '../components/ThemeToggle';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { getMe, isAuthError, listCategories, listEventsWithInteractions, listTrends } from '../lib/api';
import type { FeedEvent, UserRead } from '../lib/contracts';
import { clearSession, getCurrentUser, getProfileOverride, setCurrentUser } from '../lib/storage';
import { Search, TrendingUp, LogOut, Filter, Plus } from 'lucide-react';
import { toast } from 'sonner';
import logoImage from '../../imports/CityPulse_Logo.png';

const EVENTS_PER_PAGE = 9;

export function Feed() {
  const router = useRouter();
  const [user, setUser] = useState<UserRead | null>(null);
  const [events, setEvents] = useState<FeedEvent[]>([]);
  const [categories, setCategories] = useState<string[]>(["All Categories"]);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCity, setSelectedCity] = useState("San Diego, CA");
  const [selectedCategory, setSelectedCategory] = useState("All Categories");
  const [selectedNeighborhood, setSelectedNeighborhood] =
    useState("All Neighborhoods");
  const [startDate, setStartDate] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  function startsAfterIsoFromDateInput(value: string): string | undefined {
    if (!value.trim()) {
      return undefined;
    }
    const parsed = new Date(`${value}T12:00:00`);
    if (Number.isNaN(parsed.getTime())) {
      return undefined;
    }
    return parsed.toISOString();
  }

  const neighborhoods = [
    "All Neighborhoods",
    "Hillcrest",
    "North Park",
    "Gaslamp",
    "Pacific Beach",
    "Little Italy",
    "Ocean Beach",
    "Mission Beach",
  ];

  useEffect(() => {
    let isMounted = true;
    const bootstrap = async () => {
      const sessionUser = getCurrentUser();
      if (!sessionUser) {
        if (isMounted) {
          setLoading(false);
        }
        router.push("/");
        return;
      }
      setUser(sessionUser);
      setLoadError(null);
      try {
        const [me, eventRows, trendRows, categoryRows] = await Promise.all([
          getMe(),
          listEventsWithInteractions({
            category: selectedCategory,
            neighborhood:
              selectedNeighborhood === "All Neighborhoods"
                ? undefined
                : selectedNeighborhood,
            starts_after: startsAfterIsoFromDateInput(startDate),
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
          })),
        );
        setCategories(categoryRows.options);
      } catch (error) {
        if (isAuthError(error)) {
          clearSession();
          toast.error(error.message);
          router.push("/");
          return;
        }
        const message =
          error instanceof Error ? error.message : "Failed to load your feed";
        setLoadError(message);
        toast.error(message);
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
  }, [router, refreshToken, selectedCategory, startDate]);

  const handleLogout = () => {
    clearSession();
    toast.success("Logged out successfully");
    router.push("/");
  };

  const filteredEvents = events.filter((event) => {
    const matchesSearch =
      event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (event.content ?? "").toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCity =
      selectedCity === "San Diego, CA" || event.city === selectedCity;
    return matchesSearch && matchesCity;
  });
  const totalPages = Math.max(1, Math.ceil(filteredEvents.length / EVENTS_PER_PAGE));
  const pageStartIndex = (currentPage - 1) * EVENTS_PER_PAGE;
  const paginatedEvents = filteredEvents.slice(pageStartIndex, pageStartIndex + EVENTS_PER_PAGE);
  const startPage = Math.max(1, currentPage - 2);
  const endPage = Math.min(totalPages, startPage + 4);
  const visiblePageNumbers: number[] = [];
  for (let pageNumber = Math.max(1, endPage - 4); pageNumber <= endPage; pageNumber += 1) {
    visiblePageNumbers.push(pageNumber);
  }

  const trendingEvents = filteredEvents.filter((event) => event.trending);
  const profileOverride = user ? getProfileOverride(user.id) : null;
  const displayName = profileOverride?.displayName || user?.name || 'User';
  const profileImage = profileOverride?.avatarUrl || '';

  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, selectedCategory, startDate]);

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background grid place-items-center">
        <p className="text-muted-foreground">Loading your feed...</p>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  if (loadError) {
    return (
      <div className="min-h-screen bg-background grid place-items-center">
        <div className="text-center space-y-4">
          <p className="text-muted-foreground">{loadError}</p>
          <Button onClick={() => setRefreshToken((value) => value + 1)}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-background/95 backdrop-blur border-b border-border sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/feed" className="flex items-center gap-3">
              <img
                src={logoImage.src}
                alt="CityPulse Logo"
                className="w-8 h-8"
              />
              <span
                className="text-2xl font-bold"
                style={{
                  background:
                    "linear-gradient(135deg, #FF6B35 0%, #004E89 50%, #E63946 100%)",
                  WebkitBackgroundClip: "text",
                  WebkitTextFillColor: "transparent",
                  backgroundClip: "text",
                }}
              >
                CityPulse
              </span>
            </Link>

            <div className="flex items-center gap-2 sm:gap-4">
              <ThemeToggle />
              <Link href="/profile">
                <Button variant="ghost" size="sm" className="gap-2">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src={profileImage} alt={displayName} />
                    <AvatarFallback>{displayName[0]}</AvatarFallback>
                  </Avatar>
                  <span className="hidden sm:inline">{displayName}</span>
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
        <div className="mb-8 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              Welcome back, {displayName}!
            </h1>
            <p className="text-muted-foreground">
              Discover events happening in{" "}
              {(user.city_location ?? "San Diego").replace(/\b\w/g, (l) =>
                l.toUpperCase(),
              )}
            </p>
          </div>
          <Button onClick={() => router.push("/create")} className="gap-2">
            <Plus className="w-4 h-4" />
            <span className="sm:inline">Create Event</span>
          </Button>
        </div>

        {/* Search and Filters */}
        <div className="bg-card rounded-lg p-6 mb-8 shadow-sm border border-border">
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
              {(selectedCategory !== "All Categories" ||
                selectedNeighborhood !== "All Neighborhoods" ||
                startDate) && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSelectedCategory('All Categories');
                    setStartDate('');
                    setCurrentPage(1);
                    setRefreshToken((value) => value + 1);
                  }}
                >
                  Clear Filters
                </Button>
              )}
            </div>

            {showFilters && (
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 pt-4 border-t">
                <div className="space-y-2">
                  <label className="text-sm font-medium">City</label>
                  <Select value={selectedCity} disabled>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="San Diego, CA">
                        San Diego, CA
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <label className="text-sm font-medium">Category</label>
                  <Select
                    value={selectedCategory}
                    onValueChange={setSelectedCategory}
                  >
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
                  <Select
                    value={selectedNeighborhood}
                    onValueChange={setSelectedNeighborhood}
                  >
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
                    className="event-date-filter-input"
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
              {selectedCategory !== "All Categories"
                ? "Filtered Events"
                : "All Events"}
            </h2>
            <Badge variant="secondary">
              {filteredEvents.length}{" "}
              {filteredEvents.length === 1 ? "Event" : "Events"}
            </Badge>
          </div>

          {filteredEvents.length === 0 ? (
            <div className="bg-card rounded-lg p-12 text-center shadow-sm border border-border">
              <Search className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-xl font-semibold mb-2">No events found</h3>
              <p className="text-muted-foreground mb-4">
                Try adjusting your search or filters
              </p>
              <Button
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('All Categories');
                  setCurrentPage(1);
                }}
              >
                Clear All Filters
              </Button>
            </div>
          ) : (
            <>
              <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {paginatedEvents.map((event) => (
                  <EventCard key={event.id} event={event} />
                ))}
              </div>
              {filteredEvents.length > EVENTS_PER_PAGE && (
                <div className="mt-8 flex flex-wrap items-center justify-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                  >
                    Previous
                  </Button>
                  {visiblePageNumbers.map((pageNumber) => (
                    <Button
                      key={pageNumber}
                      variant={pageNumber === currentPage ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setCurrentPage(pageNumber)}
                    >
                      {pageNumber}
                    </Button>
                  ))}
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={currentPage === totalPages}
                    onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
                  >
                    Next
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { createEvent, isAuthError, listCategories } from '../lib/api';
import type { UserRead } from '../lib/contracts';
import { clearSession, getCurrentUser } from '../lib/storage';
import { ArrowLeft, Calendar, Plus } from 'lucide-react';
import { toast } from 'sonner';

export function CreateEvent() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserRead | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
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
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
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
      setAuthChecked(true);
      navigate('/');
      return;
    }
    setUser(currentUser);
    setAuthChecked(true);
  }, [navigate]);

  useEffect(() => {
    listCategories()
      .then((response) => {
        setCategoryOptions(response.options.filter((value) => value !== 'All Categories'));
      })
      .catch(() => {
        // Keep fallback categories if request fails.
      });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.description || !formData.category) {
      toast.error('Please fill in all required fields');
      return;
    }
    try {
      if (!user) {
        toast.error('Please sign in to create an event');
        navigate('/');
        return;
      }
      await createEvent({
        user_id: user.id,
        title: formData.title,
        category: formData.category,
        content: formData.description,
        neighborhood: formData.neighborhood || undefined,
        venue_name: formData.venueName || undefined,
        venue_address: formData.venueAddress || undefined,
        price_info: formData.priceInfo || undefined,
        event_start_at: formData.eventStartDate
          ? new Date(formData.eventStartDate).toISOString()
          : undefined,
        event_end_at: formData.eventEndDate
          ? new Date(formData.eventEndDate).toISOString()
          : undefined,
      });
      toast.success('Event created successfully!');
      navigate('/feed');
    } catch (error) {
      if (isAuthError(error)) {
        clearSession();
        toast.error(error.message);
        navigate('/');
        return;
      }
      toast.error(error instanceof Error ? error.message : 'Failed to create event');
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (!authChecked) {
    return (
      <div className="min-h-screen bg-gray-50 grid place-items-center">
        <p className="text-muted-foreground">Checking your session...</p>
      </div>
    );
  }

  if (!user) {
    return null;
  }

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

      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Plus className="w-6 h-6 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold">Create New Event</h1>
          </div>
          <p className="text-muted-foreground">
            Share an event with your community and bring people together
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Event Details</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Event Title */}
              <div className="space-y-2">
                <Label htmlFor="title">Event Title *</Label>
                <Input
                  id="title"
                  placeholder="e.g., Tech Meetup, Art Exhibition, Music Festival"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  required
                />
              </div>

              {/* Description */}
              <div className="space-y-2">
                <Label htmlFor="description">Description *</Label>
                <Textarea
                  id="description"
                  placeholder="Describe your event, what attendees can expect, and any important details..."
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  rows={5}
                  required
                />
              </div>

              {/* Category */}
              <div className="space-y-2">
                <Label htmlFor="category">Category *</Label>
                <Select value={formData.category} onValueChange={(value) => handleChange('category', value)}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select a category" />
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

              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="neighborhood">Neighborhood</Label>
                  <Input
                    id="neighborhood"
                    placeholder="e.g., North Park"
                    value={formData.neighborhood}
                    onChange={(e) => handleChange('neighborhood', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="venueName">Venue</Label>
                  <Input
                    id="venueName"
                    placeholder="Venue name"
                    value={formData.venueName}
                    onChange={(e) => handleChange('venueName', e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="venueAddress">Venue Address</Label>
                <Input
                  id="venueAddress"
                  placeholder="Street address"
                  value={formData.venueAddress}
                  onChange={(e) => handleChange('venueAddress', e.target.value)}
                />
              </div>

              <div className="grid sm:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="eventStartDate">Start Date & Time</Label>
                  <Input
                    id="eventStartDate"
                    type="datetime-local"
                    value={formData.eventStartDate}
                    onChange={(e) => handleChange('eventStartDate', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="eventEndDate">End Date & Time</Label>
                  <Input
                    id="eventEndDate"
                    type="datetime-local"
                    value={formData.eventEndDate}
                    onChange={(e) => handleChange('eventEndDate', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="priceInfo">Price / Promo</Label>
                  <Input
                    id="priceInfo"
                    placeholder="$10 cover / 2-for-1"
                    value={formData.priceInfo}
                    onChange={(e) => handleChange('priceInfo', e.target.value)}
                  />
                </div>
              </div>

              <p className="text-sm text-muted-foreground">
                Include date, venue, and promo details to improve event discovery quality.
              </p>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4">
                <Button type="submit" className="flex-1">
                  <Calendar className="w-4 h-4 mr-2" />
                  Create Event
                </Button>
                <Button 
                  type="button" 
                  variant="outline" 
                  onClick={() => navigate('/feed')}
                >
                  Cancel
                </Button>
              </div>

              <p className="text-xs text-muted-foreground text-center">
                * Required fields
              </p>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
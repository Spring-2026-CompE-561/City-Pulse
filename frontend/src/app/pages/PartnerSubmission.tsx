import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { ArrowLeft, Send } from 'lucide-react';

import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Textarea } from '../components/ui/textarea';
import { isAuthError, submitPartnerEvent } from '../lib/api';
import type { UserRead } from '../lib/contracts';
import { clearSession, getCurrentUser } from '../lib/storage';
import { toast } from 'sonner';

export function PartnerSubmission() {
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState<UserRead | null>(null);
  const [authChecked, setAuthChecked] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    organizer_name: '',
    organizer_contact: '',
    instagram_handle: '',
    instagram_post_url: '',
    external_event_url: '',
    title: '',
    description: '',
    category: 'Community',
    neighborhood: '',
    venue_name: '',
    venue_address: '',
    event_start_at: '',
    event_end_at: '',
  });

  useEffect(() => {
    const sessionUser = getCurrentUser();
    if (!sessionUser) {
      setAuthChecked(true);
      navigate('/');
      return;
    }
    setCurrentUser(sessionUser);
    setAuthChecked(true);
  }, [navigate]);

  const handleChange = (field: string, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!formData.organizer_name || !formData.title) {
      toast.error('Organizer and title are required.');
      return;
    }
    setSubmitting(true);
    try {
      if (!currentUser) {
        toast.error('Please sign in to submit an event');
        navigate('/');
        return;
      }
      await submitPartnerEvent({
        ...formData,
        organizer_contact: formData.organizer_contact || undefined,
        instagram_handle: formData.instagram_handle || undefined,
        instagram_post_url: formData.instagram_post_url || undefined,
        external_event_url: formData.external_event_url || undefined,
        description: formData.description || undefined,
        neighborhood: formData.neighborhood || undefined,
        venue_name: formData.venue_name || undefined,
        venue_address: formData.venue_address || undefined,
        event_start_at: formData.event_start_at
          ? new Date(formData.event_start_at).toISOString()
          : undefined,
        event_end_at: formData.event_end_at
          ? new Date(formData.event_end_at).toISOString()
          : undefined,
      });
      toast.success('Submission received and queued for moderation.');
      navigate('/feed');
    } catch (error) {
      if (isAuthError(error)) {
        clearSession();
        toast.error(error.message);
        navigate('/');
        return;
      }
      toast.error(error instanceof Error ? error.message : 'Failed to submit event');
    } finally {
      setSubmitting(false);
    }
  };

  if (!authChecked) {
    return (
      <div className="min-h-screen bg-gray-50 grid place-items-center">
        <p className="text-muted-foreground">Checking your session...</p>
      </div>
    );
  }

  if (!currentUser) {
    return null;
  }

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

      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <Card>
          <CardHeader>
            <CardTitle>Submit Instagram / Public Event</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="organizer_name">Organizer *</Label>
                  <Input
                    id="organizer_name"
                    value={formData.organizer_name}
                    onChange={(e) => handleChange('organizer_name', e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="organizer_contact">Contact</Label>
                  <Input
                    id="organizer_contact"
                    value={formData.organizer_contact}
                    onChange={(e) => handleChange('organizer_contact', e.target.value)}
                  />
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="instagram_handle">Instagram Handle</Label>
                  <Input
                    id="instagram_handle"
                    value={formData.instagram_handle}
                    onChange={(e) => handleChange('instagram_handle', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="instagram_post_url">Instagram Post URL</Label>
                  <Input
                    id="instagram_post_url"
                    value={formData.instagram_post_url}
                    onChange={(e) => handleChange('instagram_post_url', e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="external_event_url">External Event URL</Label>
                <Input
                  id="external_event_url"
                  value={formData.external_event_url}
                  onChange={(e) => handleChange('external_event_url', e.target.value)}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="title">Event Title *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => handleChange('title', e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => handleChange('description', e.target.value)}
                  rows={4}
                />
              </div>

              <div className="grid sm:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select value={formData.category} onValueChange={(value) => handleChange('category', value)}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Community">Community</SelectItem>
                      <SelectItem value="Charity & Causes">Charity & Causes</SelectItem>
                      <SelectItem value="Arts & Culture">Arts & Culture</SelectItem>
                      <SelectItem value="Music">Music</SelectItem>
                      <SelectItem value="Nightlife">Nightlife</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="neighborhood">Neighborhood</Label>
                  <Input
                    id="neighborhood"
                    value={formData.neighborhood}
                    onChange={(e) => handleChange('neighborhood', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="venue_name">Venue</Label>
                  <Input
                    id="venue_name"
                    value={formData.venue_name}
                    onChange={(e) => handleChange('venue_name', e.target.value)}
                  />
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="event_start_at">Start Date & Time</Label>
                  <Input
                    id="event_start_at"
                    type="datetime-local"
                    value={formData.event_start_at}
                    onChange={(e) => handleChange('event_start_at', e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="event_end_at">End Date & Time</Label>
                  <Input
                    id="event_end_at"
                    type="datetime-local"
                    value={formData.event_end_at}
                    onChange={(e) => handleChange('event_end_at', e.target.value)}
                  />
                </div>
              </div>

              <Button type="submit" className="w-full" disabled={submitting}>
                <Send className="w-4 h-4 mr-2" />
                {submitting ? 'Submitting...' : 'Submit for Review'}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

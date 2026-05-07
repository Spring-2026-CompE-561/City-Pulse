import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { getCurrentUser, addCustomEvent } from '../lib/storage';
import { categories, cities } from '../lib/mockData';
import { Event } from '../lib/mockData';
import { ArrowLeft, Calendar, Plus, Upload, X } from 'lucide-react';
import { toast } from 'sonner';

export function CreateEvent() {
  const navigate = useNavigate();
  const user = getCurrentUser();
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    location: '',
    city: '',
    date: '',
    time: '',
    image: '',
  });

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>('');

  if (!user) {
    navigate('/');
    return null;
  }

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file');
      return;
    }

    // Check file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image size should be less than 5MB');
      return;
    }

    setImageFile(file);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      const result = reader.result as string;
      setImagePreview(result);
      setFormData(prev => ({ ...prev, image: result }));
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    setImageFile(null);
    setImagePreview('');
    setFormData(prev => ({ ...prev, image: '' }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.title || !formData.description || !formData.category || 
        !formData.location || !formData.city || !formData.date || !formData.time) {
      toast.error('Please fill in all required fields');
      return;
    }

    // Create new event and save to localStorage
    const newEvent: Event = {
      id: Date.now().toString(),
      title: formData.title,
      description: formData.description,
      category: formData.category,
      location: formData.location,
      city: formData.city,
      date: formData.date,
      time: formData.time,
      image: formData.image || 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&h=600&fit=crop',
      organizer: user,
      attendees: [],
      trending: false,
    };
    addCustomEvent(newEvent);
    toast.success('Event created successfully!');
    
    // Redirect to feed
    setTimeout(() => {
      navigate('/feed');
    }, 1000);
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

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
                    {categories.filter(c => c !== 'All Categories').map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Location and City */}
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="location">Venue/Location *</Label>
                  <Input
                    id="location"
                    placeholder="e.g., Central Park, City Hall"
                    value={formData.location}
                    onChange={(e) => handleChange('location', e.target.value)}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="city">City *</Label>
                  <Select value={formData.city} onValueChange={(value) => handleChange('city', value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a city" />
                    </SelectTrigger>
                    <SelectContent>
                      {cities.filter(c => c !== 'All Cities').map((city) => (
                        <SelectItem key={city} value={city}>
                          {city}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Date and Time */}
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="date">Date *</Label>
                  <Input
                    id="date"
                    type="date"
                    value={formData.date}
                    onChange={(e) => handleChange('date', e.target.value)}
                    min={new Date().toISOString().split('T')[0]}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="time">Time *</Label>
                  <Input
                    id="time"
                    type="text"
                    placeholder="e.g., 7:00 PM - 10:00 PM"
                    value={formData.time}
                    onChange={(e) => handleChange('time', e.target.value)}
                    required
                  />
                </div>
              </div>

              {/* Event Image Upload (Optional) */}
              <div className="space-y-2">
                <Label htmlFor="image">Event Image Upload (Optional)</Label>
                <div className="flex items-center gap-2">
                  <Input
                    id="image"
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                  />
                  {imageFile && (
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={handleRemoveImage}
                    >
                      <X className="w-4 h-4" />
                      Remove
                    </Button>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  Upload an image that represents your event
                </p>
              </div>

              {/* Preview */}
              {imagePreview && (
                <div className="space-y-2">
                  <Label>Image Preview</Label>
                  <div className="relative h-48 rounded-lg overflow-hidden border">
                    <img
                      src={imagePreview}
                      alt="Event preview"
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        e.currentTarget.style.display = 'none';
                      }}
                    />
                  </div>
                </div>
              )}

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
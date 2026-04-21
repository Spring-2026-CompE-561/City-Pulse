import { useState, forwardRef } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from './ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { getCurrentUser, setCurrentUser } from '../lib/storage';
import { cities } from '../lib/mockData';
import { toast } from 'sonner';

interface EditProfileDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const EditProfileDialog = forwardRef<HTMLDivElement, EditProfileDialogProps>(
  ({ open, onOpenChange, onSuccess }, ref) => {
    const user = getCurrentUser();
    const [formData, setFormData] = useState({
      name: user?.name || '',
      city_location: user?.city_location || '',
    });

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();

      if (!user) return;

      if (!formData.name.trim()) {
        toast.error('Display name cannot be empty');
        return;
      }

      if (!formData.city_location) {
        toast.error('Please select a location');
        return;
      }

      // Update user
      const updatedUser = {
        ...user,
        name: formData.name,
        city_location: formData.city_location,
      };

      setCurrentUser(updatedUser);
      toast.success('Profile updated successfully!');
      onOpenChange(false);
      onSuccess();
    };

    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent ref={ref}>
          <DialogHeader>
            <DialogTitle>Edit Profile</DialogTitle>
            <DialogDescription>
              Update your display name and location. Email and username cannot be changed.
            </DialogDescription>
          </DialogHeader>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Display Name */}
            <div className="space-y-2">
              <Label htmlFor="name">Display Name</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                required
              />
            </div>

            {/* Location */}
            <div className="space-y-2">
              <Label htmlFor="location">Location</Label>
              <Select
                value={formData.city_location}
                onValueChange={(value) => setFormData({ ...formData, city_location: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select your location" />
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

            {/* Read-only fields */}
            <div className="space-y-2">
              <Label htmlFor="email">Email (Read-only)</Label>
              <Input
                id="email"
                value={user?.email || ''}
                disabled
                className="bg-gray-100 cursor-not-allowed"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4 pt-4">
              <Button type="submit" className="flex-1">
                Save Changes
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
              >
                Cancel
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    );
  }
);

EditProfileDialog.displayName = 'EditProfileDialog';

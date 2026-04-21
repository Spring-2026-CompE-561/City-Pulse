import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { ArrowLeft } from 'lucide-react';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { getMe } from '../lib/api';
import type { UserRead } from '../lib/contracts';
import { getCurrentUser, getProfileOverride, setCurrentUser, setProfileOverride } from '../lib/storage';

const MAX_BIO_WORDS = 100;

function word_count(value: string): number {
  const normalized = value.trim();
  if (!normalized) {
    return 0;
  }
  return normalized.split(/\s+/).length;
}

function trim_to_max_words(value: string, maxWords: number): string {
  const words = value.trim().split(/\s+/);
  if (words.length <= maxWords) {
    return value;
  }
  return words.slice(0, maxWords).join(' ');
}

export function ProfileSettings() {
  const navigate = useNavigate();
  const [user, setUser] = useState<UserRead | null>(null);
  const [displayName, setDisplayName] = useState('');
  const [profilePicture, setProfilePicture] = useState('');
  const [bio, setBio] = useState('');

  useEffect(() => {
    let isMounted = true;

    const loadProfileSettings = async () => {
      const currentUser = getCurrentUser();
      if (!currentUser) {
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

      try {
        const me = await getMe();
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
      } catch {
        // Keep cached profile values if refresh fails.
      }
    };

    loadProfileSettings();
    return () => {
      isMounted = false;
    };
  }, [navigate]);

  if (!user) {
    return null;
  }

  const bioWords = word_count(bio);

  const handle_save_profile = () => {
    const nextName = displayName.trim();
    if (!nextName) {
      toast.error('Display name cannot be empty');
      return;
    }

    if (bioWords > MAX_BIO_WORDS) {
      toast.error(`Bio cannot exceed ${MAX_BIO_WORDS} words`);
      return;
    }

    const updatedUser = {
      ...user,
      name: nextName,
    };

    setProfileOverride(user.id, {
      displayName: nextName,
      bio: bio.trim(),
      avatarUrl: profilePicture.trim(),
    });
    setCurrentUser(updatedUser);
    setUser(updatedUser);
    toast.success('Profile updated successfully!');
    navigate('/profile');
  };

  const handle_profile_picture_upload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) {
      return;
    }
    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file');
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        setProfilePicture(reader.result);
      }
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <Button variant="ghost" size="sm" onClick={() => navigate('/profile')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Profile
          </Button>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-3xl">
        <Card>
          <CardHeader>
            <h1 className="text-2xl font-bold">Profile Settings</h1>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="display-name" className="text-sm font-medium">Display Name</label>
              <Input
                id="display-name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Your display name"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="profile-picture-url" className="text-sm font-medium">Profile Picture URL</label>
              <Input
                id="profile-picture-url"
                value={profilePicture}
                onChange={(e) => setProfilePicture(e.target.value)}
                placeholder="https://example.com/profile.jpg"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="profile-picture-upload" className="text-sm font-medium">Upload Profile Picture</label>
              <Input
                id="profile-picture-upload"
                type="file"
                accept="image/*"
                onChange={handle_profile_picture_upload}
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="bio" className="text-sm font-medium">Bio</label>
              <Textarea
                id="bio"
                value={bio}
                onChange={(e) => setBio(trim_to_max_words(e.target.value, MAX_BIO_WORDS))}
                placeholder="Tell people a little about yourself"
                maxLength={700}
              />
              <p className="text-xs text-muted-foreground">{bioWords}/{MAX_BIO_WORDS} words</p>
            </div>

            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => navigate('/profile')}>
                Cancel
              </Button>
              <Button onClick={handle_save_profile}>Save Profile</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

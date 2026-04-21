import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Button } from '../components/ui/button';
import { AuthModal } from '../components/AuthModal';
import { getCurrentUser } from '../lib/storage';
import { MapPin, TrendingUp, Users, Calendar } from 'lucide-react';
import logoImage from '../../imports/CityPulse_Logo.png';

const heroImages = [
  'https://images.unsplash.com/photo-1630601836891-92035f0fe07e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxHb2xkZW4lMjBHYXRlJTIwQnJpZGdlJTIwU2FuJTIwRnJhbmNpc2NvJTIwc2NlbmljfGVufDF8fHx8MTc3NjMwNjU5OHww&ixlib=rb-4.1.0&q=80&w=1080',
  'https://images.unsplash.com/photo-1668323555953-945aabae955d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxZb3NlbWl0ZSUyME5hdGlvbmFsJTIwUGFyayUyMENhbGlmb3JuaWF8ZW58MXx8fHwxNzc2MzA2NTk4fDA&ixlib=rb-4.1.0&q=80&w=1080',
  'https://images.unsplash.com/photo-1635310426204-d88ffb4f8591?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxIb2xseXdvb2QlMjBTaWduJTIwTG9zJTIwQW5nZWxlcyUyMHN1bnNldHxlbnwxfHx8fDE3NzYzMDY1OTl8MA&ixlib=rb-4.1.0&q=80&w=1080',
  'https://images.unsplash.com/photo-1614667033956-e66b0e187f32?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxCaWclMjBTdXIlMjBDYWxpZm9ybmlhJTIwY29hc3RsaW5lfGVufDF8fHx8MTc3NjMwNjU5OXww&ixlib=rb-4.1.0&q=80&w=1080',
  'https://images.unsplash.com/photo-1668636936878-bd201871048b?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxTYW50YSUyME1vbmljYSUyMFBpZXIlMjBDYWxpZm9ybmlhfGVufDF8fHx8MTc3NjMwNjU5OXww&ixlib=rb-4.1.0&q=80&w=1080',
];

export function Landing() {
  const [showAuth, setShowAuth] = useState(false);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    // If user is already logged in, redirect to feed
    const user = getCurrentUser();
    if (user) {
      navigate('/feed');
    }
  }, [navigate]);

  useEffect(() => {
    // Slideshow interval
    const interval = setInterval(() => {
      setCurrentImageIndex((prevIndex) => (prevIndex + 1) % heroImages.length);
    }, 5000); // Change image every 5 seconds

    return () => clearInterval(interval);
  }, []);

  const handleAuthSuccess = () => {
    navigate('/feed');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src={logoImage} alt="CityPulse Logo" className="w-10 h-10" />
              <span className="text-2xl font-bold" style={{ 
                background: 'linear-gradient(135deg, #FF6B35 0%, #004E89 50%, #E63946 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                CityPulse
              </span>
            </div>
            <Button onClick={() => setShowAuth(true)}>
              Sign In
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="max-w-4xl mx-auto text-center space-y-8 relative">
          {/* Background Slideshow */}
          <div className="absolute inset-0 -z-10 overflow-hidden rounded-3xl">
            {heroImages.map((image, index) => (
              <div
                key={index}
                className={`absolute inset-0 transition-opacity duration-1000 ${
                  index === currentImageIndex ? 'opacity-30' : 'opacity-0'
                }`}
              >
                <img
                  src={image}
                  alt={`Scenic view ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </div>
            ))}
            <div className="absolute inset-0 bg-gradient-to-b from-white/60 via-white/80 to-white/90" />
          </div>

          <h1 className="text-5xl md:text-6xl font-bold leading-tight relative z-10">
            Discover What's Happening{' '}
            <span style={{ 
              background: 'linear-gradient(135deg, #FF6B35 0%, #004E89 50%, #E63946 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              In Your City
            </span>
          </h1>
          
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto relative z-10">
            CityPulse connects you to the most significant events, market trends, 
            and discussions happening in your region in real-time.
          </p>

          <div className="flex justify-center relative z-10">
            <Button 
              size="lg" 
              className="text-lg px-8"
              onClick={() => setShowAuth(true)}
            >
              Get Started
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mt-24 max-w-5xl mx-auto">
          <div className="bg-white rounded-lg p-8 shadow-sm border">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{ backgroundColor: 'rgba(255, 107, 53, 0.1)' }}>
              <MapPin className="w-6 h-6" style={{ color: '#FF6B35' }} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Location-Based Discovery</h3>
            <p className="text-muted-foreground">
              Find events and trends specifically happening in your city or region.
            </p>
          </div>

          <div className="bg-white rounded-lg p-8 shadow-sm border">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{ backgroundColor: 'rgba(0, 78, 137, 0.1)' }}>
              <TrendingUp className="w-6 h-6" style={{ color: '#004E89' }} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Real-Time Trends</h3>
            <p className="text-muted-foreground">
              Stay updated with what's trending and popular in your community.
            </p>
          </div>

          <div className="bg-white rounded-lg p-8 shadow-sm border">
            <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{ backgroundColor: 'rgba(230, 57, 70, 0.1)' }}>
              <Users className="w-6 h-6" style={{ color: '#E63946' }} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Connect & Attend</h3>
            <p className="text-muted-foreground">
              Interact with others, make plans, and declare your attendance to events.
            </p>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-24 bg-white rounded-2xl p-12 shadow-sm border max-w-5xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2" style={{ color: '#FF6B35' }}>10k+</div>
              <div className="text-muted-foreground">Active Events</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2" style={{ color: '#004E89' }}>50k+</div>
              <div className="text-muted-foreground">Community Members</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2" style={{ color: '#E63946' }}>100+</div>
              <div className="text-muted-foreground">Cities Covered</div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-24 text-center space-y-6">
          <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm">
            <Calendar className="w-4 h-4" />
            <span>New events added daily</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold">
            Ready to Explore Your City?
          </h2>
          <Button 
            size="lg" 
            className="text-lg px-8"
            onClick={() => setShowAuth(true)}
          >
            Create Your Account
          </Button>
        </div>
      </div>

      {/* Auth Modal */}
      <AuthModal
        open={showAuth}
        onOpenChange={setShowAuth}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
}
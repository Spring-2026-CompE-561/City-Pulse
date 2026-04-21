export interface User {
  id: string;
  name: string;
  email: string;
  avatar: string;
  location: string;
}

export interface Event {
  id: string;
  title: string;
  description: string;
  category: string;
  location: string;
  city: string;
  date: string;
  time: string;
  image: string;
  organizer: User;
  attendees: string[]; // user IDs
  trending: boolean;
}

export interface Comment {
  id: string;
  eventId: string;
  userId: string;
  user: User;
  text: string;
  timestamp: string;
}

export const mockUsers: User[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    email: 'sarah@example.com',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop',
    location: 'San Francisco, CA',
  },
  {
    id: '2',
    name: 'Marcus Johnson',
    email: 'marcus@example.com',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop',
    location: 'New York, NY',
  },
  {
    id: '3',
    name: 'Emily Rodriguez',
    email: 'emily@example.com',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=100&h=100&fit=crop',
    location: 'Los Angeles, CA',
  },
  {
    id: '4',
    name: 'David Kim',
    email: 'david@example.com',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=100&h=100&fit=crop',
    location: 'San Francisco, CA',
  },
  {
    id: '5',
    name: 'Jessica Williams',
    email: 'jessica@example.com',
    avatar: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&h=100&fit=crop',
    location: 'New York, NY',
  },
];

export const mockEvents: Event[] = [
  {
    id: '1',
    title: 'Tech Innovation Summit 2026',
    description: 'Join industry leaders for a day of cutting-edge tech discussions, networking, and innovation showcases. Featured speakers include top CTOs and startup founders.',
    category: 'Technology',
    location: 'Moscone Center',
    city: 'San Francisco, CA',
    date: '2026-04-15',
    time: '9:00 AM - 6:00 PM',
    image: 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&h=600&fit=crop',
    organizer: mockUsers[0],
    attendees: ['2', '4', '5'],
    trending: true,
  },
  {
    id: '2',
    title: 'Urban Art Festival',
    description: 'Experience the vibrant street art culture with live painting sessions, gallery exhibitions, and interactive workshops from renowned urban artists.',
    category: 'Arts & Culture',
    location: 'Golden Gate Park',
    city: 'San Francisco, CA',
    date: '2026-04-20',
    time: '11:00 AM - 8:00 PM',
    image: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=800&h=600&fit=crop',
    organizer: mockUsers[3],
    attendees: ['1', '2'],
    trending: false,
  },
  {
    id: '3',
    title: 'Sustainable Living Workshop',
    description: 'Learn practical tips for eco-friendly living, zero-waste practices, and sustainable home improvements. Includes hands-on demonstrations and expert Q&A.',
    category: 'Environment',
    location: 'Community Center',
    city: 'San Francisco, CA',
    date: '2026-04-12',
    time: '2:00 PM - 5:00 PM',
    image: 'https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&h=600&fit=crop',
    organizer: mockUsers[1],
    attendees: ['3', '4'],
    trending: true,
  },
  {
    id: '4',
    title: 'Broadway Night: Hamilton',
    description: 'Experience the musical phenomenon that redefined Broadway. Special evening performance with post-show Q&A with the cast.',
    category: 'Entertainment',
    location: 'Broadway Theatre',
    city: 'New York, NY',
    date: '2026-04-18',
    time: '7:30 PM - 10:30 PM',
    image: 'https://images.unsplash.com/photo-1503095396549-807759245b35?w=800&h=600&fit=crop',
    organizer: mockUsers[4],
    attendees: ['1', '3', '5'],
    trending: true,
  },
  {
    id: '5',
    title: 'Startup Founder Meetup',
    description: 'Monthly gathering for startup founders and entrepreneurs. Share experiences, network, and discuss challenges in building successful companies.',
    category: 'Business',
    location: 'WeWork SoMa',
    city: 'San Francisco, CA',
    date: '2026-04-10',
    time: '6:00 PM - 9:00 PM',
    image: 'https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=800&h=600&fit=crop',
    organizer: mockUsers[0],
    attendees: ['2', '4'],
    trending: false,
  },
  {
    id: '6',
    title: 'Food Truck Festival',
    description: 'Taste cuisine from over 50 food trucks featuring international flavors. Live music, craft beer garden, and family-friendly activities all day.',
    category: 'Food & Drink',
    location: 'Central Park',
    city: 'New York, NY',
    date: '2026-04-25',
    time: '12:00 PM - 10:00 PM',
    image: 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&h=600&fit=crop',
    organizer: mockUsers[2],
    attendees: ['1', '3', '4', '5'],
    trending: true,
  },
  {
    id: '7',
    title: 'Morning Yoga in the Park',
    description: 'Start your day with guided yoga sessions suitable for all levels. Bring your mat and enjoy mindfulness in nature with our certified instructors.',
    category: 'Health & Wellness',
    location: 'Griffith Park',
    city: 'Los Angeles, CA',
    date: '2026-04-08',
    time: '7:00 AM - 8:30 AM',
    image: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&h=600&fit=crop',
    organizer: mockUsers[2],
    attendees: ['3'],
    trending: false,
  },
  {
    id: '8',
    title: 'Crypto & Web3 Conference',
    description: 'Explore the future of blockchain technology, DeFi, and NFTs. Expert panels, networking sessions, and exclusive project launches.',
    category: 'Technology',
    location: 'Convention Center',
    city: 'San Francisco, CA',
    date: '2026-04-22',
    time: '10:00 AM - 7:00 PM',
    image: 'https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800&h=600&fit=crop',
    organizer: mockUsers[3],
    attendees: ['1', '2', '4'],
    trending: true,
  },
  {
    id: '9',
    title: 'Jazz Night at Blue Note',
    description: 'An intimate evening of live jazz featuring Grammy-nominated artists. Classic cocktails and sophisticated ambiance make this a perfect night out.',
    category: 'Music',
    location: 'Blue Note Jazz Club',
    city: 'New York, NY',
    date: '2026-04-14',
    time: '8:00 PM - 11:00 PM',
    image: 'https://images.unsplash.com/photo-1415201364774-f6f0bb35f28f?w=800&h=600&fit=crop',
    organizer: mockUsers[4],
    attendees: ['2', '5'],
    trending: false,
  },
  {
    id: '10',
    title: 'Indie Film Screening & Discussion',
    description: 'Premiere screening of award-winning independent films followed by filmmaker Q&A. Supporting emerging voices in cinema.',
    category: 'Arts & Culture',
    location: 'Alamo Drafthouse',
    city: 'Los Angeles, CA',
    date: '2026-04-17',
    time: '7:00 PM - 10:00 PM',
    image: 'https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&h=600&fit=crop',
    organizer: mockUsers[2],
    attendees: ['1', '3'],
    trending: false,
  },
];

export const cities = [
  'All Cities',
  'San Francisco, CA',
  'New York, NY',
  'Los Angeles, CA',
  'San Diego, CA',
  'Chicago, IL',
  'Miami, FL',
  'Seattle, WA',
  'Austin, TX',
];

export const categories = [
  'All Categories',
  'Technology',
  'Arts & Culture',
  'Environment',
  'Entertainment',
  'Business',
  'Food & Drink',
  'Health & Wellness',
  'Music',
];
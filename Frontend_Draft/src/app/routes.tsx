import { createBrowserRouter } from 'react-router';
import { Landing } from './pages/Landing';
import { Feed } from './pages/Feed';
import { EventDetail } from './pages/EventDetail';
import { Profile } from './pages/Profile';
import { CreateEvent } from './pages/CreateEvent';
import { NotFound } from './pages/NotFound';

export const router = createBrowserRouter([
  {
    path: '/',
    Component: Landing,
  },
  {
    path: '/feed',
    Component: Feed,
  },
  {
    path: '/event/:id',
    Component: EventDetail,
  },
  {
    path: '/profile',
    Component: Profile,
  },
  {
    path: '/create',
    Component: CreateEvent,
  },
  {
    path: '*',
    Component: NotFound,
  },
]);
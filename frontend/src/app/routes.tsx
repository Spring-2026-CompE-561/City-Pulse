import { createBrowserRouter } from 'react-router';
import { Landing } from './pages/Landing';
import { Feed } from './pages/Feed';
import { EventDetail } from './pages/EventDetail';
import { Profile } from './pages/Profile';
import { ProfileSettings } from './pages/ProfileSettings';
import { CreateEvent } from './pages/CreateEvent';
import { PartnerSubmission } from './pages/PartnerSubmission';
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
    path: '/profile/settings',
    Component: ProfileSettings,
  },
  {
    path: '/create',
    Component: CreateEvent,
  },
  {
    path: '/submit-partner-event',
    Component: PartnerSubmission,
  },
  {
    path: '*',
    Component: NotFound,
  },
]);
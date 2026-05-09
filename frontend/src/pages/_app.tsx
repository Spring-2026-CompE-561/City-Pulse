import type { AppProps } from 'next/app';
import { ThemeProvider } from 'next-themes';

import { Toaster } from '../app/components/ui/sonner';
import '../styles/index.css';

export default function CityPulseApp({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      storageKey="citypulse-theme"
    >
      <Component {...pageProps} />
      <Toaster />
    </ThemeProvider>
  );
}

import type { AppProps } from 'next/app';
import { Toaster } from '../app/components/ui/sonner';
import '../styles/index.css';

export default function CityPulseApp({ Component, pageProps }: AppProps) {
  return (
    <>
      <Component {...pageProps} />
      <Toaster />
    </>
  );
}

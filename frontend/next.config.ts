import type { NextConfig } from 'next';

const backend_api_origin =
  process.env.BACKEND_API_ORIGIN
  ?? process.env.NEXT_PUBLIC_API_BASE_URL
  ?? 'http://127.0.0.1:8000';

const next_config: NextConfig = {
  reactStrictMode: true,
  // Keep API proxy paths unchanged so FastAPI canonical URLs do not bounce
  // through browser-visible absolute redirects (which can surface as fetch failures).
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${backend_api_origin}/api/:path*`,
      },
      {
        source: '/media/:path*',
        destination: `${backend_api_origin}/media/:path*`,
      },
    ];
  },
};

export default next_config;

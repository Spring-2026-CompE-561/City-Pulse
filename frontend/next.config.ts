import type { NextConfig } from 'next';

const backend_api_origin = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://127.0.0.1:8000';

const next_config: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  skipTrailingSlashRedirect: true,
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${backend_api_origin}/api/:path*`,
      },
    ];
  },
};

export default next_config;

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable React Strict Mode for better development experience
  reactStrictMode: true,

  // Optimize images
  images: {
    remotePatterns: [
      // Add remote image domains here if needed
      // { protocol: 'https', hostname: 'example.com' },
    ],
  },

  // Environment variables that should be available on the client
  // Note: Only add non-sensitive values here
  env: {
    APP_NAME: process.env.APP_NAME || '{{ app_name }}',
  },

  // Experimental features (enable carefully)
  experimental: {
    // typedRoutes: true,
  },
};

export default nextConfig;

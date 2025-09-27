/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'p3-ofp.static.pub',
      },
      {
        protocol: 'https',
        hostname: 'p1-ofp.static.pub',
      },
      {
        protocol: 'https',
        hostname: 'hp.widen.net',
      },
      {
        protocol: 'https',
        hostname: 'www.hp.com',
      },
    ],
  },
};

module.exports = nextConfig;
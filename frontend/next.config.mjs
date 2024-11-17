/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'http',
        hostname: 'localhost',
        port: '4200',
        pathname: '/uploads/**',
      },
      {
        protocol: 'https',
        hostname: 'icaam-backend.swedencentral.azurecontainer.io',
        port: '',
        pathname: '/uploads/**',
      },
    ],
  },
}

export default nextConfig

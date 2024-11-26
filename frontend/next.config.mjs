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
        pathname: '/uploads/**',
      },
    ],
    // In real production workflow we would optimize images
    // however we are missing true domain and have to use self-signed certificate
    // nextjs does not support self-signed certificates
    unoptimized: true,
  },
}

export default nextConfig

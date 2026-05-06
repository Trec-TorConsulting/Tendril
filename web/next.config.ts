import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  turbopack: {},
  typescript: {
    // TS is checked in CI; skip during Docker cross-compile to avoid OOM
    ignoreBuildErrors: true,
  },
};

export default nextConfig;

import path from "node:path";
import { loadEnvConfig } from "@next/env"; // named import: Next compiles this file to CommonJS
import type { NextConfig } from "next";

// Local development reads the repository's root .env (git-ignored); on Vercel the same names are set
// as project environment variables.
// forceReload: Next has already loaded app/ (which has no .env) before reading this file.
loadEnvConfig(path.resolve(process.cwd(), ".."), process.env.NODE_ENV !== "production", console, true);

const nextConfig: NextConfig = {};
export default nextConfig;

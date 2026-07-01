// API route: GET /api/debug
import type { APIRoute } from 'astro';

export const prerender = false;

export const GET: APIRoute = async () => {
  const envKeys = Object.keys(process.env).filter(k => 
    k.includes('NOTION') || k.includes('JWT') || k.includes('VERCEL')
  );
  const envVals: Record<string, string> = {};
  for (const k of envKeys) {
    const v = process.env[k] || '';
    envVals[k] = v.length > 10 ? v.substring(0, 5) + '...' + v.substring(v.length - 4) : v;
  }
  return new Response(JSON.stringify({
    env_keys: envKeys,
    env_preview: envVals,
    has_process: typeof process !== 'undefined',
    has_notion_token: !!process.env.NOTION_TOKEN,
    has_notion_db: !!process.env.NOTION_USERS_DB_ID,
    runtime: 'vercel-serverless',
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};
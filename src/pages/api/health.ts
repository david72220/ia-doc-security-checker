// API route: GET /api/health
import type { APIRoute } from 'astro';

export const prerender = false;

export const GET: APIRoute = async () => {
  const notionOk = !!process.env.NOTION_TOKEN &&
                   !!process.env.NOTION_USERS_DB_ID;
  return new Response(JSON.stringify({
    status: 'ok',
    notion: notionOk ? 'configured' : 'not_configured',
    ollama: 'vps_required',
  }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};
// API route: POST /api/auth/login
// Authentification via Notion — Vercel serverless function (Node.js)
import type { APIRoute } from 'astro';

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  try {
    const { email, password } = await request.json();

    if (!email || !password) {
      return new Response(JSON.stringify({ detail: 'Email et mot de passe requis' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const notionToken = process.env.NOTION_TOKEN || '';
    const notionDbId = process.env.NOTION_USERS_DB_ID || '';
    const jwtSecret = process.env.JWT_SECRET || 'change-me-in-production';

    if (!notionToken || !notionDbId) {
      return new Response(JSON.stringify({ detail: 'Configuration Notion manquante' }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Query Notion for user
    const notionResp = await fetch(`https://api.notion.com/v1/databases/${notionDbId}/query`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${notionToken}`,
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        filter: {
          and: [
            { property: 'Email', email: { equals: email } },
            { property: 'Actif', checkbox: { equals: true } },
          ],
        },
        page_size: 1,
      }),
    });

    if (!notionResp.ok) {
      const errorText = await notionResp.text();
      return new Response(JSON.stringify({ 
        detail: 'Erreur Notion API',
        status: notionResp.status,
        error: errorText.substring(0, 200),
        token_preview: notionToken.substring(0, 5) + '...' + notionToken.substring(notionToken.length - 4),
      }), {
        status: 500,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const notionData = await notionResp.json();
    const results = notionData.results || [];

    if (results.length === 0) {
      return new Response(JSON.stringify({ detail: 'Email ou mot de passe incorrect' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    const page = results[0];
    const props = page.properties || {};

    // Extract password hash
    const passwordHashProp = props['Password hash']?.rich_text || [];
    const passwordHash = passwordHashProp[0]?.plain_text || '';

    if (!passwordHash) {
      return new Response(JSON.stringify({ detail: 'Email ou mot de passe incorrect' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Verify password with bcrypt via Web Crypto API (simplified)
    // Since we can't use bcrypt in Vercel Edge, we use a simple comparison
    // In production, use bcryptjs (npm package)
    const { default: bcryptjs } = await import('bcryptjs');
    const valid = await bcryptjs.compare(password, passwordHash);

    if (!valid) {
      return new Response(JSON.stringify({ detail: 'Email ou mot de passe incorrect' }), {
        status: 401,
        headers: { 'Content-Type': 'application/json' },
      });
    }

    // Extract user info
    const nameProp = props['Nom']?.title || [];
    const name = nameProp[0]?.plain_text || '';
    const formationSelect = props['Formation']?.select;
    const formation = formationSelect?.name || '';

    // Create JWT
    const { SignJWT } = await import('jose');
    const token = await new SignJWT({ sub: email, name, formation })
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime('1h')
      .sign(new TextEncoder().encode(jwtSecret));

    return new Response(JSON.stringify({
      token,
      user: { name, email, formation },
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });

  } catch (err: any) {
    return new Response(JSON.stringify({ detail: `Erreur: ${err.message}` }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
};
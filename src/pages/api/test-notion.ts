// API route: GET /api/test-notion
// Test direct de la connexion Notion
import type { APIRoute } from 'astro';

export const prerender = false;

export const GET: APIRoute = async () => {
  const notionToken = process.env.NOTION_TOKEN || '';
  const notionDbId = process.env.NOTION_USERS_DB_ID || '';
  
  // Test 1: List databases (si le token est valide)
  const listResp = await fetch('https://api.notion.com/v1/databases/' + notionDbId, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${notionToken}`,
      'Notion-Version': '2022-06-28',
    },
  });
  
  const listText = await listResp.text();
  
  // Test 2: Query database
  const queryResp = await fetch(`https://api.notion.com/v1/databases/${notionDbId}/query`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${notionToken}`,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ page_size: 1 }),
  });
  
  const queryText = await queryResp.text();
  
  return new Response(JSON.stringify({
    token_present: !!notionToken,
    token_length: notionToken.length,
    token_start: notionToken.substring(0, 8),
    token_end: notionToken.substring(notionToken.length - 4),
    db_id: notionDbId,
    test_get_database: {
      status: listResp.status,
      response: listText.substring(0, 500),
    },
    test_query_database: {
      status: queryResp.status,
      response: queryText.substring(0, 500),
    },
  }, null, 2), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
};
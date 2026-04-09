// Using global fetch (available in Node 18+) to avoid extra dependencies

export default async function handler(req, res) {
  // Read the secret VPS IP from the Environment Variable
  const apiBaseUrl = process.env.VITE_API_BASE_URL;

  if (!apiBaseUrl) {
    return res.status(500).json({ error: 'VITE_API_BASE_URL is not configured on Vercel' });
  }

  // Extract the path from the URL (e.g., /api/orders -> orders)
  const path = req.url.replace(/^\/api/, '');
  const targetUrl = `${apiBaseUrl}${path}`;

  try {
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
      },
      // Only include body for non-GET/HEAD requests
      body: ['GET', 'HEAD'].includes(req.method) ? undefined : JSON.stringify(req.body),
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Proxy Error:', error);
    res.status(500).json({ error: 'Failed to reach the backend server' });
  }
}

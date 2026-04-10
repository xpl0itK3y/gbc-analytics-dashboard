const getApiBaseUrl = () => {
  const value = process.env.VITE_API_BASE_URL || process.env.API_BASE_URL;
  if (!value) {
    return null;
  }

  return value.endsWith("/") ? value.slice(0, -1) : value;
};

export default async function handler(req, res) {
  const apiBaseUrl = getApiBaseUrl();

  if (!apiBaseUrl) {
    return res.status(500).json({
      error: "VITE_API_BASE_URL is not configured",
    });
  }

  const query = new URLSearchParams();
  Object.entries(req.query || {}).forEach(([key, value]) => {
    if (Array.isArray(value)) {
      value.forEach((item) => query.append(key, item));
      return;
    }

    if (value !== undefined) {
      query.append(key, value);
    }
  });

  const search = query.toString();
  const targetUrl = `${apiBaseUrl}/orders/${search ? `?${search}` : ""}`;

  try {
    const response = await fetch(targetUrl, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
      redirect: "follow",
    });

    const contentType = response.headers.get("content-type") || "application/json";
    const rawBody = await response.text();

    res.status(response.status);
    res.setHeader("Content-Type", contentType);
    return res.send(rawBody);
  } catch (error) {
    return res.status(500).json({
      error: "Failed to reach the backend server",
      details: error.message,
    });
  }
}

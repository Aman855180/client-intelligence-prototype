// Thin client for POST /analyze. Kept separate from components so the
// fetch/error-shape logic isn't duplicated across the UI.

const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

export async function analyzeConversation(conversation) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ conversation }),
  });

  let body;
  try {
    body = await res.json();
  } catch {
    throw new Error("The server returned a response that could not be parsed.");
  }

  if (!res.ok) {
    throw new Error(body.detail || `Request failed with status ${res.status}.`);
  }

  if (!body.success || !body.data) {
    throw new Error(body.error || "The analysis did not complete successfully.");
  }

  return body.data;
}

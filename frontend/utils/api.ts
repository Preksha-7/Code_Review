const API_URL = "http://127.0.0.1:8000";

export const analyzeCode = async (code: string) => {
  const response = await fetch(`${API_URL}/review/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code_snippet: code }),
  });

  return response.json();
};

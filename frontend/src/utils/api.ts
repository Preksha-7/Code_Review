const API_URL = "http://127.0.0.1:8000";

export const analyzeCode = async (code: string) => {
  try {
    const response = await fetch(`${API_URL}/review/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error("API error:", error);
    throw error;
  }
};

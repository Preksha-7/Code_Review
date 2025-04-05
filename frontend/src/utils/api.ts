const API_URL = "http://127.0.0.1:8000";

export const analyzeCode = async (code: string, language: string) => {
  try {
    const response = await fetch(`${API_URL}/review/analyze`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code, language }),
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

export const getSupportedLanguages = async () => {
  try {
    const response = await fetch(`${API_URL}/review/supported-languages`);

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return response.json();
  } catch (error) {
    console.error("API error:", error);
    throw error;
  }
};

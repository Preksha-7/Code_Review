const API_URL = "http://127.0.0.1:8000";

export const loginWithGitHub = async () => {
  try {
    const response = await fetch(`${API_URL}/auth/github`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    console.log("Auth URL received, redirecting to GitHub login...");
    window.location.href = data.auth_url;
  } catch (error) {
    console.error("Error getting auth URL:", error);
    alert("Failed to initiate GitHub login. Please try again.");
  }
};

// Handle the callback from GitHub
export const handleGitHubCallback = async (code: string) => {
  if (!code) return null;

  try {
    const response = await fetch(`${API_URL}/auth/callback?code=${code}`, {
      method: "GET",
      headers: {
        Accept: "application/json",
      },
    });

    if (!response.ok) {
      console.error(`Callback error: ${response.status}`);
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();

    if (data.user) {
      console.log("User data received, saving to localStorage");
      // Store user data in localStorage
      localStorage.setItem("user", JSON.stringify(data.user));
      return data.user;
    }
    return null;
  } catch (error) {
    console.error("Error during GitHub callback:", error);
    return null;
  }
};

// Logout function
export const logout = () => {
  localStorage.removeItem("user");
  window.location.href = "/";
};

// Get user from localStorage with improved error handling
export const getUser = () => {
  if (typeof window !== "undefined") {
    try {
      const userStr = localStorage.getItem("user");
      if (!userStr) return null;

      const user = JSON.parse(userStr);
      return user;
    } catch (e) {
      console.error("Error parsing user from localStorage:", e);
      // If there's an error parsing, clear the corrupted data
      localStorage.removeItem("user");
      return null;
    }
  }
  return null;
};

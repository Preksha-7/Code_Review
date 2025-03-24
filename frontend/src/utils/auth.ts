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

export const handleGitHubCallback = async (code: string) => {
  if (!code) return null;

  try {
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get("token");

    if (!token) {
      throw new Error("No auth token found in URL");
    }

    const response = await fetch(`${API_URL}/auth/userinfo`, {
      method: "GET",
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    const userData = await response.json();

    localStorage.setItem("user", JSON.stringify(userData));
    localStorage.setItem("authToken", token);

    return userData;
  } catch (error) {
    console.error("Error during GitHub callback:", error);
    return null;
  }
};

export const logout = () => {
  localStorage.removeItem("user");
  localStorage.removeItem("authToken");
  window.location.href = "/";
};

export const getUser = () => {
  if (typeof window !== "undefined") {
    try {
      const userStr = localStorage.getItem("user");
      if (!userStr) return null;

      const user = JSON.parse(userStr);

      // Check if auth token is still present
      const token = localStorage.getItem("authToken");
      if (!token) {
        console.warn("Auth token missing, logging out user");
        localStorage.removeItem("user");
        return null;
      }

      return user;
    } catch (e) {
      console.error("Error parsing user from localStorage:", e);
      localStorage.removeItem("user");
      return null;
    }
  }
  return null;
};

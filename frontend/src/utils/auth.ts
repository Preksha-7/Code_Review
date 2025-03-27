const API_URL = "http://127.0.0.1:8000";

export const loginWithGitHub = () => {
  // Force a fresh login by clearing existing authentication data
  localStorage.removeItem("user");
  localStorage.removeItem("authToken");

  // Redirect to GitHub login
  window.location.href = `${API_URL}/auth/github`;
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
    localStorage.setItem("lastLoginTimestamp", Date.now().toString());

    return userData;
  } catch (error) {
    console.error("Error during GitHub callback:", error);
    return null;
  }
};

export const logout = () => {
  localStorage.removeItem("user");
  localStorage.removeItem("authToken");
  localStorage.removeItem("lastLoginTimestamp");
  window.location.href = "/";
};

export const getUser = () => {
  if (typeof window !== "undefined") {
    try {
      const userStr = localStorage.getItem("user");
      const token = localStorage.getItem("authToken");
      const lastLoginTimestamp = localStorage.getItem("lastLoginTimestamp");

      // Check if all required authentication data exists
      if (!userStr || !token || !lastLoginTimestamp) {
        console.warn("Authentication data incomplete, logging out user");
        logout();
        return null;
      }

      const user = JSON.parse(userStr);

      // Optional: Add token expiration check (adjust time as needed)
      const TOKEN_EXPIRATION_TIME = 24 * 60 * 60 * 1000; // 24 hours
      const currentTime = Date.now();
      const loginTime = parseInt(lastLoginTimestamp, 10);

      if (currentTime - loginTime > TOKEN_EXPIRATION_TIME) {
        console.warn("Authentication expired, logging out user");
        logout();
        return null;
      }

      return user;
    } catch (e) {
      console.error("Error parsing user from localStorage:", e);
      logout();
      return null;
    }
  }
  return null;
};

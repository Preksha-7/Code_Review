const API_URL = "http://127.0.0.1:8000";

export const loginWithGitHub = async () => {
  const response = await fetch(`${API_URL}/auth/github`);
  const data = await response.json();
  console.log("Auth URL:", data.auth_url);
  window.location.href = data.auth_url;
};

// Handle the callback from GitHub
export const handleGitHubCallback = async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const code = urlParams.get("code");

  if (!code) return;

  try {
    const response = await fetch(`${API_URL}/auth/callback?code=${code}`);
    const data = await response.json();

    if (data.user) {
      localStorage.setItem("user", JSON.stringify(data.user));
      window.location.href = "/"; // Redirect to home after login
    }
  } catch (error) {
    console.error("Error during GitHub callback:", error);
  }
};

// Logout function
export const logout = () => {
  localStorage.removeItem("user");
  window.location.href = "/";
};

// Get user from localStorage
export const getUser = () => {
  if (typeof window !== "undefined") {
    const user = localStorage.getItem("user");
    return user ? JSON.parse(user) : null;
  }
  return null;
};

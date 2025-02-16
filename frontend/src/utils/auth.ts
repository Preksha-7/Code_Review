export const loginWithGitHub = async () => {
  const response = await fetch("http://127.0.0.1:8000/auth/github");
  const data = await response.json();
  console.log("Auth URL:", data.auth_url);
  window.location.href = data.auth_url;
};

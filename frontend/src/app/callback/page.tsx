"use client";

import { useEffect, useState } from "react";
import { handleGitHubCallback } from "@/utils/auth";
import { useRouter } from "next/navigation";

export default function Callback() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const processCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get("code");

      if (!code) {
        setError("No authorization code provided");
        return;
      }

      try {
        const user = await handleGitHubCallback(code);
        if (user) {
          // Redirect to home page after successful login
          router.push("/");
        } else {
          setError("Failed to authenticate");
        }
      } catch (err) {
        setError("Authentication error occurred");
        console.error(err);
      }
    };

    processCallback();
  }, [router]);

  // Simple loading screen while processing
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      {error ? (
        <div className="text-red-500">{error}</div>
      ) : (
        <>
          <div className="mb-4 text-xl font-bold">Logging you in...</div>
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
        </>
      )}
    </div>
  );
}

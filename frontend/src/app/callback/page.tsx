"use client";

import { useEffect, useState } from "react";
import { handleGitHubCallback } from "@/utils/auth";
import { useRouter } from "next/navigation";

export default function Callback() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string>(
    "Authenticating with GitHub..."
  );

  useEffect(() => {
    const processCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get("code");

      if (!code) {
        setError("No authorization code provided");
        return;
      }

      try {
        setProcessingStatus("Processing authentication...");
        const user = await handleGitHubCallback(code);

        if (user) {
          setProcessingStatus("Login successful! Redirecting...");
          // Use a small timeout to ensure localStorage is updated
          setTimeout(() => {
            // Force a hard redirect to ensure a fresh page load
            window.location.href = "/";
          }, 500);
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

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-md w-full">
        {error ? (
          <div className="text-red-500 text-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-12 w-12 mx-auto mb-4 text-red-500"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <p className="font-bold mb-2">Authentication Error</p>
            <p>{error}</p>
            <button
              onClick={() => router.push("/")}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700"
            >
              Return to Home
            </button>
          </div>
        ) : (
          <>
            <div className="text-center">
              <div className="h-12 w-12 mx-auto mb-4 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
              <p className="text-xl font-bold mb-2">Please wait</p>
              <p className="text-gray-600">{processingStatus}</p>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

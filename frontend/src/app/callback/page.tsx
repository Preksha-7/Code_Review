"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Callback() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string>(
    "Finalizing login..."
  );

  useEffect(() => {
    // Check for auth=success parameter
    const urlParams = new URLSearchParams(window.location.search);
    const authStatus = urlParams.get("auth");
    const token = urlParams.get("token");

    if (authStatus === "success" && token) {
      // Store the token
      localStorage.setItem("authToken", token);

      // Fetch user data with token in Authorization header
      fetch(`http://127.0.0.1:8000/auth/userinfo`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((res) => {
          if (!res.ok) {
            return res.text().then((text) => {
              try {
                // Try to parse as JSON for better error details
                const errorData = JSON.parse(text);
                throw new Error(
                  `Failed to fetch user data: ${res.status} - ${JSON.stringify(
                    errorData
                  )}`
                );
              } catch (e) {
                // If not JSON, use raw text
                throw new Error(
                  `Failed to fetch user data: ${res.status} - ${text}`
                );
              }
            });
          }
          return res.json();
        })
        .then((userData) => {
          // Store user data in localStorage
          localStorage.setItem("user", JSON.stringify(userData));
          setProcessingStatus(
            "Login successful! Redirecting to code analyzer..."
          );
          // Use router for client-side navigation directly to the analyzer
          setTimeout(() => {
            router.push("/");
          }, 1000);
        })
        .catch((err) => {
          console.error("Error fetching user data:", err);
          setError(err.message);
        });
    } else {
      setError(
        "Invalid authentication response. Missing token or auth status."
      );
    }
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

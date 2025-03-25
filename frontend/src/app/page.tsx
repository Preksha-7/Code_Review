"use client";

import { loginWithGitHub, logout, getUser } from "@/utils/auth";
import { analyzeCode } from "@/utils/api";
import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [codeSnippet, setCodeSnippet] = useState("");
  const [reviewResult, setReviewResult] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    // Check for authentication parameters from callback
    const authStatus = searchParams.get("auth");
    const token = searchParams.get("token");
    const name = searchParams.get("name");
    const email = searchParams.get("email");
    const picture = searchParams.get("picture");

    const checkUserAuth = () => {
      try {
        // If we have auth parameters, create user object and store in localStorage
        if (authStatus === "success" && token) {
          const userData = { name, email, picture };
          localStorage.setItem("user", JSON.stringify(userData));
          localStorage.setItem("authToken", token);

          // Redirect to clean URL
          router.replace("/");
        }

        // Check for existing user
        const currentUser = getUser();
        setUser(currentUser);
      } catch (error) {
        console.error("Error checking authentication:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkUserAuth();
  }, [searchParams, router]);

  const handleCodeSubmit = async () => {
    if (!codeSnippet.trim()) return;

    try {
      setIsAnalyzing(true);
      const response = await analyzeCode(codeSnippet);
      setReviewResult(response);
    } catch (error) {
      console.error("Error analyzing code:", error);
      setReviewResult({
        overall_feedback: "An error occurred while analyzing the code.",
        detailed_feedback: ["Please try again later."],
        issues_count: 0,
        prediction: 0,
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Handle logout with confirmation
  const handleLogout = () => {
    if (confirm("Are you sure you want to log out?")) {
      logout();
      setUser(null);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <div className="h-10 w-10 mx-auto mb-4 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
          <p className="text-lg font-medium">Loading application...</p>
        </div>
      </div>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center p-6 bg-gray-100">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">
        AI Code Review Platform 🚀
      </h1>

      {user ? (
        <div className="w-full max-w-4xl">
          <div className="flex items-center mb-6 justify-between">
            <div className="flex items-center">
              {user.picture && (
                <img
                  src={user.picture}
                  alt="Profile"
                  className="w-10 h-10 rounded-full shadow-md mr-3"
                  onError={(e) => {
                    e.currentTarget.style.display = "none";
                  }}
                />
              )}
              <p className="text-lg text-gray-800">
                Welcome, {user.name || "User"}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-500 text-white rounded-lg shadow-md hover:bg-red-600"
            >
              Logout
            </button>
          </div>

          {/* Code Review Form */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Code Analyzer</h2>
            <textarea
              className="w-full p-3 border rounded-lg shadow-sm font-mono text-sm h-64 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 focus:outline-none"
              placeholder="Paste your code snippet here..."
              value={codeSnippet}
              onChange={(e) => setCodeSnippet(e.target.value)}
            ></textarea>
            <button
              onClick={handleCodeSubmit}
              disabled={isAnalyzing || !codeSnippet.trim()}
              className={`mt-4 w-full px-4 py-2 rounded-lg shadow-md text-white ${
                isAnalyzing || !codeSnippet.trim()
                  ? "bg-blue-400 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {isAnalyzing ? "Analyzing..." : "Analyze Code"}
            </button>
          </div>

          {/* Review Results */}
          {reviewResult && (
            <div className="mt-6 bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>

              <div className="mb-4">
                <h3 className="text-lg font-medium mb-2">Overall Feedback</h3>
                <div className="p-4 bg-gray-100 rounded-lg">
                  <p>{reviewResult.overall_feedback}</p>
                </div>
              </div>

              <div className="mb-4">
                <h3 className="text-lg font-medium mb-2">
                  Issues Found: {reviewResult.issues_count}
                </h3>
                <div className="p-4 bg-gray-100 rounded-lg">
                  <ul className="list-disc pl-5 space-y-2">
                    {reviewResult.detailed_feedback.map(
                      (feedback: string, index: number) => (
                        <li key={index}>{feedback}</li>
                      )
                    )}
                  </ul>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-2">Quality Score</h3>
                <div className="flex items-center">
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div
                      className={`h-4 rounded-full ${
                        reviewResult.prediction > 0.7
                          ? "bg-green-500"
                          : reviewResult.prediction > 0.4
                          ? "bg-yellow-500"
                          : "bg-red-500"
                      }`}
                      style={{ width: `${reviewResult.prediction * 100}%` }}
                    ></div>
                  </div>
                  <span className="ml-3 font-medium">
                    {Math.round(reviewResult.prediction * 100)}%
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md p-8 text-center max-w-md w-full">
          <h2 className="text-2xl font-semibold mb-6">Get Started</h2>
          <p className="mb-6 text-gray-600">
            Sign in with your GitHub account to use our AI-powered code review
            platform.
          </p>
          <button
            onClick={loginWithGitHub}
            className="px-6 py-3 bg-black text-white rounded-lg shadow-md hover:bg-gray-800 flex items-center justify-center w-full"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                fillRule="evenodd"
                d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                clipRule="evenodd"
              />
            </svg>
            Sign in with GitHub
          </button>
        </div>
      )}
    </main>
  );
}

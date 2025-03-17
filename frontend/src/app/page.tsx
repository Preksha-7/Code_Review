"use client";

import { loginWithGitHub, logout, getUser } from "@/utils/auth";
import { analyzeCode } from "@/utils/api";
import { useState, useEffect } from "react";

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [codeSnippet, setCodeSnippet] = useState("");
  const [reviewResult, setReviewResult] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  useEffect(() => {
    // Check for user on component mount
    const currentUser = getUser();
    setUser(currentUser);
    setIsLoading(false);
  }, []);

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

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent"></div>
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
              <img
                src={user.picture}
                alt="Profile"
                className="w-10 h-10 rounded-full shadow-md mr-3"
              />
              <p className="text-lg text-gray-800">Welcome, {user.name}</p>
            </div>
            <button
              onClick={logout}
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

            {reviewResult && (
              <div className="mt-6 p-4 bg-gray-50 border rounded-lg">
                <h3 className="text-lg font-bold mb-2">AI Feedback:</h3>
                <div className="py-2 px-3 bg-blue-50 border-l-4 border-blue-500 mb-3">
                  <p className="font-medium">{reviewResult.overall_feedback}</p>
                </div>

                <h4 className="text-md font-semibold mb-2">
                  Detailed Analysis:
                </h4>
                <ul className="list-disc pl-5 space-y-1">
                  {reviewResult.detailed_feedback.map(
                    (feedback: string, index: number) => (
                      <li key={index} className="text-gray-700">
                        {feedback}
                      </li>
                    )
                  )}
                </ul>

                <div className="mt-4 flex items-center">
                  <div className="text-sm font-medium mr-2">Quality Score:</div>
                  <div
                    className={`py-1 px-3 rounded-full text-white text-sm ${
                      reviewResult.prediction > 0.7
                        ? "bg-green-500"
                        : reviewResult.prediction > 0.4
                        ? "bg-yellow-500"
                        : "bg-red-500"
                    }`}
                  >
                    {Math.round(reviewResult.prediction * 100)}%
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center bg-white p-10 rounded-lg shadow-lg">
          <h2 className="text-2xl font-bold mb-6">Get Started</h2>
          <p className="text-gray-600 mb-6 text-center">
            Sign in with GitHub to access the AI code review platform
          </p>
          <button
            onClick={loginWithGitHub}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 flex items-center"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 0C4.477 0 0 4.477 0 10c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.342-3.369-1.342-.454-1.155-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.272.098-2.65 0 0 .84-.269 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.699 1.028 1.592 1.028 2.683 0 3.841-2.337 4.687-4.565 4.934.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C17.14 18.163 20 14.418 20 10c0-5.523-4.477-10-10-10z"
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

"use client";

import { loginWithGitHub, logout, getUser } from "@/utils/auth";
import { analyzeCode } from "@/utils/api";
import { useState, useEffect } from "react";

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [codeSnippet, setCodeSnippet] = useState("");
  const [reviewResult, setReviewResult] = useState("");

  useEffect(() => {
    setUser(getUser());
  }, []);

  const handleCodeSubmit = async () => {
    if (!codeSnippet.trim()) return;
    const response = await analyzeCode(codeSnippet);
    setReviewResult(response.feedback || "No feedback received.");
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-gray-800">
        AI Code Review Platform 🚀
      </h1>

      {user ? (
        <div className="mt-6 flex flex-col items-center">
          <img
            src={user.picture}
            alt="Profile"
            className="w-16 h-16 rounded-full shadow-md"
          />
          <p className="text-lg text-gray-800 mt-2">Welcome, {user.name}!</p>
          <button
            onClick={logout}
            className="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg shadow-md hover:bg-red-600"
          >
            Logout
          </button>

          {/* Code Review Form */}
          <div className="mt-6 w-full max-w-lg">
            <textarea
              className="w-full p-3 border rounded-lg shadow-sm"
              rows={5}
              placeholder="Paste your code snippet here..."
              value={codeSnippet}
              onChange={(e) => setCodeSnippet(e.target.value)}
            ></textarea>
            <button
              onClick={handleCodeSubmit}
              className="mt-4 w-full bg-blue-600 text-white px-4 py-2 rounded-lg shadow-md hover:bg-blue-700"
            >
              Analyze Code
            </button>

            {reviewResult && (
              <div className="mt-4 p-4 bg-gray-200 border rounded-lg">
                <h3 className="text-lg font-bold">AI Feedback:</h3>
                <p className="mt-2 text-gray-700">{reviewResult}</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <button
          onClick={loginWithGitHub}
          className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700"
        >
          Sign in with GitHub
        </button>
      )}
    </main>
  );
}

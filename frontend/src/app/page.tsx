"use client";

import { loginWithGitHub } from "@/utils/auth";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-gray-800">
        AI Code Review Platform 🚀
      </h1>
      <p className="text-lg text-gray-600 mt-4">
        Sign in with GitHub to start reviewing your code.
      </p>
      <button
        onClick={loginWithGitHub}
        className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700"
      >
        Sign in with GitHub
      </button>
    </main>
  );
}

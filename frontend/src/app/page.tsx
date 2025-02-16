export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-gray-100 p-6">
      <h1 className="text-3xl font-bold text-gray-800">
        AI Code Review Platform 🚀
      </h1>
      <p className="text-lg text-gray-600 mt-4">
        Sign in with GitHub to start reviewing your code.
      </p>
      <a
        href="http://127.0.0.1:8000/auth/github"
        className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700"
      >
        Sign in with GitHub
      </a>
    </main>
  );
}

"use client";

import { loginWithGitHub, logout, getUser } from "@/utils/auth";
import { analyzeCode, getSupportedLanguages } from "@/utils/api";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

interface Language {
  id: string;
  name: string;
  description: string;
}

interface FixSuggestions {
  syntax_fixes: string[];
  logic_fixes: string[];
  quality_fixes: string[];
}

interface ReviewResult {
  prediction: number;
  overall_feedback: string;
  detailed_feedback: string[];
  issues_count: number;
  syntax_errors: string[];
  logic_errors: string[];
  code_quality_issues?: string[];
  fix_suggestions?: FixSuggestions;
}

export default function Home() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [codeSnippet, setCodeSnippet] = useState("");
  const [reviewResult, setReviewResult] = useState<ReviewResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("python");
  const [languages, setLanguages] = useState<Language[]>([]);
  const [languagesLoading, setLanguagesLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  useEffect(() => {
    const checkUserAuth = () => {
      try {
        const currentUser = getUser();
        setUser(currentUser);
      } catch (error) {
        console.error("Error checking authentication:", error);
      } finally {
        setIsLoading(false);
      }
    };

    checkUserAuth();

    const loadLanguages = async () => {
      try {
        setLanguagesLoading(true);
        const data = await getSupportedLanguages();
        setLanguages(data.languages || []);
      } catch (error) {
        console.error("Error loading languages:", error);
        setLanguages([
          { id: "python", name: "Python", description: "Python 3.x" },
        ]);
      } finally {
        setLanguagesLoading(false);
      }
    };

    loadLanguages();
  }, []);

  useEffect(() => {
    const handleAuthCallback = () => {
      const urlParams = new URLSearchParams(window.location.search);
      const authStatus = urlParams.get("auth");
      const token = urlParams.get("token");
      const name = urlParams.get("name");
      const email = urlParams.get("email");
      const picture = urlParams.get("picture");

      if (authStatus === "success" && token) {
        const userData = { name, email, picture };
        localStorage.setItem("user", JSON.stringify(userData));
        localStorage.setItem("authToken", token);
        window.history.replaceState({}, document.title, "/");
        window.location.reload();
      }
    };

    handleAuthCallback();
  }, []);

  const handleCodeSubmit = async () => {
    if (!codeSnippet.trim()) return;

    try {
      setIsAnalyzing(true);
      setAnalysisError(null);
      const response = await analyzeCode(codeSnippet, selectedLanguage);
      setReviewResult(response);
    } catch (error) {
      console.error("Error analyzing code:", error);
      setAnalysisError(
        "An error occurred while analyzing the code. Please try again later."
      );
      setReviewResult(null);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleLogout = () => {
    if (confirm("Are you sure you want to log out?")) {
      logout();
      setUser(null);
    }
  };

  const qualityScoreColor = (score: number) => {
    if (score >= 0.7) return "text-green-600";
    if (score >= 0.4) return "text-yellow-600";
    return "text-red-600";
  };

  const renderQualityBar = (score: number) => {
    let barColor = "bg-red-500";
    if (score >= 0.7) barColor = "bg-green-500";
    else if (score >= 0.4) barColor = "bg-yellow-500";

    return (
      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
        <div
          className={`${barColor} h-2.5 rounded-full`}
          style={{ width: `${Math.round(score * 100)}%` }}
        ></div>
      </div>
    );
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
        Python Code Bug Hunter 🐍🔍
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

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Python Code Analyzer</h2>
            <p className="text-gray-600 mb-4">
              Using PyBugHunt for intelligent code analysis and bug detection
            </p>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Select Programming Language
              </label>
              <select
                className="w-full p-2 border rounded-lg shadow-sm"
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                disabled={languagesLoading || languages.length <= 1}
              >
                {languagesLoading ? (
                  <option value="">Loading...</option>
                ) : (
                  languages.map((lang) => (
                    <option key={lang.id} value={lang.id}>
                      {lang.name} - {lang.description}
                    </option>
                  ))
                )}
              </select>
              {selectedLanguage !== "python" && (
                <p className="text-yellow-600 text-sm mt-1">
                  Currently only Python analysis is fully supported by PyBugHunt
                </p>
              )}
            </div>

            <textarea
              className="w-full p-3 border rounded-lg font-mono text-sm h-64"
              placeholder="Paste your Python code snippet here..."
              value={codeSnippet}
              onChange={(e) => setCodeSnippet(e.target.value)}
            ></textarea>

            <button
              onClick={handleCodeSubmit}
              disabled={isAnalyzing || !codeSnippet.trim()}
              className={`w-full mt-4 px-4 py-2 rounded-lg shadow-md text-white ${
                isAnalyzing || !codeSnippet.trim()
                  ? "bg-blue-400 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {isAnalyzing ? "Analyzing with PyBugHunt..." : "Analyze Code"}
            </button>
          </div>

          {analysisError && (
            <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
              {analysisError}
            </div>
          )}

          {reviewResult && (
            <div className="mt-6 bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">
                PyBugHunt Analysis Results
              </h2>

              <div className="mb-6">
                <h3 className="text-lg font-medium mb-2">Quality Score</h3>
                <div className="flex items-center">
                  <div className="flex-1 mr-4">
                    {renderQualityBar(reviewResult.prediction)}
                  </div>
                  <span
                    className={`text-lg font-bold ${qualityScoreColor(
                      reviewResult.prediction
                    )}`}
                  >
                    {Math.round(reviewResult.prediction * 100)}%
                  </span>
                </div>
              </div>

              <div className="mb-6">
                <h3 className="text-lg font-medium mb-2">Overall Feedback</h3>
                <div className="p-4 bg-gray-100 rounded-lg">
                  <p>{reviewResult.overall_feedback}</p>
                </div>
              </div>

              {/* Syntax Errors */}
              {reviewResult.syntax_errors?.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-red-600 mb-2">
                    Syntax Errors: {reviewResult.syntax_errors.length}
                  </h3>
                  <ul className="list-disc pl-5 space-y-2 bg-red-50 p-4 rounded-lg border border-red-200">
                    {reviewResult.syntax_errors.map((err, i) => (
                      <li key={`se-${i}`} className="text-red-700">
                        {err}
                      </li>
                    ))}
                  </ul>

                  {reviewResult.fix_suggestions &&
                    reviewResult.fix_suggestions.syntax_fixes &&
                    reviewResult.fix_suggestions.syntax_fixes.length > 0 && (
                      <div className="mt-2 p-4 bg-green-50 border border-green-200 rounded-lg">
                        <h4 className="font-medium text-green-700 mb-2">
                          Fix Suggestions:
                        </h4>
                        <ul className="list-disc pl-5 space-y-1">
                          {reviewResult.fix_suggestions.syntax_fixes.map(
                            (fix, i) => (
                              <li key={`sf-${i}`} className="text-green-800">
                                {fix}
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    )}
                </div>
              )}

              {/* Logic Errors */}
              {reviewResult.logic_errors?.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-medium text-yellow-600 mb-2">
                    Logic Errors: {reviewResult.logic_errors.length}
                  </h3>
                  <ul className="list-disc pl-5 space-y-2 bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                    {reviewResult.logic_errors.map((err, i) => (
                      <li key={`le-${i}`} className="text-yellow-700">
                        {err}
                      </li>
                    ))}
                  </ul>

                  {reviewResult.fix_suggestions &&
                    reviewResult.fix_suggestions.logic_fixes &&
                    reviewResult.fix_suggestions.logic_fixes.length > 0 && (
                      <div className="mt-2 p-4 bg-green-50 border border-green-200 rounded-lg">
                        <h4 className="font-medium text-green-700 mb-2">
                          Fix Suggestions:
                        </h4>
                        <ul className="list-disc pl-5 space-y-1">
                          {reviewResult.fix_suggestions.logic_fixes.map(
                            (fix, i) => (
                              <li key={`lf-${i}`} className="text-green-800">
                                {fix}
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    )}
                </div>
              )}

              {/* Code Quality Issues */}
              {reviewResult.code_quality_issues &&
                reviewResult.code_quality_issues.length > 0 && (
                  <div className="mb-6">
                    <h3 className="text-lg font-medium text-purple-600 mb-2">
                      Code Quality Issues:{" "}
                      {reviewResult.code_quality_issues.length}
                    </h3>
                    <ul className="list-disc pl-5 space-y-2 bg-purple-50 p-4 rounded-lg border border-purple-200">
                      {reviewResult.code_quality_issues.map((issue, i) => (
                        <li key={`cq-${i}`} className="text-purple-700">
                          {issue}
                        </li>
                      ))}
                    </ul>

                    {reviewResult.fix_suggestions &&
                      reviewResult.fix_suggestions.quality_fixes &&
                      reviewResult.fix_suggestions.quality_fixes.length > 0 && (
                        <div className="mt-2 p-4 bg-green-50 border border-green-200 rounded-lg">
                          <h4 className="font-medium text-green-700 mb-2">
                            Fix Suggestions:
                          </h4>
                          <ul className="list-disc pl-5 space-y-1">
                            {reviewResult.fix_suggestions.quality_fixes.map(
                              (fix, i) => (
                                <li key={`qf-${i}`} className="text-green-800">
                                  {fix}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                  </div>
                )}
              {/* Issue Summary */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="text-lg font-medium text-blue-700 mb-2">
                  Issue Summary
                </h3>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                    <span className="text-red-600 font-bold text-xl block">
                      {reviewResult.syntax_errors?.length || 0}
                    </span>
                    <span className="text-gray-600">Syntax Errors</span>
                  </div>
                  <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                    <span className="text-yellow-600 font-bold text-xl block">
                      {reviewResult.logic_errors?.length || 0}
                    </span>
                    <span className="text-gray-600">Logic Errors</span>
                  </div>
                  <div className="text-center p-3 bg-white rounded-lg shadow-sm">
                    <span className="text-purple-600 font-bold text-xl block">
                      {reviewResult.code_quality_issues?.length || 0}
                    </span>
                    <span className="text-gray-600">Quality Issues</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center">
          <p className="mb-4 text-lg">
            Sign in to use the PyBugHunt code analyzer
          </p>
          <button
            onClick={loginWithGitHub}
            className="px-6 py-3 bg-black text-white rounded-lg shadow-md hover:bg-gray-800"
          >
            Login with GitHub
          </button>
        </div>
      )}
    </main>
  );
}

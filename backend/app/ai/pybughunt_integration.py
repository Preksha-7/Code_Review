from pybughunt import CodeErrorDetector

def analyze_user_code(code: str):
    detector = CodeErrorDetector()
    results = detector.analyze(code)

    suggestions = {}
    if results["syntax_errors"] or results["logic_errors"]:
        suggestions = detector.fix_suggestions(code, results)

    return {
        "syntax_errors": results["syntax_errors"],
        "logic_errors": results["logic_errors"],
        "fix_suggestions": suggestions
    }

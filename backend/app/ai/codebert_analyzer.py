from transformers import AutoTokenizer, RobertaForSequenceClassification
import torch
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the model with error handling
try:
    # Load the CodeBERT model once at startup
    MODEL_NAME = "microsoft/codebert-base"
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    model.eval()  # Set to evaluation mode
    logger.info("CodeBERT model loaded successfully")
except Exception as e:
    logger.error(f"Error loading CodeBERT model: {str(e)}")
    model = None
    tokenizer = None

def analyze_code(code_snippet: str) -> dict:
    """Analyzes the given code snippet using CodeBERT and additional heuristics."""
    
    if not model or not tokenizer:
        logger.error("CodeBERT model not initialized correctly")
        return {
            "prediction": 0.0,
            "overall_feedback": "Model initialization error. Using basic analysis only.",
            "detailed_feedback": ["Server configuration issue. Using basic analysis."],
            "issues_count": 1
        }
    
    try:
        # Basic code analysis using CodeBERT
        inputs = tokenizer(code_snippet, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            prediction_score = torch.softmax(logits, dim=1)[0][1].item()  # Probability of "good code"
    except Exception as e:
        logger.error(f"Error in model prediction: {str(e)}")
        prediction_score = 0.5  # Neutral score in case of error
    
    # Additional heuristic analysis
    feedback = []
    issues_found = 0
    
    # Check for common Python issues
    if "import" not in code_snippet and len(code_snippet) > 100:
        feedback.append("Consider adding necessary imports.")
        issues_found += 1
    
    if "  " in code_snippet:  # Double spaces
        feedback.append("Inconsistent spacing detected.")
        issues_found += 1
    
    if re.search(r'[\w\.]+\s+=\s+\[\s*\]', code_snippet):  # Empty list initialization
        feedback.append("Empty lists detected. Ensure they're properly populated later.")
        issues_found += 1
    
    if re.search(r'print\((?!.*[\'"].*)[^)]*\)', code_snippet):  # Print without descriptive string
        feedback.append("Consider adding descriptive labels to print statements.")
        issues_found += 1
    
    # Check indentation and braces
    if code_snippet.count('{') != code_snippet.count('}'):
        feedback.append("Mismatched braces detected.")
        issues_found += 1
    
    if "try:" in code_snippet and "except:" not in code_snippet:
        feedback.append("Try block without corresponding except block.")
        issues_found += 1
    
    # Check for common Python code smells
    if re.search(r'except:\s*pass', code_snippet):
        feedback.append("Avoid using empty except blocks (except: pass). Handle exceptions properly.")
        issues_found += 1
    
    if re.search(r'except Exception as e:', code_snippet) and "logger" not in code_snippet:
        feedback.append("Consider adding logging when catching exceptions.")
        issues_found += 1
    
    # Check for hardcoded values
    if re.search(r'(password|secret|api_key|token)\s*=\s*[\'"](.*?)[\'"]', code_snippet, re.IGNORECASE):
        feedback.append("Hardcoded secrets detected. Consider using environment variables.")
        issues_found += 1
    
    # Generate overall feedback
    if prediction_score < 0.4 or issues_found > 2:
        overall = "Significant issues detected. Review recommended."
    elif prediction_score < 0.7 or issues_found > 0:
        overall = "Minor issues found. Consider the suggestions below."
    else:
        overall = "Code looks good! No major issues detected."
    
    if not feedback:
        feedback.append("No specific issues detected.")
    
    return {
        "prediction": prediction_score,
        "overall_feedback": overall,
        "detailed_feedback": feedback,
        "issues_count": issues_found
    }
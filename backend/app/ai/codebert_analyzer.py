from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers import RobertaForSequenceClassification
import torch

# Load the CodeBERT model once at startup
MODEL_NAME = "microsoft/codebert-base"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
model.eval()  # Set to evaluation mode

def analyze_code(code_snippet: str) -> dict:
    """Analyzes the given code snippet using CodeBERT."""
    inputs = tokenizer(code_snippet, return_tensors="pt", padding=True, truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1).item()

    feedback = "Code looks good!" if predictions == 1 else "Potential issues found. Review suggested."
    
    return {"prediction": predictions, "feedback": feedback}

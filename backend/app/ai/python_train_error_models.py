import os
import sys
import argparse
import logging
from python_dataset_loader import CodeNetPyLoader
from python_error_detector import train_error_detection_model

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Main function to train Python error detection models
    """
    parser = argparse.ArgumentParser(description='Train Python error detection models')
    parser.add_argument('--dataset', type=str, required=True, 
                        help='Path to the CodeNetPy dataset')
    parser.add_argument('--max_samples', type=int, default=None,
                       help='Maximum number of samples to use for training')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory for models')
    args = parser.parse_args()
    
    # Validate dataset path
    if not os.path.exists(args.dataset):
        logger.error(f"Dataset path does not exist: {args.dataset}")
        return 1
    
    # If output specified, ensure it exists
    if args.output:
        os.makedirs(args.output, exist_ok=True)
        # Set environment variable for model dir
        os.environ['MODEL_DIR'] = args.output
    
    logger.info(f"Loading dataset from {args.dataset}")
    loader = CodeNetPyLoader(args.dataset)
    
    # Load code pairs from dataset
    train_data = loader.get_training_data()
    
    if train_data["count"] == 0:
        logger.error("No training examples found in dataset")
        return 1
    
    logger.info(f"Loaded {train_data['count']} training examples")
    
    # Limit samples if specified
    if args.max_samples and args.max_samples < train_data["count"]:
        logger.info(f"Using {args.max_samples} out of {train_data['count']} examples")
        buggy_code = train_data["buggy_code"][:args.max_samples]
        fixed_code = train_data["fixed_code"][:args.max_samples]
        error_messages = train_data["error_messages"][:args.max_samples]
    else:
        buggy_code = train_data["buggy_code"]
        fixed_code = train_data["fixed_code"]
        error_messages = train_data["error_messages"]
    
    # Train error detection models
    logger.info("Training error detection models...")
    result = train_error_detection_model(buggy_code, fixed_code, error_messages)
    
    if result["success"]:
        logger.info("Training completed successfully!")
        logger.info(f"Error detector accuracy: {result.get('detector_accuracy', 'N/A')}")
        logger.info(f"Error classifier trained: {result.get('classifier_trained', False)}")
        return 0
    else:
        logger.error(f"Training failed: {result.get('message', 'Unknown error')}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
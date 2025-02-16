import os
import sys
from datetime import datetime
from pipeline_steps.step1_extract import extract_text_step
from pipeline_steps.step2_analyze import analyze_text_step
from pipeline_steps.step3_evidence import gather_evidence_step
from pipeline_steps.step4_validate import validate_evidence_step
from pipeline_steps.step5_report import generate_report_step
from pipeline_steps.step6_pdf import create_pdf_step
import json

def process_personal_statement(input_pdf_path):
    """
    Process a single personal statement PDF through the evidence gathering pipeline.
    Each step is handled by a separate module and saves its state to the output directory.
    State is saved after each step to allow for debugging and rerunning from checkpoints.
    
    Args:
        input_pdf_path (str): Path to the input personal statement PDF
        
    Returns:
        tuple: (success: bool, output_dir: str, error_message: str or None)
    """
    # Create output directory named with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("output", f"statement_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Step 1: Extract text from PDF
        raw_text, step1_state = extract_text_step(input_pdf_path)
        save_state(step1_state, output_dir, "step1_extract")
        if not raw_text:
            raise Exception("Failed to extract text from PDF")

        # Step 2: Analyze text and extract claims
        claims, step2_state = analyze_text_step(raw_text)
        save_state(step2_state, output_dir, "step2_analyze")
        if not claims:
            raise Exception("No claims identified in text")

        # Step 3: Gather evidence for claims
        evidence, step3_state = gather_evidence_step(claims)
        save_state(step3_state, output_dir, "step3_evidence")

        # Step 4: Validate and rank evidence
        validated_evidence, step4_state = validate_evidence_step(evidence)
        save_state(step4_state, output_dir, "step4_validate")

        # Step 5: Generate report text
        report_text, step5_state = generate_report_step(claims, validated_evidence)
        save_state(step5_state, output_dir, "step5_report")

        # Step 6: Create final PDF
        output_pdf, step6_state = create_pdf_step(report_text)
        save_state(step6_state, output_dir, "step6_pdf")

        print(f"Processing complete. All outputs saved to {output_dir}")
        print(f"Final report saved as {output_pdf}")
        return True, output_dir, None

    except Exception as e:
        error_message = f"Error processing personal statement: {str(e)}"
        print(error_message)
        return False, output_dir, error_message

def save_state(state_dict, output_dir, step_name):
    """
    Save the state of a pipeline step to JSON for debugging and rerunning.
    
    Args:
        state_dict (dict): State data to save
        output_dir (str): Directory to save state file
        step_name (str): Name of the pipeline step
    """
    state_file = os.path.join(output_dir, f"{step_name}_state.json")
    with open(state_file, 'w') as f:
        json.dump(state_dict, f, indent=2)

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_personal_statement.pdf>")
        sys.exit(1)
        
    input_pdf = sys.argv[1]
    if not os.path.exists(input_pdf):
        print(f"Error: File {input_pdf} not found")
        sys.exit(1)
        
    process_personal_statement(input_pdf)

if __name__ == "__main__":
    main()



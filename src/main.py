import os
import sys
from datetime import datetime

from pipeline_steps.step1_pdf_processor import extract_text_from_pdf, create_formatted_pdf
from pipeline_steps.step2_extract_claims import extract_claims_combined
from pipeline_steps.step3_evidence_gather import gather_evidence_for_claim
from pipeline_steps.step4_evidence_validator import validate_and_rank_evidence
from pipeline_steps.step5_report_generator import generate_evidence_report

import json

# Load API keys from .env file
from dotenv import load_dotenv

def process_personal_statement(input_pdf_path, continue_from=None, checkpoint_dir=None):
    """
    Process a single personal statement PDF through the evidence gathering pipeline.
    Each step is handled by a separate module and saves its state to the output directory.
    State is saved after each step to allow for debugging and rerunning from checkpoints.
    
    Args:
        input_pdf_path (str): Path to the input personal statement PDF
        
    Returns:
        tuple: (success: bool, output_dir: str, error_message: str or None)
    """
    # Create output directory 
    filename_no_ext = input_pdf_path.split("/")[-1].split(".")[0]
    output_dir = os.path.join("../output/", filename_no_ext)
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Extract text from PDF
    if not os.path.exists(os.path.join(output_dir, "step1_raw_text_state.json")):
        raw_text = extract_text_from_pdf(input_pdf_path)
        step1_state = {"raw_text": raw_text}
        save_state(step1_state, output_dir, "step1_extract_raw_text")
        if not raw_text:
            raise Exception("Failed to extract text from PDF")
    else:
        print(f"Resuming from step 1: {output_dir}")
        with open(os.path.join(output_dir, "step1_raw_text_state.json"), "r") as f:
            step1_state = json.load(f)
            raw_text = step1_state["raw_text"]

    # Step 2: Analyze text and extract claims
    if not os.path.exists(os.path.join(output_dir, "step2_v2_extract_claims_state.json")):
        claims = extract_claims_combined(raw_text)
        step2_state = {"claims": claims}
        save_state(step2_state, output_dir, "step2_v2_extract_claims")
        if not claims:
            raise Exception("No claims identified in text")
    else:
        print(f"Resuming from step 2: {output_dir}")
        with open(os.path.join(output_dir, "step2_v2_extract_claims_state.json"), "r") as f:
            step2_state = json.load(f)
            claims = step2_state["claims"]

    # Step 3: Gather evidence for claims
    if not os.path.exists(os.path.join(output_dir, "step3_evidence_state.json")):
        evidence = gather_evidence_for_claim(claims)
        step3_state = {"evidence": evidence}
        save_state(step3_state, output_dir, "step3_evidence")
        if not evidence:
            raise Exception("No evidence found for claims")
    else:
        print(f"Resuming from step 3: {output_dir}")
        with open(os.path.join(output_dir, "step3_evidence_state.json"), "r") as f:
            step3_state = json.load(f)
            evidence = step3_state["evidence"]

    # Step 4: Validate and rank evidence
    if not os.path.exists(os.path.join(output_dir, "step4_validate_state.json")):
        validated_evidence = validate_and_rank_evidence(evidence)
        step4_state = {"validated_evidence": validated_evidence}
        save_state(step4_state, output_dir, "step4_validate")
        if not validated_evidence:
            raise Exception("No validated evidence found")
    else:
        print(f"Resuming from step 4: {output_dir}")
        with open(os.path.join(output_dir, "step4_validate_state.json"), "r") as f:
            step4_state = json.load(f)
            validated_evidence = step4_state["validated_evidence"]

    # Step 5: Generate report text
    if not os.path.exists(os.path.join(output_dir, "step5_report_state.json")):
        report_text = generate_evidence_report(claims, validated_evidence)
        step5_state = {"report_text": report_text}
        save_state(step5_state, output_dir, "step5_report")
        if not report_text:
            raise Exception("Failed to generate report text")
    else:
        print(f"Resuming from step 5: {output_dir}")
        with open(os.path.join(output_dir, "step5_report_state.json"), "r") as f:
            step5_state = json.load(f)
            report_text = step5_state["report_text"]
    
    # Step 6: Create final PDF  
    if not os.path.exists(os.path.join(output_dir, "step6_pdf_state.json")):
        output_pdf = create_formatted_pdf(report_text)
        step6_state = {"output_pdf": output_pdf}
        save_state(step6_state, output_dir, "step6_pdf")
        if not output_pdf:
            raise Exception("Failed to create final PDF")
    else:
        print(f"Resuming from step 6: {output_dir}")
        with open(os.path.join(output_dir, "step6_pdf_state.json"), "r") as f:
            step6_state = json.load(f)
            output_pdf = step6_state["output_pdf"]

    print(f"Processing complete. All outputs saved to {output_dir}")
    print(f"Final report saved as {output_pdf}")
    return True, output_dir, None

    # except Exception as e:
    #     error_message = f"Error processing personal statement: {str(e)}"
    #     print(error_message)
    #     return False, output_dir, error_message

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
        print("Usage: python main.py <path_to_personal_statement.pdf> [--continue-from <step_name>] [--checkpoint-dir <dir>]")
        # print("\nOptional arguments:")
        # print("  --continue-from    Continue pipeline from a specific step (step1_extract, step2_analyze, etc)")
        # print("  --checkpoint-dir   Directory containing checkpoint files to resume from")
        sys.exit(1)
        
    input_pdf = sys.argv[1]
    if not os.path.exists(input_pdf):
        print(f"Error: File {input_pdf} not found")
        sys.exit(1)

    # continue_from = None
    # checkpoint_dir = None
    # for arg in sys.argv[2:]:
    #     if arg.startswith("--continue-from="):
    #         continue_from = arg.split("=")[1]
    #     elif arg.startswith("--checkpoint-dir="):
    #         checkpoint_dir = arg.split("=")[1]

    # Load environment variables from .env file in root directory
    load_dotenv()
    process_personal_statement(input_pdf) #, continue_from, checkpoint_dir)

if __name__ == "__main__":
    main()



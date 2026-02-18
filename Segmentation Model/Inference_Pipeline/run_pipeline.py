import subprocess
import argparse
import os
import sys
import shutil
import json

def run_pipeline():
    # =====================================================
    # ARGUMENT PARSING
    # =====================================================
    parser = argparse.ArgumentParser(description='Run the full MRI to 3D model pipeline.')
    parser.add_argument('--input', type=str, required=True, help='Path to the input MRI (.nii) file.')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory to save the final .glb files.')
    args = parser.parse_args()

    # The scripts need to be run from their own directory to find models and other files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # =====================================================
    # STEP 1: INFER SEGMENTATION
    # =====================================================
    print("[PIPELINE] Running segmentation...")
    infer_script_path = os.path.join(script_dir, 'infer_segmentation.py')
    
    # We need to capture stdout to get the JSON metrics
    process = subprocess.run(
        [sys.executable, infer_script_path, '--flair', args.input],
        cwd=script_dir,
        capture_output=True,
        text=True
    )

    if process.returncode != 0:
        print(f"[ERROR] infer_segmentation.py failed with return code {process.returncode}")
        print(process.stderr)
        sys.exit(1)

    print("[PIPELINE] Segmentation finished.")
    
    # Extract JSON from the script's output
    stdout_str = process.stdout
    try:
        json_output_str = stdout_str.split("JSON_START")[1].split("JSON_END")[0]
        metrics = json.loads(json_output_str)
    except (IndexError, json.JSONDecodeError) as e:
        print(f"[WARNING] Could not parse JSON metrics from segmentation script output: {e}")
        metrics = {}


    # =====================================================
    # STEP 2: MASK TO MESH
    # =====================================================
    print("[PIPELINE] Running mesh generation...")
    mesh_script_path = os.path.join(script_dir, 'mask_to_mesh.py')
    process = subprocess.run(
        [sys.executable, mesh_script_path],
        cwd=script_dir,
        capture_output=True,
        text=True
    )

    if process.returncode != 0:
        print(f"[ERROR] mask_to_mesh.py failed with return code {process.returncode}")
        print(process.stderr)
        sys.exit(1)
        
    print("[PIPELINE] Mesh generation finished.")

    # =====================================================
    # STEP 3: MOVE & CLEANUP
    # =====================================================
    generated_files = []
    output_files = {}

    for filename in ["tumor.glb", "edema.glb", "full_tumor.glb"]:
        src_path = os.path.join(script_dir, filename)
        if os.path.exists(src_path):
            dest_path = os.path.join(args.output_dir, filename)
            shutil.move(src_path, dest_path)
            generated_files.append(filename)
            # Use the filename as key, e.g., "full_tumor"
            output_files[filename.split('.')[0]] = filename 
            print(f"[PIPELINE] Moved {filename} to {args.output_dir}")

    # Cleanup intermediate files
    for temp_file in ["tumor_mask.npy", "tumor_probs.npy"]:
        temp_path = os.path.join(script_dir, temp_file)
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"[PIPELINE] Cleaned up {temp_file}")
            
    # =====================================================
    # FINAL OUTPUT
    # =====================================================
    final_output = {
        "metrics": metrics,
        "files": output_files
    }
    
    # Print a final JSON object for Node.js to capture
    print("PIPELINE_JSON_START")
    print(json.dumps(final_output))
    print("PIPELINE_JSON_END")

if __name__ == '__main__':
    run_pipeline()

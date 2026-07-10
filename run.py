import sys
import subprocess
import os

def run_command(command, cwd=None):
    print(f"Running: {' '.join(command)} (cwd: {cwd or '.'})")
    try:
        use_shell = os.name == 'nt'
        result = subprocess.run(command, cwd=cwd, check=True, text=True, shell=use_shell)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False

def show_help():
    print("""
Product Attribute Extraction Pipeline orchestrator.

Usage:
  python run.py [command]

Commands:
  prepare        Generate labeled dataset with 60 examples from raw definitions
  train          Train the custom SpaCy NER model on the generated dataset
  evaluate       Run model evaluation on the test split and generate metrics
  build-frontend Build the React dashboard static assets for production
  serve          Start the FastAPI backend server (which also serves the dashboard)
  all            Run prepare, train, evaluate, and build-frontend in sequence
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    
    if cmd == "prepare":
        run_command([sys.executable, "data/prepare_dataset.py"])
    elif cmd == "train":
        run_command([sys.executable, "model/train.py"])
    elif cmd == "evaluate":
        run_command([sys.executable, "model/evaluate.py"])
    elif cmd == "build-frontend":
        # Make sure node_modules exist, if not run npm install
        if not os.path.exists("frontend/node_modules"):
            print("node_modules not found in frontend directory. Running 'npm install'...")
            run_command(["npm", "install"], cwd="frontend")
        run_command(["npm", "run", "build"], cwd="frontend")
    elif cmd == "serve":
        print("Starting FastAPI Backend at http://localhost:8000")
        print("API endpoints: POST /extract, POST /api/extract")
        # Run uvicorn
        run_command([sys.executable, "-m", "uvicorn", "api.app:app", "--host", "127.0.0.1", "--port", "8000"])
    elif cmd == "all":
        print("Running full pipeline build...")
        steps = [
            (prepare_dataset, [sys.executable, "data/prepare_dataset.py"], "Preparing dataset"),
            (train_model, [sys.executable, "model/train.py"], "Training model"),
            (evaluate_model, [sys.executable, "model/evaluate.py"], "Evaluating model"),
            (build_fe, ["npm", "run", "build"], "Building frontend")
        ]
        
        # Step 1: Prepare
        if not run_command([sys.executable, "data/prepare_dataset.py"]):
            sys.exit(1)
        # Step 2: Train
        if not run_command([sys.executable, "model/train.py"]):
            sys.exit(1)
        # Step 3: Evaluate
        if not run_command([sys.executable, "model/evaluate.py"]):
            sys.exit(1)
        # Step 4: Install dependencies & Build
        if not os.path.exists("frontend/node_modules"):
            run_command(["npm", "install"], cwd="frontend")
        if not run_command(["npm", "run", "build"], cwd="frontend") :
            sys.exit(1)
            
        print("\nAll steps completed successfully!")
        print("To start the server, run: python run.py serve")
    else:
        print(f"Unknown command: {cmd}")
        show_help()
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
ResearchPilot Edge — Main Launcher
Unified CLI entrypoint for launching the UI, running benchmarks, initializing demo data, or checking diagnostics.

Usage:
    python run.py                 # Launch the Streamlit desktop UI
    python run.py --demo          # Initialize demo dataset and start UI
    python run.py --benchmark     # Run automated benchmark suite
    python run.py --diagnostic    # Run Snapdragon & hardware diagnostic check
"""

import sys
import subprocess
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

def main():
    parser = argparse.ArgumentParser(
        description="ResearchPilot Edge — Private AI Research Assistant for Snapdragon PCs"
    )
    parser.add_argument("--demo", action="store_true", help="Pre-load demo research dataset before starting UI")
    parser.add_argument("--benchmark", action="store_true", help="Run automated benchmark suite and exit")
    parser.add_argument("--diagnostic", action="store_true", help="Run hardware & Snapdragon NPU diagnostics and exit")
    parser.add_argument("--port", type=int, default=8501, help="Port to run Streamlit on (default: 8501)")
    args = parser.parse_args()

    if args.diagnostic:
        from scripts.test_snapdragon import main as diag_main
        diag_main()
        return

    if args.benchmark:
        from scripts.benchmark import main as bench_main
        bench_main()
        return

    if args.demo:
        from scripts.setup_demo import main as demo_main
        demo_main()

    # Launch Streamlit Desktop UI
    ui_script = BASE_DIR / "app" / "frontend" / "ui.py"
    print("=" * 70)
    print(" 🔬 Starting ResearchPilot Edge...")
    print(f" Web UI will be accessible at: http://localhost:{args.port}")
    print("=" * 70)

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ui_script),
        f"--server.port={args.port}",
        "--server.headless=false",
        "--theme.base=dark"
    ]

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nResearchPilot Edge closed gracefully.")

if __name__ == "__main__":
    main()

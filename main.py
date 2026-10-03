"""
Ines — The first local AI assistant with controllable internal behavior.
Main application entry point and interactive CLI loop.
"""

import sys
import argparse
from pathlib import Path

# Safe UTF-8 console output for Windows terminals
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core import config, logger, AVAILABLE_STEERING_PRESETS

BANNER = r"""
   _____ _   _ ______  _____ 
  |_   _| \ | |  ____|/ ____|
    | | |  \| | |__  | (___  
    | | | . ` |  __|  \___ \ 
   _| |_| |\  | |____ ____) |
  |_____|_| \_|______|_____/ 
======================================================
 The First Local AI Assistant with Controllable Behavior
======================================================
"""

def print_system_info():
    """Print system configuration and active runtime settings."""
    print(BANNER)
    print(f"Assistant Name     : {config.assistant_name}")
    print(f"Primary Model      : {config.model_name}")
    print(f"Alternate Model    : {config.alternate_model_name}")
    print(f"Target Device      : {config.device}")
    print(f"Quantization       : {config.quantization}")
    print(f"Steering Enabled   : {config.steering_enabled}")
    print(f"Available Presets  : {', '.join(AVAILABLE_STEERING_PRESETS)}")
    print(f"Default Preset     : {config.default_steering_preset} (alpha = {config.default_steering_strength})")
    print(f"PC Automation Safe : {config.safe_delete} (Confirmations: {config.confirmation_required})")
    print("=" * 54)

def check_dependencies() -> bool:
    """Check if ML dependencies (torch, transformers) are installed."""
    try:
        import torch
        import transformers
        return True
    except ImportError as e:
        logger.warning(
            f"Missing required ML runtime: {e}. "
            "To run local model inference and activation steering, please install dependencies: "
            "pip install -r requirements.txt"
        )
        return False

def run_interactive_cli(preset_name: str = "neutral", alpha: float = 1.5, model_name: str = None):
    """Run the interactive terminal chat loop."""
    print(BANNER)
    print("Initializing Ines Cognitive Core...")

    if not check_dependencies():
        print()
        print("[Notice] PyTorch or Transformers is not yet installed in this environment.")
        print("Run 'pip install -r requirements.txt' to enable local inference.")
        print("Core architecture, configs, and steering registry are validated and ready.")
        print()
        return

    from llm import loader, engine
    from steering import SteeringEngine

    target_model = model_name or config.model_name
    print(f"Loading local weights ({target_model}) on {config.device}...")
    loader.load(model_name=target_model)

    # Initialize Steering Engine
    steering = SteeringEngine(loader.model, loader.tokenizer_wrapper, engine)

    # Apply initial preset if specified
    if preset_name != "neutral":
        steering.set_preset(preset_name, alpha)

    print()
    print("=" * 54)
    print("Ines is online! Commands:")
    print("  /steer <preset> [strength] - Change behavioral direction")
    print("  /reset                     - Reset to neutral (unsteered)")
    print("  /compare <prompt>          - Side-by-side steered vs unsteered")
    print("  /status                    - View active steering telemetry")
    print("  /quit                      - Exit")
    print("=" * 54)
    print()

    messages = []

    while True:
        try:
            status = steering.status
            active_info = f"[{status['active_preset']}:{status['active_alpha']}x]"
            user_input = input(f"You {active_info}> ").strip()

            if not user_input:
                continue

            if user_input.lower() in ("/quit", "/exit", "exit", "quit"):
                print("Shutting down Ines. Goodbye!")
                break

            elif user_input.startswith("/steer"):
                parts = user_input.split()
                if len(parts) < 2:
                    print(f"Usage: /steer <preset> [strength] [optional question]. Presets: {', '.join(AVAILABLE_STEERING_PRESETS)}")
                    continue
                p_name = parts[1].lower()
                p_alpha = None
                prompt_start_idx = 2

                if len(parts) > 2:
                    try:
                        p_alpha = float(parts[2])
                        prompt_start_idx = 3
                    except ValueError:
                        # User typed a question right after preset without numeric strength
                        prompt_start_idx = 2

                success = steering.set_preset(p_name, p_alpha)
                if success:
                    print(f"-> Steering set to '{p_name}' (alpha = {steering.status['active_alpha']})")
                else:
                    print(f"-> Preset '{p_name}' could not be activated. Available: {', '.join(AVAILABLE_STEERING_PRESETS)}")
                    continue

                # If the user also included a question in the same line, answer it immediately!
                extra_prompt = " ".join(parts[prompt_start_idx:]).strip()
                if extra_prompt:
                    messages.append({"role": "user", "content": extra_prompt})
                    print(f"\nYou [{p_name}:{steering.status['active_alpha']}x]> {extra_prompt}")
                    print("\nInes: ", end="", flush=True)
                    response = steering.generate_steered(messages)
                    print(response + "\n")
                    messages.append({"role": "assistant", "content": response})

                continue

            elif user_input == "/reset":
                steering.reset()
                print("-> Steering reset to neutral baseline.")
                continue

            elif user_input == "/status":
                st = steering.status
                print(f"Active Preset : {st['active_preset']}")
                print(f"Active Alpha  : {st['active_alpha']}")
                print(f"Hook Active   : {st['hook_active']}")
                print(f"Target Layer  : {st['active_layer']}")
                print(f"Cached Vectors: {st['cached_directions']}")
                continue

            elif user_input.startswith("/compare"):
                prompt_to_compare = user_input[8:].strip()
                if not prompt_to_compare:
                    print("Usage: /compare <your question/prompt>")
                    continue
                compare_preset = steering.status["active_preset"]
                if compare_preset == "neutral":
                    compare_preset = "concise"
                print()
                print(f"Running dual forward pass (Baseline vs '{compare_preset}')...")
                print()
                res = steering.compare(
                    [{"role": "user", "content": prompt_to_compare}],
                    preset_name=compare_preset,
                )
                print(f"--- [1] Baseline (Unsteered) [{res['metrics']['unsteered_tokens']} tokens, {res['metrics']['unsteered_latency_ms']}ms] ---")
                print(res["unsteered"])
                print()
                print(f"--- [2] Steered: {compare_preset} [{res['metrics']['steered_tokens']} tokens ({res['metrics']['token_delta_percentage']}%), {res['metrics']['steered_latency_ms']}ms] ---")
                print(res["steered"])
                print("-" * 54)
                print()
                continue

            messages.append({"role": "user", "content": user_input})
            print()
            print("Ines: ", end="", flush=True)
            response = steering.generate_steered(messages)
            print(response)
            print()
            messages.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            print()
            print("Session interrupted. Exiting...")
            break
        except Exception as e:
            logger.error(f"Error during execution: {e}")
            print(f"[Error]: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Ines — The First Local AI Assistant with Controllable Internal Behavior."
    )
    parser.add_argument("--info", action="store_true", help="Print system configuration and exit")
    parser.add_argument("--steer", type=str, default="neutral", choices=AVAILABLE_STEERING_PRESETS,
                        help="Initial steering preset (default: neutral)")
    parser.add_argument("--strength", type=float, default=1.5, help="Initial steering strength alpha")
    parser.add_argument("--organize", action="store_true", help="Scan and organize files in watched folders")
    parser.add_argument("--dry-run", action="store_true", help="Simulate organization without moving files")
    parser.add_argument("--watch", action="store_true", help="Start background folder watcher daemon")

    args = parser.parse_args()

    if args.info:
        print_system_info()
        return

    if args.organize:
        from organizer import FolderWatcher
        print(BANNER)
        print("Starting Smart File Organizer...")
        watcher = FolderWatcher()
        results = watcher.scan_existing(dry_run=args.dry_run)
        print(f"\nCompleted scan of {len(results)} items. (Dry run: {args.dry_run})")
        for r in results:
            print(f"  - {r.get('file')}: {r.get('category', 'N/A')} [{r.get('action')}]")
        return

    if args.watch:
        import time
        from organizer import FolderWatcher
        print(BANNER)
        print("Starting Real-time Folder Watcher daemon...")
        watcher = FolderWatcher()
        watcher.start()
        print(f"Watching folders: {', '.join(str(p) for p in watcher.watch_dirs)}")
        print("Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            watcher.stop()
            print("\nWatcher stopped.")
        return

    run_interactive_cli(preset_name=args.steer, alpha=args.strength, model_name=args.model)

if __name__ == "__main__":
    main()

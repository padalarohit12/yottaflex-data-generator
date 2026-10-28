"""
CLI entrypoint for generation
"""
import sys
from .config import Config
from .generator import DataGenerator
from .export import export_all

def main():
    seed = 20261022
    scale = 'full'
    # Simple arg parsing
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == '--seed' and i+1 < len(args):
            seed = int(args[i+1])
        elif arg == '--scale' and i+1 < len(args):
            scale = args[i+1]
    
    config = Config()
    config.seed = seed
    config.scale = scale
    
    gen = DataGenerator(config)
    data = gen.generate_all()
    
    export_all(data, gen.ground_truth, gen.state_events, config)
    
    print("\n=== Generation Complete ===")
    print(f"Seed: {seed}, Scale: {scale}")
    print(f"Output: {config.output_dir}")
    print(f"Ground truth: {config.ground_truth_dir}")

if __name__ == "__main__":
    main()

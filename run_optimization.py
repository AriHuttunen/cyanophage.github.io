#!/usr/bin/env python3
"""
Main script to run the complete Pareto optimization process
"""
import subprocess
import sys
import time

def run_optimization():
    """Run the complete optimization and HTML generation process"""
    print("=== Pareto Multi-Objective Keyboard Layout Optimizer ===")
    print("Optimizing for both English and Finnish simultaneously")
    print("Fixed letters: n r s t h e a i u o y")
    print()
    
    # Check Python version
    if sys.version_info < (3, 12):
        print("Warning: This script is designed for Python 3.12+")
        print(f"Current version: {sys.version}")
        print()
    
    start_time = time.time()
    
    try:
        # Step 1: Run optimization
        print("Step 1: Running NSGA-II optimization...")
        result = subprocess.run([sys.executable, 'pareto_optimizer.py'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error during optimization:")
            print(result.stderr)
            return False
        
        print(result.stdout)
        
        # Step 2: Generate HTML
        print("Step 2: Generating HTML visualization...")
        result = subprocess.run([sys.executable, 'generate_html.py'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Error during HTML generation:")
            print(result.stderr)
            return False
        
        print(result.stdout)
        
        # Success
        elapsed = time.time() - start_time
        print(f"\n✅ Optimization complete in {elapsed:.1f} seconds!")
        print("\nResults available at: http://localhost:8000/pareto_results.html")
        print("(Make sure your local server is running)")
        
        return True
        
    except FileNotFoundError:
        print("Error: Required files not found. Make sure all scripts are in the current directory.")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_optimization()
    if not success:
        sys.exit(1)
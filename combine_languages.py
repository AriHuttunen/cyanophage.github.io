#!/usr/bin/env python3
"""
Script to combine two language word frequency files with custom percentages.

Usage:
    python combine_languages.py <lang1> <percent1> <lang2> <percent2>

Example:
    python combine_languages.py english 90 finnish 10
    python combine_languages.py english 50 german 50
"""

import json
import sys
import os
from typing import Dict, Any

def load_language_file(language: str) -> Dict[str, int]:
    """Load a language word frequency file."""
    if language.lower() == 'english':
        filename = 'word_list.json'
    else:
        filename = f'words-{language.lower()}.json'
    
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Language file not found: {filename}")
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def combine_languages(lang1_data: Dict[str, int], percent1: float, 
                     lang2_data: Dict[str, int], percent2: float) -> Dict[str, int]:
    """Combine two language datasets with given percentages."""
    combined = {}
    
    # Add words from first language with scaling
    for word, freq in lang1_data.items():
        combined[word] = int(freq * percent1 / 100.0)
    
    # Add words from second language with scaling
    for word, freq in lang2_data.items():
        if word in combined:
            # If word exists in both languages, add the frequencies
            combined[word] += int(freq * percent2 / 100.0)
        else:
            combined[word] = int(freq * percent2 / 100.0)
    
    # Remove any words with zero frequency
    combined = {word: freq for word, freq in combined.items() if freq > 0}
    
    # Sort by frequency (descending)
    return dict(sorted(combined.items(), key=lambda x: x[1], reverse=True))

def main():
    if len(sys.argv) != 5:
        print("Usage: python combine_languages.py <lang1> <percent1> <lang2> <percent2>")
        print("Example: python combine_languages.py english 90 finnish 10")
        sys.exit(1)
    
    lang1, percent1_str, lang2, percent2_str = sys.argv[1:5]
    
    try:
        percent1 = float(percent1_str)
        percent2 = float(percent2_str)
    except ValueError:
        print("Error: Percentages must be numbers")
        sys.exit(1)
    
    if percent1 + percent2 != 100:
        print("Warning: Percentages don't add up to 100")
    
    if percent1 < 0 or percent2 < 0:
        print("Error: Percentages must be positive")
        sys.exit(1)
    
    try:
        # Load language data
        print(f"Loading {lang1} data...")
        lang1_data = load_language_file(lang1)
        print(f"Loaded {len(lang1_data)} words from {lang1}")
        
        print(f"Loading {lang2} data...")
        lang2_data = load_language_file(lang2)
        print(f"Loaded {len(lang2_data)} words from {lang2}")
        
        # Combine languages
        print(f"Combining {lang1} ({percent1}%) + {lang2} ({percent2}%)...")
        combined_data = combine_languages(lang1_data, percent1, lang2_data, percent2)
        
        # Generate output filename
        output_filename = f"words-{lang1.lower()}{int(percent1)}-{lang2.lower()}{int(percent2)}.json"
        
        # Save combined data
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, separators=(',', ':'))
        
        print(f"Created {output_filename} with {len(combined_data)} unique words")
        print(f"Total frequency count: {sum(combined_data.values())}")
        
        # Show top 10 words
        print("\nTop 10 most frequent words:")
        for i, (word, freq) in enumerate(list(combined_data.items())[:10]):
            print(f"{i+1:2d}. {word}: {freq}")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Available languages: english, finnish, german, french, spanish, etc.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
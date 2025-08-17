#!/usr/bin/env python3
"""
Export all 100 Pareto-optimal layouts to a comprehensive JSON file
"""
import json
from datetime import datetime

def export_all_layouts():
    """Export all layouts with complete information to JSON"""
    
    # Load the results
    with open('pareto_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    # Create comprehensive export structure
    export_data = {
        "metadata": {
            "export_date": datetime.now().isoformat(),
            "total_layouts": len(results),
            "optimization_type": "NSGA-II Pareto Multi-Objective",
            "languages": ["English (80%)", "Finnish (20%)"],
            "fixed_letters": ["n", "r", "s", "t", "h", "e", "a", "i", "u", "o", "y", "\\", "/", "q", "ä", "ö"],
            "optimized_positions": 19,
            "metrics": ["SFB", "Scissors", "Lateral Stretch", "Skip Bigrams"],
            "description": "Keyboard layouts optimized for bilingual English/Finnish typing"
        },
        "layouts": []
    }
    
    # Process each layout
    for i, result in enumerate(results):
        layout_data = {
            "id": i + 1,
            "rank_by_weighted_score": i + 1,  # Already sorted by weighted score
            
            # Layout representation
            "layout": {
                "grid": result['layout_grid'],
                "flat_representation": layout_grid_to_string(result['layout_grid']),
                "typing_string": layout_grid_to_typing_string(result['layout_grid'])
            },
            
            # English metrics
            "english_metrics": {
                "same_finger_bigrams": round(result['english_metrics']['sfb'], 3),
                "scissors": round(result['english_metrics']['scissors'], 3),
                "lateral_stretch": round(result['english_metrics']['lat_stretch'], 3),
                "skip_bigrams": round(result['english_metrics']['skip_bigrams'], 3),
                "total_penalty": round(
                    result['english_metrics']['sfb'] + 
                    result['english_metrics']['scissors'] + 
                    result['english_metrics']['lat_stretch'] + 
                    result['english_metrics']['skip_bigrams'], 3
                )
            },
            
            # Finnish metrics
            "finnish_metrics": {
                "same_finger_bigrams": round(result['finnish_metrics']['sfb'], 3),
                "scissors": round(result['finnish_metrics']['scissors'], 3),
                "lateral_stretch": round(result['finnish_metrics']['lat_stretch'], 3),
                "skip_bigrams": round(result['finnish_metrics']['skip_bigrams'], 3),
                "total_penalty": round(
                    result['finnish_metrics']['sfb'] + 
                    result['finnish_metrics']['scissors'] + 
                    result['finnish_metrics']['lat_stretch'] + 
                    result['finnish_metrics']['skip_bigrams'], 3
                )
            },
            
            # Combined scores
            "combined_scores": {
                "weighted_score": round(result['weighted_score'], 3),
                "english_weight": 0.8,
                "finnish_weight": 0.2,
                "combined_total_penalty": round(
                    0.8 * (result['english_metrics']['sfb'] + result['english_metrics']['scissors'] + 
                           result['english_metrics']['lat_stretch'] + result['english_metrics']['skip_bigrams']) +
                    0.2 * (result['finnish_metrics']['sfb'] + result['finnish_metrics']['scissors'] + 
                           result['finnish_metrics']['lat_stretch'] + result['finnish_metrics']['skip_bigrams']), 3
                )
            }
        }
        
        export_data["layouts"].append(layout_data)
    
    # Write to JSON file
    output_filename = 'all_pareto_layouts.json'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Exported {len(results)} layouts to {output_filename}")
    
    # Also create a simple summary
    create_summary_file(export_data)
    
    return output_filename

def layout_grid_to_string(grid):
    """Convert layout grid to a simple string representation"""
    lines = []
    for row in grid:
        line = ""
        for char in row:
            if char:
                line += char.ljust(2)
            else:
                line += "  "
        lines.append(line.rstrip())
    return lines

def layout_grid_to_typing_string(grid):
    """Convert layout grid to typing-friendly string (like Pine v4 format)"""
    # Extract just the main typing area (ignore empty positions)
    chars_by_position = {}
    
    for row_idx, row in enumerate(grid):
        for col_idx, char in enumerate(row):
            if char and char != ' ':
                chars_by_position[(row_idx, col_idx)] = char
    
    # Build the typing string representation
    typing_parts = []
    for row_idx in range(3):  # 3 rows
        row_chars = []
        for col_idx in range(12):  # 12 columns
            char = chars_by_position.get((row_idx, col_idx), '')
            row_chars.append(char)
        
        # Join non-empty characters for this row
        row_string = ''.join(row_chars)
        typing_parts.append(row_string)
    
    return ''.join(typing_parts)

def create_summary_file(export_data):
    """Create a human-readable summary file"""
    summary_lines = []
    summary_lines.append("=" * 60)
    summary_lines.append("PARETO-OPTIMAL KEYBOARD LAYOUTS SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append(f"Generated: {export_data['metadata']['export_date']}")
    summary_lines.append(f"Total layouts: {export_data['metadata']['total_layouts']}")
    summary_lines.append(f"Fixed letters: {' '.join(export_data['metadata']['fixed_letters'])}")
    summary_lines.append("")
    summary_lines.append("Top 10 layouts by weighted score:")
    summary_lines.append("-" * 40)
    
    for i, layout in enumerate(export_data['layouts'][:10]):
        summary_lines.append(f"\nLayout {layout['id']} (Score: {layout['combined_scores']['weighted_score']})")
        
        # Show the grid
        for row in layout['layout']['grid']:
            row_str = ""
            for char in row:
                if char:
                    row_str += f"{char:>2}"
                else:
                    row_str += "  "
            summary_lines.append(f"  {row_str}")
        
        # Show metrics
        eng = layout['english_metrics']
        fin = layout['finnish_metrics']
        summary_lines.append(f"  English: SFB={eng['same_finger_bigrams']}% Scissors={eng['scissors']}% Lat={eng['lateral_stretch']}%")
        summary_lines.append(f"  Finnish: SFB={fin['same_finger_bigrams']}% Scissors={fin['scissors']}% Lat={fin['lateral_stretch']}%")
    
    # Write summary
    with open('layouts_summary.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))
    
    print("✅ Created layouts_summary.txt with top 10 layouts")

def main():
    """Main export function"""
    print("Exporting all Pareto-optimal layouts...")
    
    try:
        filename = export_all_layouts()
        print(f"\n📁 Files created:")
        print(f"   • {filename} - Complete JSON data")
        print(f"   • layouts_summary.txt - Human-readable summary")
        print(f"\n💡 You can now:")
        print(f"   • Import the JSON into other tools")
        print(f"   • Analyze the data programmatically") 
        print(f"   • Share the complete results")
        
    except FileNotFoundError:
        print("❌ Error: pareto_results.json not found")
        print("   Run the optimization first: python3 run_optimization.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Export layouts with detailed bigram analysis like the original web page
"""
import json
from typing import Dict, List, Tuple
from datetime import datetime

class DetailedLayoutAnalyzer:
    def __init__(self):
        # Load language data
        with open('word_list.json', 'r', encoding='utf-8') as f:
            self.english_words = json.load(f)
        
        with open('words-finnish.json', 'r', encoding='utf-8') as f:
            self.finnish_words = json.load(f)
        
        # Calculate bigrams
        self.english_bigrams, self.english_total = self.calculate_bigrams_from_words(self.english_words)
        self.finnish_bigrams, self.finnish_total = self.calculate_bigrams_from_words(self.finnish_words)
    
    def calculate_bigrams_from_words(self, words: Dict[str, int]) -> Tuple[Dict[str, int], int]:
        """Calculate bigram frequencies from word frequency data"""
        bigrams = {}
        total_length = 0
        
        for word, count in words.items():
            word_with_spaces = " " + word + " "
            
            for i in range(len(word_with_spaces) - 1):
                bigram = word_with_spaces[i:i+2]
                if bigram not in bigrams:
                    bigrams[bigram] = 0
                bigrams[bigram] += count
            
            total_length += (len(word) + 1) * count
        
        return bigrams, total_length
    
    def analyze_layout_detailed(self, layout_positions: Dict[str, Dict[str, int]], language: str):
        """Analyze a layout with detailed bigram breakdowns"""
        if language == 'english':
            bigrams = self.english_bigrams
            total_length = self.english_total
        else:
            bigrams = self.finnish_bigrams
            total_length = self.finnish_total
        
        # Initialize counters with detailed tracking
        sfb_bigrams = []
        scissors_bigrams = []
        lat_stretch_bigrams = []
        skip_bigrams = []
        
        # Process each bigram
        for bigram, count in bigrams.items():
            if len(bigram) != 2:
                continue
                
            char1, char2 = bigram[0], bigram[1]
            
            # Skip if characters not in layout
            if char1 not in layout_positions or char2 not in layout_positions:
                continue
                
            pos1 = layout_positions[char1]
            pos2 = layout_positions[char2]
            
            row1, col1, finger1 = pos1['row'], pos1['col'], pos1['finger']
            row2, col2, finger2 = pos2['row'], pos2['col'], pos2['finger']
            
            # Same Finger Bigrams (SFB)
            if finger1 == finger2 and char1 != char2:
                percentage = (count * 100.0) / total_length
                sfb_bigrams.append({
                    'bigram': bigram,
                    'count': count,
                    'percentage': percentage
                })
            
            # Same hand analysis (only if different fingers)
            elif finger1 != finger2:
                # Left hand (cols 0-5)
                if col1 <= 5 and col2 <= 5:
                    if row1 <= 2 and row2 <= 2:
                        # Scissors: 2 rows apart, adjacent columns
                        if abs(row1 - row2) == 2:
                            if abs(col1 - col2) == 1:
                                percentage = (count * 100.0) / total_length
                                scissors_bigrams.append({
                                    'bigram': bigram,
                                    'count': count,
                                    'percentage': percentage
                                })
                        
                        # Skip bigrams (approximation - same as scissors for now)
                        if abs(row1 - row2) == 2:
                            percentage = (count * 100.0) / total_length
                            skip_bigrams.append({
                                'bigram': bigram,
                                'count': count,
                                'percentage': percentage
                            })
                        
                        # Lateral stretch patterns
                        is_lat_stretch = False
                        multiplier = 1.0
                        
                        if (col1 == 5 and col2 == 3) or (col1 == 3 and col2 == 5):
                            is_lat_stretch = True
                        elif (col1 == 5 and col2 == 2) or (col1 == 2 and col2 == 5):
                            is_lat_stretch = True
                            multiplier = 0.5
                        
                        if is_lat_stretch:
                            percentage = (count * multiplier * 100.0) / total_length
                            lat_stretch_bigrams.append({
                                'bigram': bigram,
                                'count': count,
                                'percentage': percentage,
                                'multiplier': multiplier
                            })
                
                # Right hand (cols 6-11)
                elif col1 >= 6 and col2 >= 6:
                    if row1 <= 2 and row2 <= 2:
                        # Scissors: 2 rows apart, adjacent columns
                        if abs(row1 - row2) == 2:
                            if abs(col1 - col2) == 1:
                                percentage = (count * 100.0) / total_length
                                scissors_bigrams.append({
                                    'bigram': bigram,
                                    'count': count,
                                    'percentage': percentage
                                })
                        
                        # Skip bigrams
                        if abs(row1 - row2) == 2:
                            percentage = (count * 100.0) / total_length
                            skip_bigrams.append({
                                'bigram': bigram,
                                'count': count,
                                'percentage': percentage
                            })
                        
                        # Lateral stretch patterns  
                        is_lat_stretch = False
                        multiplier = 1.0
                        
                        if (col1 == 6 and col2 == 8) or (col1 == 8 and col2 == 6):
                            is_lat_stretch = True
                        elif (col1 == 6 and col2 == 9) or (col1 == 9 and col2 == 6):
                            is_lat_stretch = True
                            multiplier = 0.5
                        
                        if is_lat_stretch:
                            percentage = (count * multiplier * 100.0) / total_length
                            lat_stretch_bigrams.append({
                                'bigram': bigram,
                                'count': count,
                                'percentage': percentage,
                                'multiplier': multiplier
                            })
        
        # Sort by percentage (highest first) and take top 10
        sfb_bigrams.sort(key=lambda x: x['percentage'], reverse=True)
        scissors_bigrams.sort(key=lambda x: x['percentage'], reverse=True)
        lat_stretch_bigrams.sort(key=lambda x: x['percentage'], reverse=True)
        skip_bigrams.sort(key=lambda x: x['percentage'], reverse=True)
        
        return {
            'sfb_total': sum(b['percentage'] for b in sfb_bigrams),
            'sfb_bigrams': sfb_bigrams[:10],
            'scissors_total': sum(b['percentage'] for b in scissors_bigrams),
            'scissors_bigrams': scissors_bigrams[:10],
            'lat_stretch_total': sum(b['percentage'] for b in lat_stretch_bigrams),
            'lat_stretch_bigrams': lat_stretch_bigrams[:10],
            'skip_bigrams_total': sum(b['percentage'] for b in skip_bigrams),
            'skip_bigrams': skip_bigrams[:10]
        }
    
    def load_layout_from_grid(self, layout_grid: List[List[str]]) -> Dict[str, Dict[str, int]]:
        """Convert layout grid back to position mapping"""
        # Fixed positions
        layout = {
            'n': {'row': 1, 'col': 1, 'finger': 1},
            'r': {'row': 1, 'col': 2, 'finger': 2}, 
            's': {'row': 1, 'col': 3, 'finger': 3},
            't': {'row': 1, 'col': 4, 'finger': 4},
            'h': {'row': 1, 'col': 7, 'finger': 7},
            'e': {'row': 1, 'col': 8, 'finger': 8},
            'a': {'row': 1, 'col': 9, 'finger': 9},
            'i': {'row': 1, 'col': 10, 'finger': 10},
            'u': {'row': 0, 'col': 8, 'finger': 8},
            'o': {'row': 0, 'col': 9, 'finger': 9},
            'y': {'row': 0, 'col': 10, 'finger': 10},
            '\\': {'row': 2, 'col': 0, 'finger': 1},
            '/': {'row': 2, 'col': 11, 'finger': 10},
            'q': {'row': 0, 'col': 1, 'finger': 1},
            'ä': {'row': 1, 'col': 11, 'finger': 10},
            'ö': {'row': 0, 'col': 11, 'finger': 10},
            ' ': {'row': 3, 'col': 6, 'finger': 6},
        }
        
        # Finger mapping by column
        finger_map = {
            0: 1, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4,
            6: 7, 7: 7, 8: 8, 9: 9, 10: 10, 11: 10
        }
        
        # Add moveable characters from grid
        for row_idx, row in enumerate(layout_grid):
            for col_idx, char in enumerate(row):
                if char and char not in layout:
                    layout[char] = {
                        'row': row_idx,
                        'col': col_idx,
                        'finger': finger_map[col_idx]
                    }
        
        return layout

def get_original_pine_v4_layout():
    """Get the original Pine v4 layout with Finnish extensions
    
    CORRECT FINGER ASSIGNMENTS:
    1:qnj 2:lrx 3:csz 4:mtgkwv 7:'pbfhd 8:ue; 9:oa, 10:yi.öä/
    """
    return {
        # Finger 1: q n j
        'q': {'row': 0, 'col': 0, 'finger': 1},
        'n': {'row': 1, 'col': 0, 'finger': 1},
        'j': {'row': 2, 'col': 0, 'finger': 1},
        
        # Finger 2: l r x
        'l': {'row': 0, 'col': 1, 'finger': 2},
        'r': {'row': 1, 'col': 1, 'finger': 2},
        'x': {'row': 2, 'col': 1, 'finger': 2},
        
        # Finger 3: c s z
        'c': {'row': 0, 'col': 2, 'finger': 3},
        's': {'row': 1, 'col': 2, 'finger': 3},
        'z': {'row': 2, 'col': 2, 'finger': 3},
        
        # Finger 4: m t g k w v
        'm': {'row': 0, 'col': 3, 'finger': 4},
        't': {'row': 1, 'col': 3, 'finger': 4},
        'g': {'row': 2, 'col': 3, 'finger': 4},
        'k': {'row': 0, 'col': 4, 'finger': 4},
        'w': {'row': 1, 'col': 4, 'finger': 4},
        'v': {'row': 2, 'col': 4, 'finger': 4},
        
        # Finger 7: ' p b f h d
        "'": {'row': 0, 'col': 5, 'finger': 7},
        'p': {'row': 1, 'col': 5, 'finger': 7},
        'b': {'row': 2, 'col': 5, 'finger': 7},
        'f': {'row': 0, 'col': 6, 'finger': 7},
        'h': {'row': 1, 'col': 6, 'finger': 7},
        'd': {'row': 2, 'col': 6, 'finger': 7},
        
        # Finger 8: u e ;
        'u': {'row': 0, 'col': 7, 'finger': 8},
        'e': {'row': 1, 'col': 7, 'finger': 8},
        ';': {'row': 2, 'col': 7, 'finger': 8},
        
        # Finger 9: o a ,
        'o': {'row': 0, 'col': 8, 'finger': 9},
        'a': {'row': 1, 'col': 8, 'finger': 9},
        ',': {'row': 2, 'col': 8, 'finger': 9},
        
        # Finger 10: y i . ö ä /
        'y': {'row': 0, 'col': 9, 'finger': 10},
        'i': {'row': 1, 'col': 9, 'finger': 10},
        '.': {'row': 2, 'col': 9, 'finger': 10},
        'ö': {'row': 0, 'col': 10, 'finger': 10},
        'ä': {'row': 1, 'col': 10, 'finger': 10},
        '/': {'row': 2, 'col': 10, 'finger': 10},
        
        # Space
        ' ': {'row': 3, 'col': 6, 'finger': 6},
    }

def export_detailed_layouts():
    """Export layouts with detailed bigram analysis"""
    analyzer = DetailedLayoutAnalyzer()
    
    # Load basic results
    with open('pareto_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print("Analyzing layouts in detail...")
    
    detailed_results = {
        "metadata": {
            "export_date": datetime.now().isoformat(),
            "total_layouts": len(results),
            "analysis_type": "Detailed bigram breakdown like original web page",
            "languages": ["English", "Finnish"],
            "metrics_included": ["SFB", "Scissors", "Lateral Stretch", "Skip Bigrams"],
            "bigram_details": "Top 10 worst bigrams for each metric with percentages"
        },
        "layouts": []
    }
    
    # Analyze each layout
    for i, result in enumerate(results[:10]):  # Analyze top 10 layouts
        print(f"Analyzing layout {i+1}/10...")
        
        # Convert grid to layout positions
        layout_positions = analyzer.load_layout_from_grid(result['layout_grid'])
        
        # Analyze for both languages
        english_detailed = analyzer.analyze_layout_detailed(layout_positions, 'english')
        finnish_detailed = analyzer.analyze_layout_detailed(layout_positions, 'finnish')
        
        layout_data = {
            "id": i + 1,
            "layout_grid": result['layout_grid'],
            "weighted_score": result['weighted_score'],
            
            "english_analysis": {
                "summary": {
                    "sfb_total": round(english_detailed['sfb_total'], 3),
                    "scissors_total": round(english_detailed['scissors_total'], 3),
                    "lat_stretch_total": round(english_detailed['lat_stretch_total'], 3),
                    "skip_bigrams_total": round(english_detailed['skip_bigrams_total'], 3)
                },
                "detailed_bigrams": {
                    "same_finger_bigrams": [
                        {
                            "bigram": b['bigram'],
                            "percentage": round(b['percentage'], 3)
                        } for b in english_detailed['sfb_bigrams']
                    ],
                    "scissors": [
                        {
                            "bigram": b['bigram'], 
                            "percentage": round(b['percentage'], 3)
                        } for b in english_detailed['scissors_bigrams']
                    ],
                    "lateral_stretch": [
                        {
                            "bigram": b['bigram'],
                            "percentage": round(b['percentage'], 3)
                        } for b in english_detailed['lat_stretch_bigrams']
                    ],
                    "skip_bigrams": [
                        {
                            "bigram": b['bigram'],
                            "percentage": round(b['percentage'], 3)
                        } for b in english_detailed['skip_bigrams']
                    ]
                }
            },
            
            "finnish_analysis": {
                "summary": {
                    "sfb_total": round(finnish_detailed['sfb_total'], 3),
                    "scissors_total": round(finnish_detailed['scissors_total'], 3),
                    "lat_stretch_total": round(finnish_detailed['lat_stretch_total'], 3),
                    "skip_bigrams_total": round(finnish_detailed['skip_bigrams_total'], 3)
                },
                "detailed_bigrams": {
                    "same_finger_bigrams": [
                        {
                            "bigram": b['bigram'],
                            "percentage": round(b['percentage'], 3)
                        } for b in finnish_detailed['sfb_bigrams']
                    ],
                    "scissors": [
                        {
                            "bigram": b['bigram'],
                            "percentage": round(b['percentage'], 3)
                        } for b in finnish_detailed['scissors_bigrams']
                    ],
                    "lateral_stretch": [
                        {
                            "bigram": b['bigram'],
                            "percentage": round(b['percentage'], 3)
                        } for b in finnish_detailed['lat_stretch_bigrams']
                    ],
                    "skip_bigrams": [
                        {
                            "bigram": b['bigram'],
                            "percentage": round(b['percentage'], 3)
                        } for b in finnish_detailed['skip_bigrams']
                    ]
                }
            }
        }
        
        detailed_results["layouts"].append(layout_data)
    
    # Write detailed results
    with open('detailed_bigram_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, indent=2, ensure_ascii=False)
    
    print("✅ Created detailed_bigram_analysis.json")
    
    # Create human-readable summary
    create_detailed_summary(detailed_results)
    
    return detailed_results

def create_detailed_summary(detailed_results):
    """Create human-readable summary with bigram details"""
    lines = []
    lines.append("=" * 80)
    lines.append("DETAILED BIGRAM ANALYSIS - ORIGINAL VS OPTIMIZED")
    lines.append("=" * 80)
    lines.append(f"Generated: {detailed_results['metadata']['export_date']}")
    lines.append("")
    
    # Add original Pine v4 layout analysis first
    analyzer = DetailedLayoutAnalyzer()
    original_layout = get_original_pine_v4_layout()
    
    # Analyze original layout
    english_original = analyzer.analyze_layout_detailed(original_layout, 'english')
    finnish_original = analyzer.analyze_layout_detailed(original_layout, 'finnish')
    
    lines.append("ORIGINAL LAYOUT - Pine v4 with Finnish Extensions")
    lines.append("=" * 50)
    
    # Show original layout grid (columns: qnj, lrx, csz, mtg, kwv, 'pb, fhd, ue;, oa,, yi., öä/)
    original_grid = [
        ['q', 'l', 'c', 'm', 'k', "'", 'f', 'u', 'o', 'y', 'ö'],
        ['n', 'r', 's', 't', 'w', 'p', 'h', 'e', 'a', 'i', 'ä'],
        ['j', 'x', 'z', 'g', 'v', 'b', 'd', ';', ',', '.', '/']
    ]
    
    for row in original_grid:
        row_str = ""
        for char in row:
            if char:
                row_str += f"{char:>3}"
            else:
                row_str += "   "
        lines.append(f"  {row_str}")
    lines.append("")
    
    # Original English analysis
    lines.append("ENGLISH:")
    lines.append(f"  Same Finger Bigrams: {english_original['sfb_total']:.3f}%")
    for bigram in english_original['sfb_bigrams'][:5]:
        lines.append(f"    {bigram['bigram']} = {bigram['percentage']:.3f}%")
    
    lines.append(f"  Scissors: {english_original['scissors_total']:.3f}%")
    for bigram in english_original['scissors_bigrams'][:5]:
        lines.append(f"    {bigram['bigram']} = {bigram['percentage']:.3f}%")
    
    lines.append(f"  Lateral Stretch: {english_original['lat_stretch_total']:.3f}%")
    for bigram in english_original['lat_stretch_bigrams'][:5]:
        lines.append(f"    {bigram['bigram']} = {bigram['percentage']:.3f}%")
    
    lines.append("")
    
    # Original Finnish analysis
    lines.append("FINNISH:")
    lines.append(f"  Same Finger Bigrams: {finnish_original['sfb_total']:.3f}%")
    for bigram in finnish_original['sfb_bigrams'][:5]:
        lines.append(f"    {bigram['bigram']} = {bigram['percentage']:.3f}%")
    
    lines.append(f"  Scissors: {finnish_original['scissors_total']:.3f}%")
    for bigram in finnish_original['scissors_bigrams'][:5]:
        lines.append(f"    {bigram['bigram']} = {bigram['percentage']:.3f}%")
    
    lines.append(f"  Lateral Stretch: {finnish_original['lat_stretch_total']:.3f}%")
    for bigram in finnish_original['lat_stretch_bigrams'][:5]:
        lines.append(f"    {bigram['bigram']} = {bigram['percentage']:.3f}%")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("OPTIMIZED LAYOUTS - TOP 3")
    lines.append("=" * 80)
    lines.append("")
    
    for layout in detailed_results['layouts'][:3]:
        lines.append(f"LAYOUT {layout['id']} (Weighted Score: {layout['weighted_score']})")
        lines.append("=" * 40)
        
        # Show layout
        for row in layout['layout_grid']:
            row_str = ""
            for char in row:
                if char:
                    row_str += f"{char:>3}"
                else:
                    row_str += "   "
            lines.append(f"  {row_str}")
        lines.append("")
        
        # English analysis
        eng = layout['english_analysis']
        lines.append("ENGLISH:")
        lines.append(f"  Same Finger Bigrams: {eng['summary']['sfb_total']}%")
        for bigram in eng['detailed_bigrams']['same_finger_bigrams'][:5]:
            lines.append(f"    {bigram['bigram']} = {bigram['percentage']}%")
        
        lines.append(f"  Scissors: {eng['summary']['scissors_total']}%")
        for bigram in eng['detailed_bigrams']['scissors'][:5]:
            lines.append(f"    {bigram['bigram']} = {bigram['percentage']}%")
        
        lines.append(f"  Lateral Stretch: {eng['summary']['lat_stretch_total']}%")
        for bigram in eng['detailed_bigrams']['lateral_stretch'][:5]:
            lines.append(f"    {bigram['bigram']} = {bigram['percentage']}%")
        
        lines.append("")
        
        # Finnish analysis
        fin = layout['finnish_analysis']
        lines.append("FINNISH:")
        lines.append(f"  Same Finger Bigrams: {fin['summary']['sfb_total']}%")
        for bigram in fin['detailed_bigrams']['same_finger_bigrams'][:5]:
            lines.append(f"    {bigram['bigram']} = {bigram['percentage']}%")
        
        lines.append(f"  Scissors: {fin['summary']['scissors_total']}%")
        for bigram in fin['detailed_bigrams']['scissors'][:5]:
            lines.append(f"    {bigram['bigram']} = {bigram['percentage']}%")
        
        lines.append(f"  Lateral Stretch: {fin['summary']['lat_stretch_total']}%")
        for bigram in fin['detailed_bigrams']['lateral_stretch'][:5]:
            lines.append(f"    {bigram['bigram']} = {bigram['percentage']}%")
        
        lines.append("")
        lines.append("-" * 80)
        lines.append("")
    
    # Write summary
    with open('detailed_analysis_summary.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print("✅ Created detailed_analysis_summary.txt")

if __name__ == "__main__":
    export_detailed_layouts()
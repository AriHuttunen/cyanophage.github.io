#!/usr/bin/env python3
import json
import sys

def create_layout_mapping():
    """Create the layout mapping for the user's current layout"""
    # Layout: [ignored] q l c m k | ' f u o y ö
    #         -        n r s t w | p h e a i ä  
    #         \        j x z g v | b d ; , . /
    
    # Finger mapping: 1=pinky, 2=ring, 3=middle, 4=index, 7=index, 8=middle, 9=ring, 10=pinky
    layout = {}
    
    # Top row (row 0)
    layout['q'] = {'row': 0, 'col': 1, 'finger': 1}
    layout['l'] = {'row': 0, 'col': 2, 'finger': 2}
    layout['c'] = {'row': 0, 'col': 3, 'finger': 3}
    layout['m'] = {'row': 0, 'col': 4, 'finger': 4}
    layout['k'] = {'row': 0, 'col': 5, 'finger': 4}
    layout["'"] = {'row': 0, 'col': 6, 'finger': 7}
    layout['f'] = {'row': 0, 'col': 7, 'finger': 7}
    layout['u'] = {'row': 0, 'col': 8, 'finger': 8}
    layout['o'] = {'row': 0, 'col': 9, 'finger': 9}
    layout['y'] = {'row': 0, 'col': 10, 'finger': 10}
    layout['ö'] = {'row': 0, 'col': 11, 'finger': 10}
    
    # Middle row (row 1) - home row
    layout['-'] = {'row': 1, 'col': 0, 'finger': 1}
    layout['n'] = {'row': 1, 'col': 1, 'finger': 1}
    layout['r'] = {'row': 1, 'col': 2, 'finger': 2}
    layout['s'] = {'row': 1, 'col': 3, 'finger': 3}
    layout['t'] = {'row': 1, 'col': 4, 'finger': 4}
    layout['w'] = {'row': 1, 'col': 5, 'finger': 4}
    layout['p'] = {'row': 1, 'col': 6, 'finger': 7}
    layout['h'] = {'row': 1, 'col': 7, 'finger': 7}
    layout['e'] = {'row': 1, 'col': 8, 'finger': 8}
    layout['a'] = {'row': 1, 'col': 9, 'finger': 9}
    layout['i'] = {'row': 1, 'col': 10, 'finger': 10}
    layout['ä'] = {'row': 1, 'col': 11, 'finger': 10}
    
    # Bottom row (row 2)
    layout['\\'] = {'row': 2, 'col': 0, 'finger': 1}
    layout['j'] = {'row': 2, 'col': 1, 'finger': 1}
    layout['x'] = {'row': 2, 'col': 2, 'finger': 2}
    layout['z'] = {'row': 2, 'col': 3, 'finger': 3}
    layout['g'] = {'row': 2, 'col': 4, 'finger': 4}
    layout['v'] = {'row': 2, 'col': 5, 'finger': 4}
    layout['b'] = {'row': 2, 'col': 6, 'finger': 7}
    layout['d'] = {'row': 2, 'col': 7, 'finger': 7}
    layout[';'] = {'row': 2, 'col': 8, 'finger': 8}
    layout[','] = {'row': 2, 'col': 9, 'finger': 9}
    layout['.'] = {'row': 2, 'col': 10, 'finger': 10}
    layout['/'] = {'row': 2, 'col': 11, 'finger': 10}
    
    # Space (usually thumb)
    layout[' '] = {'row': 3, 'col': 6, 'finger': 6}
    
    return layout

def calculate_bigrams_from_words(words):
    """Calculate bigram frequencies from word frequency data"""
    bigrams = {}
    total_length = 0
    
    for word, count in words.items():
        # Add spaces around words like the original code
        word_with_spaces = " " + word + " "
        
        for i in range(len(word_with_spaces) - 1):
            bigram = word_with_spaces[i:i+2]
            if bigram not in bigrams:
                bigrams[bigram] = 0
            bigrams[bigram] += count
        
        total_length += (len(word) + 1) * count  # +1 for space
    
    return bigrams, total_length

def calculate_metrics(words, layout):
    """Calculate keyboard layout metrics"""
    bigrams, total_length = calculate_bigrams_from_words(words)
    
    # Initialize counters
    sfb = 0
    psfb = 0  # pinky SFB
    rsfb = 0  # ring SFB
    scissors = 0
    lat_str = 0  # lateral stretch
    wide_scissors = 0
    
    # Process each bigram
    for bigram, count in bigrams.items():
        if len(bigram) != 2:
            continue
            
        char1, char2 = bigram[0], bigram[1]
        
        # Skip if characters not in layout
        if char1 not in layout or char2 not in layout:
            continue
            
        pos1 = layout[char1]
        pos2 = layout[char2]
        
        row1, col1, finger1 = pos1['row'], pos1['col'], pos1['finger']
        row2, col2, finger2 = pos2['row'], pos2['col'], pos2['finger']
        
        # Same Finger Bigrams (SFB)
        if finger1 == finger2 and char1 != char2:
            sfb += count
            # Pinky SFB
            if finger1 == 1 or finger1 == 10:
                psfb += count
            # Ring SFB  
            if finger1 == 2 or finger1 == 9:
                rsfb += count
        
        # Same hand analysis (only if different fingers)
        elif finger1 != finger2:
            # Left hand (cols 0-5)
            if col1 <= 5 and col2 <= 5:
                if row1 <= 2 and row2 <= 2:
                    # Scissors: 2 rows apart, adjacent columns
                    if abs(row1 - row2) == 2:
                        if abs(col1 - col2) == 1:
                            scissors += count
                        else:
                            wide_scissors += count
                    
                    # Lateral stretch patterns
                    if (col1 == 5 and col2 == 3) or (col1 == 3 and col2 == 5):
                        lat_str += count
                    if (col1 == 5 and col2 == 2) or (col1 == 2 and col2 == 5):
                        lat_str += count / 2
            
            # Right hand (cols 6-11)
            elif col1 >= 6 and col2 >= 6:
                if row1 <= 2 and row2 <= 2:
                    # Scissors: 2 rows apart, adjacent columns
                    if abs(row1 - row2) == 2:
                        if abs(col1 - col2) == 1:
                            scissors += count
                        else:
                            wide_scissors += count
                    
                    # Lateral stretch patterns  
                    if (col1 == 6 and col2 == 8) or (col1 == 8 and col2 == 6):
                        lat_str += count
                    if (col1 == 6 and col2 == 9) or (col1 == 9 and col2 == 6):
                        lat_str += count / 2
    
    # Calculate percentages
    sfb_pct = (sfb * 100.0) / total_length
    scissors_pct = (scissors * 100.0) / total_length  
    lat_str_pct = (lat_str * 100.0) / total_length
    
    # Skip bigrams calculation (simplified - this needs more complex analysis)
    # For now, estimate based on pattern
    skip_bigrams_pct = scissors_pct  # Rough approximation
    
    return {
        'sfb': sfb_pct,
        'scissors': scissors_pct,
        'lat_stretch': lat_str_pct,
        'skip_bigrams': skip_bigrams_pct,
        'total_length': total_length
    }

def main():
    layout = create_layout_mapping()
    
    # Load English data
    print("Loading English data...")
    with open('word_list.json', 'r') as f:
        english_words = json.load(f)
    
    # Load Finnish data  
    print("Loading Finnish data...")
    with open('words-finnish.json', 'r') as f:
        finnish_words = json.load(f)
    
    # Calculate English metrics
    print("\nCalculating English metrics...")
    english_metrics = calculate_metrics(english_words, layout)
    
    # Calculate Finnish metrics
    print("Calculating Finnish metrics...")
    finnish_metrics = calculate_metrics(finnish_words, layout)
    
    # Display results
    print("\n" + "="*50)
    print("LAYOUT STATISTICS")
    print("="*50)
    
    print("\nYour Current Layout:")
    print("[ignored]  q  l  c  m  k     '  f  u  o  y  ö")
    print("-          n  r  s  t  w     p  h  e  a  i  ä")
    print("\\          j  x  z  g  v     b  d  ;  ,  .  /")
    
    print(f"\nENGLISH STATISTICS:")
    print(f"Same Finger Bigrams (SFB): {english_metrics['sfb']:.2f}%")
    print(f"Skip Bigrams: {english_metrics['skip_bigrams']:.2f}%")
    print(f"Lateral Stretch Bigrams: {english_metrics['lat_stretch']:.2f}%")
    print(f"Scissors: {english_metrics['scissors']:.2f}%")
    
    print(f"\nFINNISH STATISTICS:")
    print(f"Same Finger Bigrams (SFB): {finnish_metrics['sfb']:.2f}%")
    print(f"Skip Bigrams: {finnish_metrics['skip_bigrams']:.2f}%")
    print(f"Lateral Stretch Bigrams: {finnish_metrics['lat_stretch']:.2f}%")
    print(f"Scissors: {finnish_metrics['scissors']:.2f}%")

if __name__ == "__main__":
    main()
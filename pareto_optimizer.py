#!/usr/bin/env python3
"""
Multi-objective keyboard layout optimizer using NSGA-II
Optimizes for both English and Finnish simultaneously
"""
import json
import random
import math
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from copy import deepcopy

@dataclass
class LayoutMetrics:
    """Metrics for a single language"""
    sfb: float
    scissors: float
    lat_stretch: float
    skip_bigrams: float

@dataclass
class Layout:
    """Represents a keyboard layout with dual-language metrics"""
    positions: Dict[str, Dict[str, int]]  # char -> {row, col, finger}
    english_metrics: LayoutMetrics
    finnish_metrics: LayoutMetrics
    weighted_score: float
    rank: int = 0
    crowding_distance: float = 0.0
    
    def dominates(self, other: 'Layout') -> bool:
        """Check if this layout Pareto dominates another"""
        # Convert to minimization objectives (lower is better)
        self_obj = [
            self.english_metrics.sfb, self.english_metrics.scissors,
            self.english_metrics.lat_stretch, self.english_metrics.skip_bigrams,
            self.finnish_metrics.sfb, self.finnish_metrics.scissors,
            self.finnish_metrics.lat_stretch, self.finnish_metrics.skip_bigrams
        ]
        other_obj = [
            other.english_metrics.sfb, other.english_metrics.scissors,
            other.english_metrics.lat_stretch, other.english_metrics.skip_bigrams,
            other.finnish_metrics.sfb, other.finnish_metrics.scissors,
            other.finnish_metrics.lat_stretch, other.finnish_metrics.skip_bigrams
        ]
        
        # Check if self is better or equal in all objectives
        better_or_equal = all(s <= o for s, o in zip(self_obj, other_obj))
        # Check if self is strictly better in at least one objective
        strictly_better = any(s < o for s, o in zip(self_obj, other_obj))
        
        return better_or_equal and strictly_better

class KeyboardOptimizer:
    def __init__(self):
        # Fixed letters that cannot move
        self.fixed_letters = {'n', 'r', 's', 't', 'h', 'e', 'a', 'i', 'u', 'o', 'y'}
        
        # Define the base layout structure with fixed positions
        self.base_layout = {
            # Fixed positions (cannot change)
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
            ' ': {'row': 3, 'col': 6, 'finger': 6},  # Space
        }
        
        # Moveable positions (empty in base, will be filled by optimization)
        self.moveable_positions = [
            {'row': 0, 'col': 1, 'finger': 1},   # q position
            {'row': 0, 'col': 2, 'finger': 2},   # l position
            {'row': 0, 'col': 3, 'finger': 3},   # c position
            {'row': 0, 'col': 4, 'finger': 4},   # m position
            {'row': 0, 'col': 5, 'finger': 4},   # k position
            {'row': 0, 'col': 6, 'finger': 7},   # ' position
            {'row': 0, 'col': 7, 'finger': 7},   # f position
            {'row': 0, 'col': 11, 'finger': 10}, # ö position
            {'row': 1, 'col': 0, 'finger': 1},   # - position
            {'row': 1, 'col': 5, 'finger': 4},   # w position
            {'row': 1, 'col': 6, 'finger': 7},   # p position
            {'row': 1, 'col': 11, 'finger': 10}, # ä position
            {'row': 2, 'col': 0, 'finger': 1},   # \ position
            {'row': 2, 'col': 1, 'finger': 1},   # j position
            {'row': 2, 'col': 2, 'finger': 2},   # x position
            {'row': 2, 'col': 3, 'finger': 3},   # z position
            {'row': 2, 'col': 4, 'finger': 4},   # g position
            {'row': 2, 'col': 5, 'finger': 4},   # v position
            {'row': 2, 'col': 6, 'finger': 7},   # b position
            {'row': 2, 'col': 7, 'finger': 7},   # d position
            {'row': 2, 'col': 8, 'finger': 8},   # ; position
            {'row': 2, 'col': 9, 'finger': 9},   # , position
            {'row': 2, 'col': 10, 'finger': 10}, # . position
            {'row': 2, 'col': 11, 'finger': 10}, # / position
        ]
        
        # Moveable letters
        self.moveable_letters = ['q', 'l', 'c', 'm', 'k', "'", 'f', 'ö', '-', 'w', 'p', 'ä', 
                                '\\', 'j', 'x', 'z', 'g', 'v', 'b', 'd', ';', ',', '.', '/']
        
        # Load language data
        self.load_language_data()
    
    def load_language_data(self):
        """Load English and Finnish word frequency data"""
        print("Loading language data...")
        
        with open('word_list.json', 'r', encoding='utf-8') as f:
            self.english_words = json.load(f)
        
        with open('words-finnish.json', 'r', encoding='utf-8') as f:
            self.finnish_words = json.load(f)
        
        # Pre-calculate bigrams for efficiency
        self.english_bigrams, self.english_total = self.calculate_bigrams_from_words(self.english_words)
        self.finnish_bigrams, self.finnish_total = self.calculate_bigrams_from_words(self.finnish_words)
        
        print(f"Loaded {len(self.english_words)} English words, {len(self.finnish_words)} Finnish words")
    
    def calculate_bigrams_from_words(self, words: Dict[str, int]) -> Tuple[Dict[str, int], int]:
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
    
    def create_random_layout(self) -> Dict[str, Dict[str, int]]:
        """Create a random layout with fixed letters in place"""
        layout = deepcopy(self.base_layout)
        
        # Randomly assign moveable letters to moveable positions
        shuffled_letters = self.moveable_letters[:]
        random.shuffle(shuffled_letters)
        shuffled_positions = self.moveable_positions[:]
        random.shuffle(shuffled_positions)
        
        for letter, position in zip(shuffled_letters, shuffled_positions):
            layout[letter] = position
            
        return layout
    
    def calculate_metrics(self, layout: Dict[str, Dict[str, int]], 
                         bigrams: Dict[str, int], total_length: int) -> LayoutMetrics:
        """Calculate keyboard layout metrics for a given language"""
        # Initialize counters
        sfb = 0
        scissors = 0
        lat_str = 0
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
        
        # Skip bigrams approximation (use scissors as rough estimate)
        skip_bigrams_pct = scissors_pct
        
        return LayoutMetrics(
            sfb=sfb_pct,
            scissors=scissors_pct,
            lat_stretch=lat_str_pct,
            skip_bigrams=skip_bigrams_pct
        )
    
    def evaluate_layout(self, layout_positions: Dict[str, Dict[str, int]]) -> Layout:
        """Evaluate a layout for both languages"""
        # Calculate metrics for both languages
        english_metrics = self.calculate_metrics(layout_positions, self.english_bigrams, self.english_total)
        finnish_metrics = self.calculate_metrics(layout_positions, self.finnish_bigrams, self.finnish_total)
        
        # Calculate weighted score (80% English, 20% Finnish)
        english_score = english_metrics.sfb + english_metrics.scissors + english_metrics.lat_stretch
        finnish_score = finnish_metrics.sfb + finnish_metrics.scissors + finnish_metrics.lat_stretch
        weighted_score = 0.8 * english_score + 0.2 * finnish_score
        
        return Layout(
            positions=layout_positions,
            english_metrics=english_metrics,
            finnish_metrics=finnish_metrics,
            weighted_score=weighted_score
        )
    
    def mutate_layout(self, layout: Layout) -> Layout:
        """Create a mutated version of a layout"""
        new_positions = deepcopy(layout.positions)
        
        # Get current moveable letter assignments
        moveable_chars = []
        moveable_pos = []
        
        for char in self.moveable_letters:
            if char in new_positions:
                moveable_chars.append(char)
                moveable_pos.append(new_positions[char])
        
        # Perform swap mutation
        if len(moveable_chars) >= 2:
            # Randomly swap two moveable letters
            idx1, idx2 = random.sample(range(len(moveable_chars)), 2)
            char1, char2 = moveable_chars[idx1], moveable_chars[idx2]
            
            # Swap their positions
            new_positions[char1], new_positions[char2] = new_positions[char2], new_positions[char1]
        
        return self.evaluate_layout(new_positions)
    
    def fast_non_dominated_sort(self, population: List[Layout]) -> List[List[Layout]]:
        """NSGA-II fast non-dominated sorting"""
        fronts = [[]]
        
        for i, layout_i in enumerate(population):
            layout_i.domination_count = 0
            layout_i.dominated_solutions = []
            
            for j, layout_j in enumerate(population):
                if layout_i.dominates(layout_j):
                    layout_i.dominated_solutions.append(j)
                elif layout_j.dominates(layout_i):
                    layout_i.domination_count += 1
            
            if layout_i.domination_count == 0:
                layout_i.rank = 0
                fronts[0].append(layout_i)
        
        front_index = 0
        while len(fronts[front_index]) > 0:
            next_front = []
            for layout_i in fronts[front_index]:
                for j in layout_i.dominated_solutions:
                    population[j].domination_count -= 1
                    if population[j].domination_count == 0:
                        population[j].rank = front_index + 1
                        next_front.append(population[j])
            
            front_index += 1
            fronts.append(next_front)
        
        return fronts[:-1]  # Remove last empty front
    
    def calculate_crowding_distance(self, front: List[Layout]):
        """Calculate crowding distance for layouts in a front"""
        if len(front) <= 2:
            for layout in front:
                layout.crowding_distance = float('inf')
            return
        
        # Initialize distances
        for layout in front:
            layout.crowding_distance = 0
        
        # Get all objectives
        objectives = [
            lambda l: l.english_metrics.sfb,
            lambda l: l.english_metrics.scissors,
            lambda l: l.english_metrics.lat_stretch,
            lambda l: l.english_metrics.skip_bigrams,
            lambda l: l.finnish_metrics.sfb,
            lambda l: l.finnish_metrics.scissors,
            lambda l: l.finnish_metrics.lat_stretch,
            lambda l: l.finnish_metrics.skip_bigrams,
        ]
        
        # Calculate crowding distance for each objective
        for obj_func in objectives:
            # Sort by objective value
            front.sort(key=obj_func)
            
            # Set boundary points to infinity
            front[0].crowding_distance = float('inf')
            front[-1].crowding_distance = float('inf')
            
            # Calculate distances for intermediate points
            obj_values = [obj_func(layout) for layout in front]
            obj_range = max(obj_values) - min(obj_values)
            
            if obj_range > 0:
                for i in range(1, len(front) - 1):
                    distance = (obj_values[i + 1] - obj_values[i - 1]) / obj_range
                    front[i].crowding_distance += distance
    
    def optimize(self, population_size: int = 100, generations: int = 50) -> List[Layout]:
        """Run NSGA-II optimization"""
        print(f"Starting optimization: {population_size} population, {generations} generations")
        
        # Initialize population
        population = []
        for _ in range(population_size):
            layout_positions = self.create_random_layout()
            layout = self.evaluate_layout(layout_positions)
            population.append(layout)
        
        best_weighted_score = float('inf')
        
        for generation in range(generations):
            # Create offspring through mutation
            offspring = []
            for layout in population:
                if random.random() < 0.8:  # Mutation probability
                    mutated = self.mutate_layout(layout)
                    offspring.append(mutated)
            
            # Combine parent and offspring populations
            combined_population = population + offspring
            
            # Fast non-dominated sort
            fronts = self.fast_non_dominated_sort(combined_population)
            
            # Calculate crowding distance for each front
            for front in fronts:
                self.calculate_crowding_distance(front)
            
            # Select next generation
            new_population = []
            front_index = 0
            
            while len(new_population) + len(fronts[front_index]) <= population_size:
                new_population.extend(fronts[front_index])
                front_index += 1
            
            # Fill remaining slots with best crowding distance
            if len(new_population) < population_size:
                remaining_front = fronts[front_index]
                remaining_front.sort(key=lambda x: x.crowding_distance, reverse=True)
                new_population.extend(remaining_front[:population_size - len(new_population)])
            
            population = new_population
            
            # Track progress
            current_best = min(layout.weighted_score for layout in population)
            if current_best < best_weighted_score:
                best_weighted_score = current_best
                print(f"Generation {generation}: Best weighted score = {best_weighted_score:.3f}")
        
        # Return Pareto front (first front)
        final_fronts = self.fast_non_dominated_sort(population)
        pareto_front = final_fronts[0] if final_fronts else []
        
        # Sort by weighted score for easier interpretation
        pareto_front.sort(key=lambda x: x.weighted_score)
        
        print(f"Optimization complete. Found {len(pareto_front)} Pareto-optimal solutions.")
        return pareto_front

def main():
    """Main optimization function"""
    optimizer = KeyboardOptimizer()
    
    # Run optimization
    pareto_solutions = optimizer.optimize(population_size=100, generations=100)
    
    # Save results (will be used by HTML generator)
    results = []
    for i, layout in enumerate(pareto_solutions):
        # Convert layout to readable format
        layout_grid = [[''] * 12 for _ in range(3)]
        
        for char, pos in layout.positions.items():
            if char != ' ' and pos['row'] < 3:  # Skip space and invalid positions
                layout_grid[pos['row']][pos['col']] = char
        
        result = {
            'id': i,
            'layout_grid': layout_grid,
            'english_metrics': {
                'sfb': layout.english_metrics.sfb,
                'scissors': layout.english_metrics.scissors,
                'lat_stretch': layout.english_metrics.lat_stretch,
                'skip_bigrams': layout.english_metrics.skip_bigrams,
            },
            'finnish_metrics': {
                'sfb': layout.finnish_metrics.sfb,
                'scissors': layout.finnish_metrics.scissors,
                'lat_stretch': layout.finnish_metrics.lat_stretch,
                'skip_bigrams': layout.finnish_metrics.skip_bigrams,
            },
            'weighted_score': layout.weighted_score
        }
        results.append(result)
    
    # Save to JSON for HTML generator
    with open('pareto_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to pareto_results.json")
    print("Run generate_html.py to create the web interface")

if __name__ == "__main__":
    main()
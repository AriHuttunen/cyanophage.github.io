#!/usr/bin/env python3
"""
Generate HTML page showing Pareto-optimal keyboard layouts
"""
import json

def generate_layout_html(layout_grid, layout_id):
    """Generate HTML for a single keyboard layout"""
    html = f'<div class="keyboard" id="layout-{layout_id}">\n'
    
    for row_idx, row in enumerate(layout_grid):
        html += f'  <div class="row">\n'
        for col_idx, char in enumerate(row):
            if char:
                # Check if this is a fixed letter
                fixed_letters = {'n', 'r', 's', 't', 'h', 'e', 'a', 'i', 'u', 'o', 'y'}
                css_class = "key fixed" if char in fixed_letters else "key"
                display_char = "␣" if char == " " else char
                html += f'    <div class="{css_class}">{display_char}</div>\n'
            else:
                html += f'    <div class="key empty"></div>\n'
        html += f'  </div>\n'
    
    html += '</div>\n'
    return html

def generate_metrics_html(english_metrics, finnish_metrics, weighted_score):
    """Generate HTML for metrics display"""
    html = '<div class="metrics">\n'
    
    # English metrics
    html += '  <div class="language-metrics">\n'
    html += '    <h4>English</h4>\n'
    html += f'    <div class="metric">SFB: <span class="value">{english_metrics["sfb"]:.2f}%</span></div>\n'
    html += f'    <div class="metric">Scissors: <span class="value">{english_metrics["scissors"]:.2f}%</span></div>\n'
    html += f'    <div class="metric">Lat Stretch: <span class="value">{english_metrics["lat_stretch"]:.2f}%</span></div>\n'
    html += f'    <div class="metric">Skip Bigrams: <span class="value">{english_metrics["skip_bigrams"]:.2f}%</span></div>\n'
    html += '  </div>\n'
    
    # Finnish metrics
    html += '  <div class="language-metrics">\n'
    html += '    <h4>Finnish</h4>\n'
    html += f'    <div class="metric">SFB: <span class="value">{finnish_metrics["sfb"]:.2f}%</span></div>\n'
    html += f'    <div class="metric">Scissors: <span class="value">{finnish_metrics["scissors"]:.2f}%</span></div>\n'
    html += f'    <div class="metric">Lat Stretch: <span class="value">{finnish_metrics["lat_stretch"]:.2f}%</span></div>\n'
    html += f'    <div class="metric">Skip Bigrams: <span class="value">{finnish_metrics["skip_bigrams"]:.2f}%</span></div>\n'
    html += '  </div>\n'
    
    # Weighted score
    html += '  <div class="weighted-score">\n'
    html += f'    <h4>Weighted Score</h4>\n'
    html += f'    <div class="score">{weighted_score:.3f}</div>\n'
    html += f'    <div class="weight-info">(80% English + 20% Finnish)</div>\n'
    html += '  </div>\n'
    
    html += '</div>\n'
    return html

def generate_html_page():
    """Generate complete HTML page"""
    # Load results
    with open('pareto_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pareto-Optimal Keyboard Layouts</title>
    <style>
        body {
            font-family: 'Roboto Mono', monospace;
            background-color: #1b1c1f;
            color: #dfe2eb;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            color: #ffffff;
            margin-bottom: 10px;
        }
        
        .subtitle {
            text-align: center;
            color: #999;
            margin-bottom: 30px;
        }
        
        .layout-container {
            background-color: #2a2d35;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            border: 1px solid #444;
        }
        
        .layout-header {
            text-align: center;
            margin-bottom: 20px;
        }
        
        .layout-content {
            display: flex;
            gap: 30px;
            align-items: flex-start;
        }
        
        .keyboard {
            flex: 1;
        }
        
        .row {
            display: flex;
            gap: 4px;
            margin-bottom: 4px;
            justify-content: center;
        }
        
        .key {
            width: 35px;
            height: 35px;
            background-color: #444;
            border: 1px solid #666;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: bold;
        }
        
        .key.fixed {
            background-color: #4a7c59;
            color: #ffffff;
            border-color: #5a8c69;
        }
        
        .key.empty {
            background-color: #333;
            border-color: #555;
        }
        
        .metrics {
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .language-metrics {
            background-color: #333;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #555;
        }
        
        .language-metrics h4 {
            margin: 0 0 10px 0;
            color: #ffffff;
            text-align: center;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
        }
        
        .value {
            font-weight: bold;
            color: #4CAF50;
        }
        
        .weighted-score {
            background-color: #3a3a3a;
            padding: 15px;
            border-radius: 6px;
            border: 2px solid #6a6a6a;
            text-align: center;
        }
        
        .weighted-score h4 {
            margin: 0 0 10px 0;
            color: #ffffff;
        }
        
        .score {
            font-size: 24px;
            font-weight: bold;
            color: #ffeb3b;
            margin-bottom: 5px;
        }
        
        .weight-info {
            font-size: 11px;
            color: #999;
        }
        
        .legend {
            background-color: #2a2d35;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 30px;
            border: 1px solid #444;
            text-align: center;
        }
        
        .legend-item {
            display: inline-block;
            margin: 0 15px;
            font-size: 14px;
        }
        
        .legend-key {
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 3px;
            margin-right: 8px;
            vertical-align: middle;
        }
        
        .legend-key.fixed {
            background-color: #4a7c59;
        }
        
        .legend-key.moveable {
            background-color: #444;
        }
        
        @media (max-width: 1000px) {
            .layout-content {
                flex-direction: column;
            }
            
            .keyboard {
                align-self: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Pareto-Optimal Keyboard Layouts</h1>
        <p class="subtitle">Multi-objective optimization for English (80%) and Finnish (20%)</p>
        
        <div class="legend">
            <div class="legend-item">
                <span class="legend-key fixed"></span>
                Fixed letters (nrstheaiuoy)
            </div>
            <div class="legend-item">
                <span class="legend-key moveable"></span>
                Optimized letters
            </div>
        </div>
'''
    
    # Add each layout
    for i, result in enumerate(results):
        html += f'''
        <div class="layout-container">
            <div class="layout-header">
                <h3>Layout {i + 1}</h3>
            </div>
            <div class="layout-content">
'''
        
        # Add keyboard layout
        html += generate_layout_html(result['layout_grid'], result['id'])
        
        # Add metrics
        html += generate_metrics_html(
            result['english_metrics'], 
            result['finnish_metrics'], 
            result['weighted_score']
        )
        
        html += '''
            </div>
        </div>
'''
    
    html += '''
    </div>
</body>
</html>'''
    
    # Write HTML file
    with open('pareto_results.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Generated pareto_results.html")

if __name__ == "__main__":
    generate_html_page()
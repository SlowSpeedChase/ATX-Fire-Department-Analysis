#!/usr/bin/env python3
"""
Step 5: Visualization
======================
Creates maps and charts for the fire resource analysis.

Usage:
    python scripts/05_visualize.py

Input:
    processed_data/response_areas_final.geojson
    outputs/summary_by_urban_class.csv
    outputs/summary_by_housing_type.csv

Output:
    outputs/map_incidents_per_capita.html
    outputs/map_urban_classification.html
    outputs/map_housing_typology.html
    outputs/chart_urban_comparison.png
    outputs/chart_housing_correlation.png
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# Try to import folium for interactive maps
try:
    import folium
    from folium import plugins
    HAS_FOLIUM = True
except ImportError:
    HAS_FOLIUM = False
    print("Note: Install folium for interactive maps: pip install folium")


def load_data():
    """Load processed data"""
    print("\nLoading data...")
    
    ra = gpd.read_file("processed_data/response_areas_final.geojson")
    print(f"  Response areas: {len(ra)}")
    
    summary_urban = pd.read_csv("outputs/summary_by_urban_class.csv")
    summary_housing = pd.read_csv("outputs/summary_by_housing_type.csv")
    
    return ra, summary_urban, summary_housing


def create_choropleth_map(gdf, column, title, filename, colormap='YlOrRd'):
    """Create an interactive choropleth map with folium"""
    if not HAS_FOLIUM:
        print(f"  Skipping {filename} (folium not installed)")
        return
    
    print(f"  Creating: {filename}")
    
    # Center on Austin
    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='cartodbpositron')
    
    # Filter out invalid values
    valid_gdf = gdf[gdf[column].notna() & (gdf[column] > 0)].copy()
    
    if len(valid_gdf) == 0:
        print(f"    Warning: No valid data for {column}")
        return
    
    # Create choropleth
    folium.Choropleth(
        geo_data=valid_gdf.__geo_interface__,
        data=valid_gdf,
        columns=['response_area_id', column],
        key_on='feature.properties.response_area_id',
        fill_color=colormap,
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=title,
        nan_fill_color='white'
    ).add_to(m)
    
    # Add tooltips
    style_function = lambda x: {'fillColor': '#ffffff', 'color': '#000000', 'fillOpacity': 0, 'weight': 0.1}
    highlight_function = lambda x: {'fillColor': '#000000', 'color': '#000000', 'fillOpacity': 0.3, 'weight': 1}
    
    tooltip = folium.GeoJsonTooltip(
        fields=['response_area_id', column, 'population', 'urban_class'],
        aliases=['Response Area:', f'{title}:', 'Population:', 'Classification:'],
        localize=True
    )
    
    folium.GeoJson(
        valid_gdf,
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=tooltip
    ).add_to(m)
    
    m.save(f"outputs/{filename}")
    print(f"    ✓ Saved: outputs/{filename}")


def create_categorical_map(gdf, column, title, filename, colors=None):
    """Create a categorical choropleth map"""
    if not HAS_FOLIUM:
        print(f"  Skipping {filename} (folium not installed)")
        return
    
    print(f"  Creating: {filename}")
    
    # Center on Austin
    center_lat = gdf.geometry.centroid.y.mean()
    center_lon = gdf.geometry.centroid.x.mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11, tiles='cartodbpositron')
    
    # Default colors
    if colors is None:
        colors = {
            'urban_core': '#d62728',       # Red
            'inner_suburban': '#ff7f0e',   # Orange
            'outer_suburban': '#2ca02c',   # Green
            'unknown': '#7f7f7f'           # Gray
        }
    
    # Style function
    def style_function(feature):
        category = feature['properties'].get(column, 'unknown')
        return {
            'fillColor': colors.get(category, '#7f7f7f'),
            'color': '#000000',
            'weight': 0.5,
            'fillOpacity': 0.7
        }
    
    # Add GeoJson layer
    tooltip = folium.GeoJsonTooltip(
        fields=['response_area_id', column, 'population', 'incidents_per_1000_pop'],
        aliases=['Response Area:', 'Classification:', 'Population:', 'Incidents/1000:'],
        localize=True
    )
    
    folium.GeoJson(
        gdf,
        style_function=style_function,
        tooltip=tooltip
    ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; 
                background-color: white; padding: 10px; border: 2px solid grey;
                border-radius: 5px; font-size: 14px;">
    <p><strong>Urban Classification</strong></p>
    <p><span style="background-color: #d62728; padding: 2px 10px;"></span> Urban Core</p>
    <p><span style="background-color: #ff7f0e; padding: 2px 10px;"></span> Inner Suburban</p>
    <p><span style="background-color: #2ca02c; padding: 2px 10px;"></span> Outer Suburban</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    m.save(f"outputs/{filename}")
    print(f"    ✓ Saved: outputs/{filename}")


def create_bar_chart(summary_df, filename):
    """Create bar chart comparing incident rates by urban classification"""
    print(f"  Creating: {filename}")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Order categories
    order = ['urban_core', 'inner_suburban', 'outer_suburban']
    summary_df['urban_class'] = pd.Categorical(summary_df['urban_class'], categories=order, ordered=True)
    summary_df = summary_df.sort_values('urban_class')
    
    # Labels
    labels = {
        'urban_core': 'Urban Core\n(>10k/sq mi)',
        'inner_suburban': 'Inner Suburban\n(3-10k/sq mi)',
        'outer_suburban': 'Outer Suburban\n(<3k/sq mi)'
    }
    x_labels = [labels.get(c, c) for c in summary_df['urban_class']]
    
    # Colors
    colors = ['#d62728', '#ff7f0e', '#2ca02c']
    
    # Plot 1: Incidents per 1,000 population
    ax1 = axes[0]
    bars1 = ax1.bar(x_labels, summary_df['incidents_per_1000_pop'], color=colors, edgecolor='black')
    ax1.set_ylabel('Fire Incidents per 1,000 Population', fontsize=12)
    ax1.set_title('Per-Capita Fire Incident Rate', fontsize=14, fontweight='bold')
    ax1.tick_params(axis='x', rotation=0)
    
    # Add value labels
    for bar, val in zip(bars1, summary_df['incidents_per_1000_pop']):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Plot 2: % Single-Family Housing
    ax2 = axes[1]
    bars2 = ax2.bar(x_labels, summary_df['pct_single_family'], color=colors, edgecolor='black')
    ax2.set_ylabel('% Single-Family Housing', fontsize=12)
    ax2.set_title('Housing Typology', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='x', rotation=0)
    
    # Add value labels
    for bar, val in zip(bars2, summary_df['pct_single_family']):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{val:.0f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_scatter_plot(gdf, filename):
    """Create scatter plot of % single-family vs incident rate"""
    print(f"  Creating: {filename}")
    
    # Filter to valid data
    valid = gdf[
        (gdf['population'] > 100) &
        (gdf['pct_single_family'].notna()) &
        (gdf['incidents_per_1000_pop'].notna()) &
        (gdf['urban_class'] != 'unknown')
    ].copy()
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Color by urban class
    colors = {
        'urban_core': '#d62728',
        'inner_suburban': '#ff7f0e',
        'outer_suburban': '#2ca02c'
    }
    
    for urban_class, color in colors.items():
        subset = valid[valid['urban_class'] == urban_class]
        ax.scatter(
            subset['pct_single_family'],
            subset['incidents_per_1000_pop'],
            c=color,
            label=urban_class.replace('_', ' ').title(),
            alpha=0.6,
            s=subset['population'] / 100,  # Size by population
            edgecolors='black',
            linewidth=0.5
        )
    
    # Add trend line
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        valid['pct_single_family'],
        valid['incidents_per_1000_pop']
    )
    
    x_line = [0, 100]
    y_line = [intercept, intercept + slope * 100]
    ax.plot(x_line, y_line, 'k--', alpha=0.5, label=f'Trend (r={r_value:.2f})')
    
    ax.set_xlabel('% Single-Family Housing', fontsize=12)
    ax.set_ylabel('Fire Incidents per 1,000 Population', fontsize=12)
    ax.set_title('Fire Incident Rate vs Housing Typology\n(bubble size = population)', 
                 fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.set_xlim(-5, 105)
    ax.set_ylim(bottom=0)
    
    # Add correlation annotation
    ax.annotate(
        f'Correlation: r = {r_value:.3f}\np-value = {p_value:.4f}',
        xy=(0.95, 0.95),
        xycoords='axes fraction',
        ha='right',
        va='top',
        fontsize=11,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
    )
    
    plt.tight_layout()
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def create_summary_table_image(summary_df, filename):
    """Create a formatted summary table as an image"""
    print(f"  Creating: {filename}")
    
    # Select and rename columns for display
    display_cols = {
        'urban_class': 'Classification',
        'population': 'Population',
        'total_incidents': 'Total Incidents',
        'incidents_per_1000_pop': 'Rate per 1,000 Pop',
        'pct_single_family': '% Single-Family'
    }
    
    table_df = summary_df[[c for c in display_cols.keys() if c in summary_df.columns]].copy()
    table_df.columns = [display_cols[c] for c in table_df.columns]
    
    # Format numbers
    if 'Population' in table_df.columns:
        table_df['Population'] = table_df['Population'].apply(lambda x: f'{x:,.0f}')
    if 'Total Incidents' in table_df.columns:
        table_df['Total Incidents'] = table_df['Total Incidents'].apply(lambda x: f'{x:,.0f}')
    if 'Rate per 1,000 Pop' in table_df.columns:
        table_df['Rate per 1,000 Pop'] = table_df['Rate per 1,000 Pop'].apply(lambda x: f'{x:.2f}')
    if '% Single-Family' in table_df.columns:
        table_df['% Single-Family'] = table_df['% Single-Family'].apply(lambda x: f'{x:.1f}%')
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.axis('off')
    
    table = ax.table(
        cellText=table_df.values,
        colLabels=table_df.columns,
        cellLoc='center',
        loc='center',
        colColours=['#f0f0f0'] * len(table_df.columns)
    )
    
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 1.8)
    
    plt.title('Fire Incident Rates by Urban Classification', fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig(f"outputs/{filename}", dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"    ✓ Saved: outputs/{filename}")


def main():
    print("\n" + "#"*60)
    print("# FIRE RESOURCE ANALYSIS - VISUALIZATION")
    print("#"*60)
    
    # Load data
    ra, summary_urban, summary_housing = load_data()
    
    os.makedirs("outputs", exist_ok=True)
    
    # Create maps
    print("\nCreating maps...")
    
    if HAS_FOLIUM:
        create_choropleth_map(
            ra, 
            'incidents_per_1000_pop',
            'Fire Incidents per 1,000 Population',
            'map_incidents_per_capita.html'
        )
        
        create_categorical_map(
            ra,
            'urban_class',
            'Urban Classification',
            'map_urban_classification.html'
        )
        
        create_choropleth_map(
            ra,
            'pct_single_family',
            '% Single-Family Housing',
            'map_housing_typology.html',
            colormap='RdYlGn_r'
        )
    else:
        print("  Skipping interactive maps (install folium: pip install folium)")
    
    # Create charts
    print("\nCreating charts...")
    
    create_bar_chart(summary_urban, 'chart_urban_comparison.png')
    create_scatter_plot(ra, 'chart_housing_correlation.png')
    create_summary_table_image(summary_urban, 'table_summary.png')
    
    # Summary
    print("\n" + "="*60)
    print("OUTPUTS CREATED")
    print("="*60)
    
    outputs = os.listdir("outputs")
    for f in sorted(outputs):
        print(f"  - outputs/{f}")
    
    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. Review the visualizations:
   - Open outputs/map_incidents_per_capita.html in a browser
   - Open outputs/map_urban_classification.html in a browser
   - Review the PNG charts

2. Prepare the findings brief:
   - Key finding: Do suburban areas have higher per-capita incident rates?
   - Statistical significance: Check outputs/statistical_tests.txt
   - Housing correlation: Does % single-family predict incident rates?

3. Share with Tim for review
""")


if __name__ == "__main__":
    main()

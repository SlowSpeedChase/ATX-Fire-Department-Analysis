# Austin Fire Resource Allocation Analysis

**Research Question:** Do suburban areas in Austin utilize disproportionate fire department resources on a per-capita basis compared to urban areas?

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python scripts/01_download_data.py   # Download all data
python scripts/02_clean_incidents.py  # Clean incident data
python scripts/03_create_crosswalk.py # Create spatial crosswalk
python scripts/04_analysis.py         # Run analysis
python scripts/05_visualize.py        # Generate maps & charts
```

## Project Structure

```
fire_resource_analysis/
├── scripts/
│   ├── 01_download_data.py      # Fetch data from APIs
│   ├── 02_clean_incidents.py    # Clean & classify incidents
│   ├── 03_create_crosswalk.py   # Census tract → response area mapping
│   ├── 04_analysis.py           # Calculate rates & run tests
│   └── 05_visualize.py          # Generate maps & charts
├── raw_data/                     # Downloaded data (created by scripts)
├── processed_data/               # Cleaned/merged data
├── outputs/                      # Final results & visualizations
├── EXECUTION_PLAN.md            # Detailed task breakdown
├── RESEARCH_PLAN.md             # Methodology & data sources
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Data Sources

| Data | Source |
|------|--------|
| Fire Incidents (2018-2024) | Austin Open Data Portal |
| Response Area Boundaries | City of Austin ArcGIS |
| Population by Tract | Census ACS 5-Year (B01003) |
| Housing Units by Type | Census ACS 5-Year (B25024) |

## Key Outputs

- `outputs/summary_by_urban_class.csv` - Incident rates by urban/suburban classification
- `outputs/summary_by_housing_type.csv` - Incident rates by housing typology
- `outputs/statistical_tests.txt` - T-tests and ANOVA results
- `outputs/map_incidents_per_capita.html` - Interactive choropleth map
- `outputs/chart_urban_comparison.png` - Bar chart comparison

## Research Context

This analysis supports the Research Hub's investigation into fire department resource allocation, informed by:
- Single-stair building code discussions
- Fire department aerial equipment requirements
- Pew Research report on multifamily building safety
- Austin budget and zoning debates

## Contact

Research Hub - Austin Housing & Land Use Working Group

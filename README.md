# sprime

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Development Status](https://img.shields.io/badge/status-alpha-orange)](https://github.com/MoCoMakers/sprime)

**sprime** (S' or S prime) is a Python library for analyzing quantitative high-throughput screening (qHTS) data in preclinical drug discovery studies. The library provides tools for processing dose-response curves, fitting Hill equations, and calculating S' values—a single metric that summarizes a drug's dose-response profile relative to a cell line and assay.

## Overview

sprime enables researchers to:

- **Process qHTS data**: Load and analyze dose-response data from screening campaigns
- **Fit Hill curves**: Automatically fit four-parameter logistic (4PL) models to dose-response data
- **Calculate S' values**: Compute S' (S prime) metrics that combine potency and efficacy into a single score
- **Compare cell lines**: Use delta S' (ΔS') to identify compounds with selective activity between reference and test cell lines
- **Rank compounds**: Systematically prioritize drug candidates based on their dose-response profiles

## About S' (S Prime)

S' is a single value score that summarizes a drug's dose-response curve. The metric is calculated from Hill curve parameters using the formula:

**S' = asinh((Upper - Lower) / EC50)**

This is equivalent to:

$$S' = \ln\left(\frac{\text{Upper} - \text{Lower}}{\text{EC50}} + \sqrt{\left(\frac{\text{Upper} - \text{Lower}}{\text{EC50}}\right)^2 + 1}\right)$$

Where:
- **Upper** = Upper asymptote of the dose-response curve
- **Lower** = Lower asymptote of the dose-response curve  
- **EC50** = Half-maximal effect concentration

Higher S' values indicate stronger drug responses (higher efficacy and/or potency). See [Background and Concepts](docs/background_and_concepts.md#the-s-s-prime-metric) for detailed information.

### Delta S' and Comparative Analysis

**Delta S'** (ΔS') enables quantitative comparison of drug responses between different cell lines within a single assay:

**ΔS' = S'(reference cell line) - S'(test cell line)**

This metric allows researchers to:
- Compare drug effects across cell lines
- Rank compounds by selectivity
- Prioritize drug candidates for further investigation

For detailed information and examples, see [Delta S' for Comparative Analysis](docs/background_and_concepts.md#delta-s-for-comparative-analysis).

This library implements **Generation 2** of the S' methodology, which evolved from the original S metric. See the [Citation](#citation) section below for references.

## Installation

### Requirements

- Python 3.8 or higher
- numpy >= 1.20.0, < 3.0
- scipy >= 1.7.0

### Install from PyPI

```bash
pip install sprime
```

### Install from Source

For development or to get the latest version:

```bash
# Clone the repository
git clone https://github.com/MoCoMakers/sprime.git
cd sprime

# Install in editable mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Development Setup

To set up a development environment:

```bash
# Clone the repository
git clone https://github.com/MoCoMakers/sprime.git
cd sprime

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Run tests to verify installation
pytest tests/
```

## Quick Start

The basic workflow in sprime is:

1. **Load** raw data from CSV → `RawDataset`
2. **Process** data (fit curves, calculate S') → `ScreeningDataset`
3. **Analyze** using delta S' for comparative analysis

```python
from sprime import SPrime as sp

# Load raw screening data from CSV
raw_data = sp.load("screening_data.csv")

# Process: fit Hill curves and calculate S' values
screening_data = sp.process(raw_data)

# Export results as list of dictionaries
results = screening_data.to_dict_list()
for profile in results:
    print(f"{profile['compound_name']} vs {profile['cell_line']}: S' = {profile['s_prime']:.2f}")
```

## Usage Examples

### Loading and Processing Screening Data

```python
from sprime import SPrime as sp

# Load raw screening data from CSV
raw_data = sp.load("screening_data.csv")

# Process: fit Hill curves and calculate S' values
screening_data = sp.process(raw_data)

# Export results as list of dictionaries
results = screening_data.to_dict_list()
for profile in results:
    print(f"{profile['compound_name']} vs {profile['cell_line']}: S' = {profile['s_prime']:.2f}")
```

### Calculating Delta S'

Compare drug responses between reference and test cell lines:

```python
# Calculate delta S' = S'(reference) - S'(test)
delta_results = screening_data.calculate_delta_s_prime(
    reference_cell_lines="ipnf05.5 mc",  # e.g., non-tumor tissue
    test_cell_lines=["ipNF96.11C", "ipnf02.3"]  # e.g., tumor cell lines
)

# Access results for each reference cell line
for ref_cellline, comparisons in delta_results.items():
    for comp in comparisons:
        print(f"{comp['compound_name']}: ΔS' = {comp['delta_s_prime']:.2f}")
```

### Working with Individual Profiles

```python
from sprime import DoseResponseProfile, Compound, CellLine, Assay

# Create a dose-response profile
compound = Compound(name="Trifluoperazine", drug_id="NCGC00013226-15")
cell_line = CellLine(name="ipNF96.11C")
assay = Assay(name="HTS002", readout_type="activity")

profile = DoseResponseProfile(
    compound=compound,
    cell_line=cell_line,
    assay=assay,
    concentrations=[1.30E-09, 3.91E-09, 1.17E-08, ...],
    responses=[-63.23, -66.40, -67.04, ...],
    concentration_units="microM"
)

# Fit Hill curve and calculate S'
s_prime = profile.fit_and_calculate_s_prime()
print(f"S' = {s_prime:.2f}")
```

### Working with Pre-calculated Parameters

If your data already has fitted Hill curve parameters:

```python
from sprime import HillCurveParams

# Use pre-calculated parameters
profile.hill_params = HillCurveParams(
    ec50=1.94,
    upper=85.81,
    lower=-64.77,
    r_squared=0.95
)

# Just calculate S'
s_prime = profile.calculate_s_prime()
```

## Key Features

- **Automatic Curve Fitting**: Fits four-parameter logistic (Hill) curves to dose-response data
- **Flexible Input**: Supports raw dose-response data or pre-calculated Hill parameters. When both exist, use `allow_overwrite_hill_coefficients=True` to refit from raw; overwrites are logged as warnings.
- **CSV Loading**: Handles common screening data formats with automatic forward-filling of compound metadata
- **Delta S' Analysis**: Compare drug responses across cell lines within a single assay
- **CSV Export**: Built-in methods to export results and delta S' comparisons to CSV
- **In-Memory Processing**: Process data directly from list of dictionaries without CSV files
- **Metadata Support**: Extracts and preserves metadata (MOA, drug targets) from CSV files
- **Type-Safe**: Uses Python dataclasses and type hints throughout
- **Comprehensive Documentation**: Includes guides for users and detailed technical documentation

## Documentation

### Getting Started

- **[Basic Usage Guide](docs/usage/basic_usage_guide.md)** - Comprehensive step-by-step guide to using sprime with your data, including advanced usage patterns and testing

### Core Concepts

- **[Background and Concepts](docs/background_and_concepts.md)** - Introduction to qHTS, assays, S' metric, and key terminology
- **[Understanding 4PL Dose-Response Curves](docs/README_4PL_Dose_Response.md)** - Detailed explanation of the Hill equation model

### Technical Documentation

- **[Hill Curve Fitting Configuration](docs/usage/hill_curve_fitting_configuration.md)** - Technical details on curve fitting parameters and configuration options

### Examples

- **[Demo Script](docs/usage/demo.py)** - Consolidated demo: S' only (raw -> Hill -> S'), pre-calc only (bypass raw data), and Delta S' (raw -> Hill -> S' -> delta, export tables)

## Requirements

### Runtime Dependencies

- **numpy** >= 1.20.0, < 3.0 - Numerical computing (compatible with numpy 1.x and 2.x)
- **scipy** >= 1.7.0 - Scientific computing and curve fitting

### Development Dependencies

Development dependencies are optional and only needed if you plan to contribute to sprime or run the test suite:

- **pytest** >= 7.0.0 - Testing framework for running the comprehensive test suite
  - Used to execute unit tests, integration tests, and edge case tests
  - Provides test discovery, fixtures, and assertion utilities
  - Required for: `pytest tests/` commands

- **pytest-cov** >= 4.0.0 - Coverage reporting plugin for pytest
  - Generates code coverage reports to identify untested code
  - Used with: `pytest --cov=src/sprime --cov-report=html`
  - Helps ensure comprehensive test coverage during development

**Install development dependencies:**
```bash
pip install -e ".[dev]"
```

These dependencies are not required for normal usage of sprime - only for development and testing.

## Testing

sprime includes a comprehensive test suite. To run tests:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/sprime --cov-report=html

# Run specific test files
pytest tests/test_sprime.py
pytest tests/test_hill_fitting.py
pytest tests/test_integration.py
```

See the [Basic Usage Guide](docs/usage/basic_usage_guide.md#running-the-test-suite) for more testing information.

## Project Status

This project is currently in **active development** (Alpha status). Features and API may change.

### Current Version

The package uses semantic versioning. Version is derived from **Git tags** (via [hatch-vcs](https://github.com/ofek/hatch-vcs)); `src/sprime/_version.py` is generated at build/install time and is not committed. Check the installed version:

```python
import sprime
print(sprime.__version__)
```

**Tagging releases:** Create a Git tag (e.g. `v0.1.0`) and push it. The version used in built packages and on PyPI comes from that tag.

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Contributing

Contributions are welcome! We appreciate your help in making sprime better.

### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** and add tests if applicable
4. **Run the test suite** to ensure everything passes (`pytest tests/`)
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

### Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub:
- [Issue Tracker](https://github.com/MoCoMakers/sprime/issues)

### Questions

For questions or support, please reach out via:
- [MoCo Makers Contact](https://www.mocomakers.com/contact/)
- Open a GitHub Discussion

## Repository

- **GitHub**: [https://github.com/MoCoMakers/sprime](https://github.com/MoCoMakers/sprime)
- **Issues**: [https://github.com/MoCoMakers/sprime/issues](https://github.com/MoCoMakers/sprime/issues)

## Citation

If you use sprime in your research, please cite:

### Generation 2 (S') Methodology

New citations introducing Generation 2 (S') are forthcoming. Please check back for updated citation information.

### Original S Metric

This library implements **Generation 2** of the S' methodology, which evolved from the original S metric described in:

> Zamora PO, Altay G, Santamaria U, Dwarshuis N, Donthi H, Moon CI, Bakalar D, Zamora M. Drug Responses in Plexiform Neurofibroma Type I (PNF1) Cell Lines Using High-Throughput Data and Combined Effectiveness and Potency. *Cancers (Basel)*. 2023 Dec 12;15(24):5811. doi: [10.3390/cancers15245811](https://doi.org/10.3390/cancers15245811). PMID: 38136356; PMCID: PMC10742026.

### Hill Curve Fitting Implementation

The Hill curve fitting implementation in sprime is inspired by the four parameter logistic regression work by Giuseppe Cardillo:

> Giuseppe Cardillo (2025). Four parameters logistic regression - There and back again (https://github.com/dnafinder/logistic4), GitHub. Retrieved December 24, 2025

## Acknowledgments

This library was developed by the **Computational Biology Working Group** at [DMV Petri Dish](https://compbio.dmvpetridish.com/) with support from the nonprofit [DMV Petri Dish](https://www.dmvpetridish.com/). 

We're also part of the DIY tech/science community at [MoCo Makers](https://www.mocomakers.com/).

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Copyright (C) 2026 MoCo Maker Labs LLC

## Support

- **Documentation**: See the [docs](docs/) directory for comprehensive guides
- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/MoCoMakers/sprime/issues)
- **Contact**: Reach out via [MoCo Makers Contact](https://www.mocomakers.com/contact/)

## Related Projects

- [DMV Petri Dish Computational Biology](https://compbio.dmvpetridish.com/) - Computational biology research group
- [MoCo Makers](https://www.mocomakers.com/) - DIY tech/science community

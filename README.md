# MLB Data Analysis

This repository contains a PostgreSQL database and a Python script for analyzing MLB player statistics, specifically focusing on the Los Angeles Dodgers. The project performs data extraction, transformation, and loading (ETL) processes to structure and analyze player performance data.

## Features

- **PostgreSQL Database:** Creates and queries the `LA_Dodgers_Box_Scores` table.
- **SQL Analysis:** Calculates batting averages, on-base percentage (OBP), slugging percentage (SLG), and other key metrics.
- **Ranking Queries:** Ranks players based on their performance.
- **Python Integration:** A Python script extracts, transforms, and loads (ETL) data into the PostgreSQL database.

## Files

- `mlb_data.sql` - Contains SQL queries for creating the database and analyzing player statistics.
- `dodgers_data.py` - Python script for loading data into PostgreSQL and running analyses.
- `dodgers_data.ipynb` - Google Colab notebook for data processing and analysis.

## Getting Started

### Prerequisites

Ensure you have the following installed:
- **PostgreSQL** (for database storage and queries)
- **Python 3** (for running the ETL script)
- Required Python libraries (`psycopg2`, `pandas`, etc.)

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/mlb-data-analysis.git
   cd mlb-data-analysis
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up PostgreSQL and execute `mlb_analysis.sql` to create the database and tables.
4. Run the Python ETL script:
   ```bash
   python etl_script.py
   ```

## Usage

- Modify the Python script to connect to your PostgreSQL instance.
- Run the provided SQL queries to analyze player performance.

## Contributing

Feel free to fork this repository, make enhancements, and submit pull requests.

## Contact

For any questions or suggestions, please open an issue.

---

This project is for educational and analytical purposes.

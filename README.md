# Job Collection System

Robust and modular job scraper following Clean Code and SOLID principles.

## Features

- Multiple Platform Support: Collects jobs from Indeed and Glassdoor
- Clean Data Export: Exports to CSV and JSON with no invalid values
- Modular Architecture: Organized in separate components following SOLID principles
- Unicode Support: Properly handles special characters
- No NaN Values: Aggressive cleaning ensures no NaN in output files
- Duplicate Removal: Automatically removes duplicate job postings
- Rate Limiting Protection: Built-in delays between searches
- Auto-create Output Directory: Automatically creates results folder if needed

## Architecture

The system is organized in modules following Single Responsibility Principle:

```
jobs/
├── src/
│   ├── __init__.py          # Package initialization
│   ├── cleaner.py           # JobDataCleaner class
│   ├── scraper.py           # JobScraper class  
│   ├── exporter.py          # JobDataExporter class
│   └── collector.py         # JobCollector orchestrator
├── results/                 # Output directory (auto-created)
├── main.py                  # Entry point
├── collect_jobs.py          # Legacy/backup
└── README.md                # This file
```

### Modules

**JobDataCleaner** (`src/cleaner.py`)
- Cleans and validates job data
- Removes unnecessary columns
- Eliminates invalid values (NaN, empty strings)

**JobScraper** (`src/scraper.py`)
- Scrapes jobs from multiple platforms (Indeed, Glassdoor)
- Handles search configuration
- Automatically adjusts location for Glassdoor (requires country-level)
- Provides statistics and progress info

**JobDataExporter** (`src/exporter.py`)
- Exports to CSV and JSON formats
- Ensures clean output without NaN
- Handles Unicode correctly
- Auto-creates results directory

**JobCollector** (`src/collector.py`)
- Orchestrates the entire process
- Manages multiple searches
- Handles deduplication
- Coordinates cleaning and export

## Installation

### Prerequisites

Install [uv](https://docs.astral.sh/uv/) - A fast Python package installer and resolver:

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Dependencies

```bash
# Navigate to project directory
cd Jobs-Advertising-Scraper
uv sync
```

## Configuration

The system uses a `config.json` file for easy customization without changing code.

### Quick Setup

1. Install uv (if not already installed):
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

2. Install dependencies:
```bash
uv sync
```

3. Copy the example configuration:
```bash
# Windows
copy config.example.json config.json

# Linux/Mac
cp config.example.json config.json
```

4. Edit `config.json` with your preferences

5. Run the system:
```bash
uv run main.py
```

### Configuration File Structure

```json
{
  "search": {
    "terms": ["QA Engineer", "Test Engineer"],
    "location": "São Paulo",
    "country": "Brazil",
    "platforms": ["indeed", "glassdoor"],
    "results_per_term": 50,
    "days_old": 7
  },
  "output": {
    "directory": "results",
    "filename": "jobs_consolidated"
  },
  "scraping": {
    "delay_between_searches": 10,
    "verbose": 1
  },
  "filters": {
    "job_type": null,
    "is_remote": null
  }
}
```

### Configuration Options

**search.terms** (list of strings)
- Job titles to search for
- Examples: "QA Engineer", "Software Tester", "SDET"
- Multiple terms will be searched sequentially

**search.location** (string)
- Search location (city or country)
- Examples: "São Paulo", "Rio de Janeiro", "Brazil"
- Used for Indeed; auto-adjusted for Glassdoor

**search.country** (string)
- Country name for filtering
- Used for Indeed's country filter and Glassdoor location
- Example: "Brazil"

**search.platforms** (list)
- Platforms to search
- Options: "indeed", "glassdoor", "linkedin", "zip_recruiter"
- Default: ["indeed", "glassdoor"]

**search.results_per_term** (integer)
- Number of jobs to fetch per search term
- Range: 1-100 (recommended: 15-50)
- Higher numbers may trigger rate limiting

**search.days_old** (integer)
- How many days back to search
- Range: 1-365
- Recommended: 7-30 for active jobs

**output.directory** (string)
- Where to save result files
- Default: "results"
- Directory is auto-created if needed

**output.filename** (string)
- Base name for output files
- Timestamp is added automatically
- Example: "jobs_consolidated" becomes "jobs_consolidated_20251024_123456.csv"

**scraping.delay_between_searches** (integer)
- Seconds to wait between searches
- Minimum: 5 (to avoid rate limiting)
- Recommended: 10-15

**scraping.verbose** (integer)
- Logging level
- 0: Silent (no output)
- 1: Basic (recommended)
- 2: Detailed (debug mode)

**filters.job_type** (string or null)
- Filter by employment type
- Options: "fulltime", "parttime", "contract", "internship"
- null: No filter (any type)

**filters.is_remote** (boolean or null)
- Filter remote jobs
- true: Remote only
- false: Office only
- null: Any (remote or office)

## Usage

### Quick Start (Using Configuration File)

```bash
# 1. Create your config file
copy config.example.json config.json

# 2. Edit config.json with your preferences

# 3. Test your configuration (optional but recommended)
uv run test_config.py

# 4. Run the system
uv run main.py
```

The system will:
1. Load configuration from `config.json`
2. Display current settings
3. Search for jobs on specified platforms
4. Clean and deduplicate results
5. Export to CSV and JSON in the results directory

### Simple Execution

```bash
# Using main.py with uv (recommended)
uv run main.py

# Or direct Python execution (requires installed dependencies)
python main.py

# Legacy entry point
uv run collect_jobs.py
```

### Programmatic Usage (Without Config File)

```python
from src.collector import JobCollector

# Initialize with custom output directory
collector = JobCollector(output_dir="my_results", verbose=1)

# Run collection
collector.collect_and_export(
    search_terms=["QA Engineer", "Test Engineer"],
    location="São Paulo",
    country="Brazil",
    platforms=["indeed", "glassdoor"],
    results_per_term=20,
    days_old=30
)
```

### Using Individual Components

```python
from src.scraper import JobScraper
from src.cleaner import JobDataCleaner
from src.exporter import JobDataExporter

# Scrape jobs
scraper = JobScraper(verbose=1)
jobs = scraper.search(
    search_term="QA Engineer",
    location="São Paulo",
    country="Brazil"
)

# Clean data
cleaner = JobDataCleaner()
clean_jobs = cleaner.clean(jobs)

# Export (automatically creates results directory)
exporter = JobDataExporter(output_dir="results")
exporter.export(clean_jobs, "my_jobs")
```

## Design Principles

### Clean Code
- Meaningful names for classes and methods
- Small, focused functions
- Clear comments and docstrings
- No magic numbers
- English language throughout codebase

### SOLID Principles

**Single Responsibility**
- Each class has one reason to change
- Cleaner only cleans, Scraper only scrapes, Exporter only exports

**Open/Closed**
- Classes are open for extension
- Closed for modification through inheritance

**Liskov Substitution**
- Implementations follow contracts
- Can swap implementations without breaking code

**Interface Segregation**
- Small, focused interfaces
- No unnecessary dependencies

**Dependency Inversion**
- Depend on abstractions
- High-level modules don't depend on low-level details

## Output Format

### File Naming
Files are named with timestamp: `{filename}_{YYYYMMDD_HHMMSS}.{ext}`

Example: `jobs_consolidated_20251024_014041.csv`

### Output Location
All files are saved in the directory specified in `config.json` (default: `results/`)

### Exported Columns
Essential job information only (19 columns):
- id, site, job_url, job_url_direct
- title, company, location, date_posted
- job_type, salary_source, interval, min_amount, max_amount, currency
- is_remote, job_level, job_function
- description, skills

Unnecessary company data removed: logo, reviews, revenue, addresses, etc.

### File Formats

**CSV**
- UTF-8 encoding
- Quoted fields for safety
- No NaN values (replaced with empty)

**JSON**
- Pretty-printed (indented)
- UTF-8 encoding with Unicode preserved
- No NaN values (replaced with null)
- No escaped forward slashes
- Human-readable format

## Customization Examples

### Example 1: Search for Remote Python Jobs

```json
{
  "search": {
    "terms": ["Python Developer", "Python Engineer", "Backend Python"],
    "location": "Brazil",
    "country": "Brazil",
    "platforms": ["indeed", "glassdoor"],
    "results_per_term": 30,
    "days_old": 14
  },
  "filters": {
    "job_type": "fulltime",
    "is_remote": true
  }
}
```

### Example 2: Quick Daily Scan

```json
{
  "search": {
    "terms": ["QA Engineer"],
    "location": "São Paulo",
    "country": "Brazil",
    "platforms": ["indeed"],
    "results_per_term": 20,
    "days_old": 1
  },
  "scraping": {
    "delay_between_searches": 5,
    "verbose": 0
  }
}
```

### Example 3: Comprehensive Search

```json
{
  "search": {
    "terms": [
      "QA Engineer",
      "Test Engineer",
      "Software Tester",
      "SDET",
      "QA Automation",
      "Test Analyst"
    ],
    "location": "Brazil",
    "country": "Brazil",
    "platforms": ["indeed", "glassdoor"],
    "results_per_term": 100,
    "days_old": 30
  },
  "scraping": {
    "delay_between_searches": 15,
    "verbose": 2
  }
}
```

## Configuration Best Practices

1. **Start Small**: Begin with 1-2 search terms and low results_per_term
2. **Test Platforms**: Try one platform first, then add others
3. **Respect Rate Limits**: Use delays of 10+ seconds for multiple searches
4. **Backup Config**: Keep your working config.json in version control
5. **Use Specific Terms**: More specific terms yield better results
6. **Adjust Days**: Recent jobs (7 days) for urgent searches, 30+ for comprehensive

## Configuration

Edit `main.py` to configure:

```python
search_terms = ["Your", "Search", "Terms"]
location = "São Paulo"  # City for Indeed
country = "Brazil"      # Country for Indeed and Glassdoor
platforms = ["indeed", "glassdoor"]
results_per_term = 50
days_old = 7
delay_between_searches = 10
output_filename = "jobs_consolidated"
```

## Platform Notes

### Indeed
- Works globally
- Location can be city or country
- Multiple job types supported
- Accepts city-level searches (e.g., "São Paulo")
- **Returns complete job descriptions**
- **Recommended as primary source**

### Glassdoor
- Requires country-level location for best results
- System automatically uses country when Glassdoor is included
- City-level searches converted to country automatically
- Longer periods (30+ days) recommended
- **WARNING: Currently does not return job descriptions**
- **Jobs without descriptions are automatically filtered**
- Consider using Indeed for complete data

## Rate Limiting

- 10 second delay between searches (configurable)
- Automatic handling of multiple searches
- If rate limited, increase delay or wait 15 minutes

## Output Directory

The `results/` directory is automatically created if it doesn't exist.
- All CSV and JSON files are saved there
- Old files are not automatically deleted
- Manage files manually as needed

## Troubleshooting

**Config file not found**
```bash
# Copy the example and customize it
copy config.example.json config.json
```

**Invalid configuration**
```bash
# Test your config before running
uv run test_config.py
```

**Import errors**
```bash
# Make sure uv is installed
uv --version

# Install dependencies
uv sync

# Make sure you're in the jobs directory
cd c:\Users\ed133\Documents\mestrado\pesquisa\jobs

# Run with uv
uv run main.py
```

**No results**
- Check internet connection
- Verify platform accessibility
- Try broader search terms
- Increase days_old parameter

**Glassdoor location errors**
- System now handles this automatically
- Uses country-level location when Glassdoor is included
- If issues persist, set location="Brazil" directly

**Glassdoor missing descriptions**
- This is a known limitation of JobSpy with Glassdoor
- Jobs without descriptions are automatically filtered
- Recommend using Indeed as primary platform
- Or use platforms: ["indeed"] in config.json

**NaN in output**
- Should not happen with current implementation
- All NaN values are aggressively cleaned
- If it occurs, please report as bug

## Files

- `main.py` - Main entry point (uses config.json)
- `test_config.py` - Validate configuration before running
- `config.json` - Your configuration file (create from example, not in git)
- `config.example.json` - Example configuration with all options
- `collect_jobs.py` - Legacy entry point (backup)
- `jobs_scraper.py` - Test script with validation
- `src/` - Modular components
  - `config_loader.py` - Configuration management
  - `collector.py` - Main orchestrator
  - `scraper.py` - Job scraping
  - `cleaner.py` - Data cleaning
  - `exporter.py` - File export
- `results/` - Output directory (auto-created)
- `.gitignore` - Git ignore rules (includes config.json)

## Development

The codebase follows:
- PEP 8 style guidelines
- Type hints where applicable
- Comprehensive docstrings
- Clean Code principles
- SOLID design patterns

## License

MIT License

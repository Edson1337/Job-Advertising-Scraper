"""
Job Collection System
Orchestrates job scraping, cleaning, and export process
"""

from src.collector import JobCollector
from src.config_loader import ConfigLoader
from datetime import datetime


def print_header():
    """Print system header"""
    print("\n" + "+" + "=" * 68 + "+")
    print("|" + " " * 20 + "JOB COLLECTION SYSTEM" + " " * 27 + "|")
    print("|" + " " * 15 + "Robust search across multiple platforms" + " " * 14 + "|")
    print("+" + "=" * 68 + "+")
    print(f"\nDate/Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """
    Main execution function
    Loads configuration and runs the job collection process
    """
    print_header()
    
    # Load configuration
    config = ConfigLoader("config.json")
    config.print_config()
    
    # Create collector
    collector = JobCollector(
        output_dir=config.config['output']['directory'],
        verbose=config.config['scraping']['verbose'],
        proxies=config.config['scraping'].get('proxies', [])
    )
    
    # Execute collection
    search_config = config.get_search_config()
    collector.collect_and_export(
        search_terms=search_config['terms'],
        locations=search_config['locations'],
        platforms=search_config['platforms'],
        results_per_term=search_config['results_per_term'],
        days_old=search_config['days_old'],
        output_filename=config.config['output']['filename'],
        delay_between_searches=config.config['scraping']['delay_between_searches'],
        job_type=config.config['filters']['job_type'],
        is_remote=config.config['filters']['is_remote']
    )


if __name__ == "__main__":
    main()

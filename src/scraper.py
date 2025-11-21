"""
Job scraping module
Handles job collection from multiple platforms
By Edson Moreira (My scraper)
"""

import time
from typing import Optional, List
import pandas as pd
from jobspy import scrape_jobs


class JobScraper:
    """
    Scrapes job postings from multiple platforms
    Provides a clean interface for job search operations
    """
    
    DEFAULT_PLATFORMS = ["indeed", "glassdoor"]
    DEFAULT_COUNTRY = "Brazil"
    DEFAULT_RESULTS = 10
    DEFAULT_DAYS = 30
    DEFAULT_VERBOSE = 1
    
    def __init__(self, verbose: int = DEFAULT_VERBOSE, proxies: Optional[List[str]] = None):
        """
        Initialize the job scraper
        
        Args:
            verbose: Verbosity level (0 = silent, 1 = normal, 2 = debug)
            proxies: List of proxy URLs (optional)
        """
        self.verbose = verbose
        self.proxies = proxies if proxies else []

    def search(
        self,
        search_term: str,
        location: str,
        platforms: Optional[List[str]] = None,
        country: str = DEFAULT_COUNTRY,
        results_wanted: int = DEFAULT_RESULTS,
        days_old: int = DEFAULT_DAYS,
        job_type: Optional[str] = None,
        is_remote: Optional[bool] = None
    ) -> Optional[pd.DataFrame]:
        """
        Search for jobs on specified platforms
        
        Args:
            search_term: Search term (e.g., "QA Engineer")
            location: Location (e.g., "Recife, Pernambuco")
            platforms: List of platforms to search (default: Indeed + Glassdoor)
            country: Country for Indeed filter
            results_wanted: Number of results per platform
            days_old: Maximum age of job postings in days
            job_type: Optional job type filter (e.g., "fulltime")
            is_remote: Optional remote filter (True/False)
            
        Returns:
            DataFrame with job results or None if search fails
        """
        if not platforms:
            platforms = self.DEFAULT_PLATFORMS
        
        # Print configuration
        self._print_search_info(
            search_term, location, platforms, country,
            results_wanted, days_old, job_type, is_remote
        )
        
        try:
            start_time = time.time()
            
            params = self._build_params(
                search_term, location, platforms, country,
                results_wanted, days_old, job_type, is_remote
            )
            
            jobs = scrape_jobs(**params)
            elapsed_time = time.time() - start_time

            self._print_results(jobs, elapsed_time)
            
            return jobs if jobs is not None and len(jobs) > 0 else None
            
        except Exception as e:
            print(f"\nERROR during search: {e}")
            if self.verbose >= 2:
                import traceback
                traceback.print_exc()
            return None

    def _build_params(
        self,
        search_term: str,
        location: str,
        platforms: List[str],
        country: str,
        results_wanted: int,
        days_old: int,
        job_type: Optional[str],
        is_remote: Optional[bool]
    ) -> dict:
        """Build parameters for scrape_jobs function"""
        # Keep the location as passed (works well for most sites)
        final_location = location

        params = {
            "site_name": platforms,
            "search_term": search_term,
            "location": final_location,
            "country_indeed": country,
            "results_wanted": results_wanted,
            "hours_old": days_old * 24,
            "verbose": self.verbose,
            "linkedin_fetch_description": True
        }
        
        # Add proxies if configured
        if self.proxies:
            params["proxies"] = self.proxies
            if self.verbose >= 2:
                print(f"  Using {len(self.proxies)} proxies")
        
        if job_type:
            params["job_type"] = job_type
        if is_remote is not None:
            params["is_remote"] = is_remote
        
        return params

    def _filter_by_search_term(
        self,
        jobs: pd.DataFrame,
        search_term: str
    ) -> pd.DataFrame:
        """
        Local post-filter to ensure the search term actually appears
        in returned jobs (title/description).

        This corrects cases where JobSpy or the platform itself returns
        jobs that are too loosely related to the search term.
        """
        if not search_term:
            return jobs

        normalized = search_term.strip().lower()
        if not normalized:
            return jobs

        def row_matches(row) -> bool:
            cols_to_check = ["title", "description"]
            for col in cols_to_check:
                value = row.get(col)
                if isinstance(value, str) and normalized in value.lower():
                    return True
            return False

        try:
            mask = jobs.apply(row_matches, axis=1)
        except Exception:
            # If unexpected error occurs, don't filter anything
            return jobs

        filtered = jobs[mask]

        if self.verbose >= 1:
            removed = len(jobs) - len(filtered)
            print(f"\nPost-filter by search term '{search_term}':")
            print(f"  - kept: {len(filtered)} jobs")
            print(f"  - removed: {removed} jobs without the term in title/description")

        # If filter removes everything, return original to avoid data loss
        return filtered if len(filtered) > 0 else jobs

    def _print_search_info(
        self,
        search_term: str,
        location: str,
        platforms: List[str],
        country: str,
        results_wanted: int,
        days_old: int,
        job_type: Optional[str],
        is_remote: Optional[bool]
    ) -> None:
        """Print search configuration"""
        if self.verbose == 0:
            return
        
        print("\n" + "=" * 70)
        print("JOB SEARCH")
        print("=" * 70)
        print(f"\nSettings:")
        print(f"  Term: '{search_term}'")
        print(f"  Location: {location}")
        print(f"  Platforms: {', '.join(platforms)}")
        print(f"  Country (Indeed): {country}")
        print(f"  Desired quantity: {results_wanted} per platform")
        print(f"  Period: last {days_old} days")
        
        if job_type:
            print(f"  Type: {job_type}")
        if is_remote is not None:
            print(f"  Remote: {'Yes' if is_remote else 'No'}")
        
        print("\nStarting search...")
    
    def _print_results(self, jobs: pd.DataFrame, elapsed_time: float) -> None:
        """Print search results summary"""
        if self.verbose == 0:
            return
        
        print(f"\nSearch completed in {elapsed_time:.2f} seconds")
        
        if jobs is None:
            print("No data returned from JobSpy.")
            self._print_no_results_help()
            return

        print(f"Total jobs found: {len(jobs)}")
        
        if len(jobs) > 0 and self.verbose >= 1:
            self._print_statistics(jobs)
        elif len(jobs) == 0:
            self._print_no_results_help()
    
    def _print_statistics(self, jobs: pd.DataFrame) -> None:
        """Print job statistics"""
        print(f"\nDistribution by platform:")
        if "site" in jobs.columns:
            count_by_site = jobs["site"].value_counts()
            for platform, count in count_by_site.items():
                print(f"  - {platform}: {count} jobs")
        else:
            print("  Column 'site' not found in DataFrame.")
        
        print(f"\nStatistics:")
        if "company" in jobs.columns:
            print(f"  - Unique companies: {jobs['company'].nunique()}")
        if "location" in jobs.columns:
            print(f"  - Unique locations: {jobs['location'].nunique()}")
        
        if "is_remote" in jobs.columns:
            total_remote = jobs["is_remote"].sum()
            percentage = (total_remote / len(jobs)) * 100 if len(jobs) > 0 else 0
            print(f"  - Remote jobs: {total_remote} ({percentage:.1f}%)")
    
    @staticmethod
    def _print_no_results_help() -> None:
        """Print help message when no results found"""
        print("\nWARNING: No jobs found")
        print("Possible causes:")
        print("  - Search term too specific")
        print("  - Location not recognized by platform")
        print("  - Rate limiting (try again in a few minutes)")

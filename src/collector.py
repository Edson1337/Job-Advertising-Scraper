"""
Job collection orchestrator
Coordinates scraping, cleaning, and exporting operations
"""

import time
from typing import List, Optional
import pandas as pd

from .scraper import JobScraper
from .cleaner import JobDataCleaner
from .exporter import JobDataExporter


class JobCollector:
    """
    Orchestrates the complete job collection process
    Handles scraping, cleaning, deduplication, and export
    """
    
    def __init__(self, output_dir: str = "results", verbose: int = 1, proxies: Optional[list] = None):
        """
        Initialize the job collector
        
        Args:
            output_dir: Directory where results will be saved
            verbose: Verbosity level (0=none, 1=basic, 2=detailed)
            proxies: List of proxy URLs (optional)
        """
        self.scraper = JobScraper(verbose=verbose, proxies=proxies)
        self.cleaner = JobDataCleaner()
        self.exporter = JobDataExporter(output_dir=output_dir, verbose=(verbose > 0))
        self.verbose = verbose
    
    def collect_and_export(
        self,
        search_terms: list,
        locations: list,
        platforms: list,
        results_per_term: int = 10,
        days_old: int = 7,
        output_filename: str = "jobs_dataset",
        delay_between_searches: int = 10,
        job_type: Optional[str] = None,
        is_remote: Optional[bool] = None
    ) -> bool:
        """
        Collect jobs for all search terms and locations, then export results.
        
        Importante: aqui garantimos que **cada chamada** de busca usa
        **apenas um termo**, e fazemos um `for` para percorrer todos
        os termos configurados.
        
        Args:
            search_terms: List of search terms
            locations: List of location dicts with 'location' and 'country' keys
            platforms: List of platforms
            results_per_term: Number of results per term
            days_old: Maximum age of jobs
            output_filename: Base filename for output
            delay_between_searches: Seconds to wait between searches
            job_type: Optional job type filter
            is_remote: Optional remote filter
        """
        self._print_header()
        
        all_jobs: List[pd.DataFrame] = []
        total_searches = len(search_terms) * len(locations)
        current_search = 0
        
        for location_config in locations:
            location = location_config["location"]
            country = location_config["country"]
            
            # UM TERMO POR BUSCA: loop em locations x terms
            for term in search_terms:
                current_search += 1
                self._print_search_header(current_search, total_searches)
                
                jobs = self.scraper.search(
                    search_term=term,
                    location=location,
                    platforms=platforms,
                    country=country,
                    results_wanted=results_per_term,
                    days_old=days_old,
                    job_type=job_type,
                    is_remote=is_remote,
                )
                
                if jobs is not None and not jobs.empty:
                    # metadata da busca
                    jobs["search_term"] = term
                    jobs["search_location"] = location
                    jobs["search_country"] = country
                    all_jobs.append(jobs)
                
                # espera entre buscas (menos na última)
                if current_search < total_searches:
                    self._wait_between_searches(delay_between_searches)
        
        if not all_jobs:
            self._print_no_results_error()
            return False
        
        # Consolidar, deduplicar e exportar
        return self._consolidate_and_export(all_jobs, output_filename)
    
    def _consolidate_and_export(
        self,
        all_jobs: List[pd.DataFrame],
        output_filename: str
    ) -> bool:
        """
        Consolidate results, clean, deduplicate, and export.
        
        Aqui fazemos o "pós": juntamos tudo, removemos duplicatas
        por `id` (se existir), limpamos e exportamos.
        """
        self._print_consolidation_header()
        
        # Juntar todos os resultados
        consolidated = pd.concat(all_jobs, ignore_index=True)
        
        # Remover duplicatas por ID da vaga (se a coluna existir)
        if "id" in consolidated.columns:
            before = len(consolidated)
            unique_jobs = consolidated.drop_duplicates(subset=["id"], keep="first").reset_index(drop=True)
            duplicates_removed = before - len(unique_jobs)
        else:
            # fallback: dedup geral se não tiver coluna 'id'
            before = len(consolidated)
            unique_jobs = consolidated.drop_duplicates().reset_index(drop=True)
            duplicates_removed = before - len(unique_jobs)
        
        self._print_consolidation_stats(consolidated, unique_jobs, duplicates_removed)
        
        # Limpar dados
        clean_jobs = self.cleaner.clean(unique_jobs)
        
        # Exportar
        success = self.exporter.export(clean_jobs, output_filename)
        
        if success:
            print("\nSUCCESS: Collection completed!")
            print("Files generated and ready for analysis")
        else:
            print("\nWARNING: Collection completed but export failed")
        
        print("\n" + "=" * 70)
        return success
    
    def _print_header(self) -> None:
        """Print main header"""
        if self.verbose == 0:
            return
        
        print("\n")
        print("+" + "=" * 68 + "+")
        print("|" + " " * 20 + "JOB COLLECTION SYSTEM" + " " * 27 + "|")
        print("|" + " " * 15 + "Robust search across multiple platforms" + " " * 14 + "|")
        print("+" + "=" * 68 + "+")
        print(f"\nDate/Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def _print_search_header(self, current: int, total: int) -> None:
        """Print header for each search"""
        if self.verbose == 0:
            return
        
        print(f"\n{'=' * 70}")
        print(f"SEARCH {current}/{total}")
        print(f"{'=' * 70}")
    
    def _print_consolidation_header(self) -> None:
        """Print consolidation header"""
        if self.verbose == 0:
            return
        
        print("\n" + "=" * 70)
        print("CONSOLIDATING RESULTS")
        print("=" * 70)
    
    def _print_consolidation_stats(
        self,
        consolidated: pd.DataFrame,
        unique: pd.DataFrame,
        duplicates_removed: int
    ) -> None:
        """Print consolidation statistics"""
        if self.verbose == 0:
            return
        
        print(f"\nConsolidated results:")
        print(f"  Total collected: {len(consolidated)}")
        print(f"  Duplicates removed: {duplicates_removed}")
        print(f"  Unique total: {len(unique)}")
    
    def _wait_between_searches(self, seconds: int) -> None:
        """Wait between searches with message"""
        if self.verbose > 0:
            print(f"\nWaiting {seconds}s before next search...")
        time.sleep(seconds)
    
    @staticmethod
    def _print_no_results_error() -> None:
        """Print error when no results collected"""
        print("\nERROR: No jobs collected")
        print("Check:")
        print("  1. Internet connection")
        print("  2. JobSpy installation: uv add python-jobspy")
        print("  3. Platform rate limiting")

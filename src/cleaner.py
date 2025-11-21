"""
Data cleaning module
Handles data validation and cleaning
"""

from typing import Optional
import pandas as pd


class JobDataCleaner:
    """
    Cleans and validates job posting data
    Removes unnecessary columns and invalid values
    """
    
    ESSENTIAL_COLUMNS = [
        'id',
        'site',
        'job_url',
        'job_url_direct',
        'title',
        'company',
        'location',
        'date_posted',
        'job_type',
        'salary_source',
        'interval',
        'min_amount',
        'max_amount',
        'currency',
        'is_remote',
        'job_level',
        'job_function',
        'description',
        'skills',
        # Metadata columns for multi-location tracking
        'search_term',
        'search_location',
        'search_country'
    ]
    
    def clean(self, jobs: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Clean and validate job data
        
        Args:
            jobs: Raw job dataframe
            
        Returns:
            Cleaned dataframe or None if empty
        """
        if jobs is None or jobs.empty:
            return None
        
        initial_count = len(jobs)
        
        # Remove jobs without description (common issue with Glassdoor)
        if 'description' in jobs.columns:
            jobs = jobs[jobs['description'].notna() & (jobs['description'] != '')]
            removed_count = initial_count - len(jobs)
            
            if removed_count > 0:
                print(f"WARNING: Removed {removed_count} jobs without description ({removed_count/initial_count*100:.1f}%)")
                
                # Show distribution by platform
                if 'site' in jobs.columns:
                    print("  Distribution of removed jobs by platform:")
                    # This is approximate since we already filtered
                    for site in jobs['site'].unique():
                        site_count = len(jobs[jobs['site'] == site])
                        print(f"    - {site}: kept {site_count} jobs")
        
        # Filter only essential columns
        jobs = self._filter_columns(jobs)
        
        # Remove invalid values
        jobs = self._remove_invalid_values(jobs)
        
        return jobs if not jobs.empty else None
    
    def _filter_columns(self, jobs: pd.DataFrame) -> pd.DataFrame:
        """Filter only essential columns that exist in the dataset"""
        available_columns = [col for col in self.ESSENTIAL_COLUMNS if col in jobs.columns]
        return jobs[available_columns].copy()
    
    def _remove_invalid_values(self, jobs: pd.DataFrame) -> pd.DataFrame:
        """Remove all types of invalid values (NaN, empty strings, etc.)"""
        # Replace pandas NA types with None
        jobs = jobs.replace({pd.NA: None, pd.NaT: None})
        jobs = jobs.where(pd.notna(jobs), None)
        
        # Convert to dict for deep cleaning
        jobs_dict = jobs.to_dict(orient='records')
        
        # Clean each record
        for record in jobs_dict:
            self._clean_record(record)
        
        return pd.DataFrame(jobs_dict)
    
    def _clean_record(self, record: dict) -> None:
        """Clean a single job record in-place"""
        for key, value in list(record.items()):
            if value is None:
                continue
                
            # Clean float NaN
            if isinstance(value, float) and self._is_nan(value):
                record[key] = None
            
            # Clean string NaN or empty
            elif isinstance(value, str) and self._is_invalid_string(value):
                record[key] = None
    
    @staticmethod
    def _is_nan(value: float) -> bool:
        """Check if float value is NaN"""
        return value != value or str(value).lower() == 'nan'
    
    @staticmethod
    def _is_invalid_string(value: str) -> bool:
        """Check if string is empty or represents NaN"""
        return value.strip() == '' or value.lower() == 'nan'

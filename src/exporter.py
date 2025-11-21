"""
Data export module
Handles exporting job data to CSV and JSON formats
"""

import os
import csv
import json
from datetime import datetime, date
from pathlib import Path
import pandas as pd


class JobDataExporter:
    """
    Exports job data to CSV and JSON formats
    Ensures clean output without invalid values
    """
    
    DEFAULT_OUTPUT_DIR = "results"
    
    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR, verbose: bool = True):
        """
        Initialize the exporter
        
        Args:
            output_dir: Directory where files will be saved
            verbose: Whether to print export information
        """
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self._ensure_output_directory()
    
    def export(self, jobs: pd.DataFrame, base_filename: str = "jobs") -> bool:
        """
        Export job data to CSV and JSON files
        
        Args:
            jobs: Clean job dataframe
            base_filename: Base name for output files
            
        Returns:
            True if successful, False otherwise
        """
        if jobs is None or jobs.empty:
            if self.verbose:
                print("WARNING: No jobs to export")
            return False
        
        try:
            timestamp = self._generate_timestamp()
            csv_file = self.output_dir / f"{base_filename}_{timestamp}.csv"
            json_file = self.output_dir / f"{base_filename}_{timestamp}.json"
            
            self._print_processing_info(jobs)
            
            # Export files
            self._export_csv(jobs, csv_file)
            self._export_json(jobs, json_file)
            
            # Print summary
            self._print_export_summary(csv_file, json_file, jobs)
            
            return True
            
        except Exception as e:
            print(f"\nERROR exporting: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _export_csv(self, jobs: pd.DataFrame, filename: Path) -> None:
        """Export to CSV format"""
        jobs.to_csv(
            str(filename),
            quoting=csv.QUOTE_NONNUMERIC,
            escapechar="\\",
            index=False
        )
        if self.verbose:
            print(f"\nCSV exported: {filename}")
    
    def _export_json(self, jobs: pd.DataFrame, filename: Path) -> None:
        """Export to JSON format with proper cleaning"""
        jobs_dict = jobs.to_dict(orient='records')
        
        # Final cleanup before JSON serialization
        self._clean_for_json(jobs_dict)
        
        with open(str(filename), 'w', encoding='utf-8') as f:
            json.dump(
                jobs_dict,
                f,
                indent=2,
                ensure_ascii=False,
                default=self._json_serializer,
                allow_nan=False
            )
        
        if self.verbose:
            print(f"JSON exported: {filename}")
    
    def _clean_for_json(self, jobs_dict: list) -> None:
        """Final aggressive NaN cleanup for JSON serialization"""
        for record in jobs_dict:
            for key in list(record.keys()):
                value = record[key]
                
                if value is None:
                    continue
                
                # Clean float NaN
                if isinstance(value, float) and (value != value or str(value).lower() == 'nan'):
                    record[key] = None
                
                # Clean string "NaN"
                elif isinstance(value, str) and value.lower() == 'nan':
                    record[key] = None
    
    @staticmethod
    def _json_serializer(obj):
        """Custom JSON serializer for special types"""
        # Convert dates to ISO format
        if isinstance(obj, (pd.Timestamp, datetime, date)):
            return obj.isoformat()
        
        # Convert None explicitly
        if obj is None:
            return None
        
        # Check float NaN
        if isinstance(obj, float):
            if obj != obj or str(obj).lower() == 'nan':
                return None
        
        # Try pd.isna with fallback
        try:
            if pd.isna(obj):
                return None
        except (ValueError, TypeError):
            pass
        
        raise TypeError(f"Type {type(obj)} is not serializable")
    
    def _print_processing_info(self, jobs: pd.DataFrame) -> None:
        """Print dataset processing information"""
        if not self.verbose:
            return
        
        print(f"\nDataset processed:")
        print(f"  Columns: {len(jobs.columns)}")
        print(f"  Records: {len(jobs)}")
    
    def _print_export_summary(
        self,
        csv_file: Path,
        json_file: Path,
        jobs: pd.DataFrame
    ) -> None:
        """Print export summary with file information"""
        if not self.verbose:
            return
        
        csv_size = csv_file.stat().st_size / 1024
        json_size = json_file.stat().st_size / 1024
        
        print(f"\nFile sizes:")
        print(f"  CSV:  {csv_size:.2f} KB")
        print(f"  JSON: {json_size:.2f} KB")
        
        print(f"\nExported columns ({len(jobs.columns)}):")
        for col in jobs.columns:
            print(f"  - {col}")
        
        print(f"\nFiles saved in: {self.output_dir.absolute()}")
    
    def _ensure_output_directory(self) -> None:
        """Create output directory if it doesn't exist"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.verbose:
            print(f"Output directory: {self.output_dir.absolute()}")
    
    @staticmethod
    def _generate_timestamp() -> str:
        """Generate timestamp for filenames"""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

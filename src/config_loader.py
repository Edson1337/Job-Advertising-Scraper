"""
Configuration loader module
Handles loading and validation of configuration files
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class ConfigLoader:
    """
    Loads and validates configuration from JSON file
    Provides default values and validation
    """
    
    DEFAULT_CONFIG = {
        "search": {
            "terms": ["QA Engineer"],
            "locations": [{"location": "Brazil", "country": "Brazil"}],
            "platforms": ["indeed"],
            "results_per_term": 10,
            "days_old": 7
        },
        "output": {
            "directory": "results",
            "filename": "jobs_dataset"
        },
        "scraping": {
            "delay_between_searches": 10,
            "verbose": 1,
            "proxies": []
        },
        "filters": {
            "job_type": None,
            "is_remote": None
        }
    }
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize config loader
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        if not self.config_path.exists():
            print(f"Config file not found: {self.config_path}")
            print("Using default configuration")
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # Merge with defaults (user config overrides defaults)
            config = self._merge_configs(user_config, self.DEFAULT_CONFIG)
            
            print(f"Configuration loaded from: {self.config_path.absolute()}")
            return config
            
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in config file: {e}")
            print("Using default configuration")
            return self.DEFAULT_CONFIG.copy()
        
        except Exception as e:
            print(f"ERROR loading config: {e}")
            print("Using default configuration")
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_configs(self, user_config: dict, default_config: dict) -> dict:
        """Recursively merge user config with defaults"""
        merged = default_config.copy()
        
        for key, value in user_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(value, merged[key])
            else:
                merged[key] = value
        
        # Handle backward compatibility: convert single location to list
        if 'search' in merged:
            if 'location' in merged['search'] and 'locations' not in merged['search']:
                merged['search']['locations'] = [{
                    'location': merged['search']['location'],
                    'country': merged['search'].get('country', merged['search']['location'])
                }]
                # Remove old keys
                merged['search'].pop('location', None)
                merged['search'].pop('country', None)
        
        return merged
    
    def _validate_config(self) -> None:
        """Validate configuration structure and values"""
        search = self.config.get('search', {})
        
        # Validate search terms
        if not search.get('terms') or not isinstance(search['terms'], list):
            raise ValueError("search.terms must be a non-empty list")
        
        # Validate locations
        if not search.get('locations') or not isinstance(search['locations'], list):
            raise ValueError("search.locations must be a non-empty list")
        
        for loc in search['locations']:
            if not isinstance(loc, dict) or 'location' not in loc or 'country' not in loc:
                raise ValueError(
                    "Each location must be a dict with 'location' and 'country' keys"
                )
        
        # Validate platforms
        if not search.get('platforms') or not isinstance(search['platforms'], list):
            raise ValueError("search.platforms must be a non-empty list")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get config value using dot notation
        
        Args:
            key_path: Path to config value (e.g., "search.terms")
            default: Default value if key not found
            
        Returns:
            Config value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_search_config(self) -> dict:
        """Get complete search configuration"""
        return {
            'terms': self.config['search']['terms'],
            'locations': self.config['search']['locations'],
            'platforms': self.config['search']['platforms'],
            'results_per_term': self.config['search']['results_per_term'],
            'days_old': self.config['search']['days_old']
        }
    
    def get_locations(self) -> list:
        """Get list of location configurations"""
        return self.config['search']['locations']
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get all output configuration"""
        return self.config["output"]
    
    def get_scraping_config(self) -> Dict[str, Any]:
        """Get all scraping configuration"""
        return self.config["scraping"]
    
    def get_filters_config(self) -> Dict[str, Any]:
        """Get all filter configuration"""
        return self.config["filters"]
    
    def print_config(self) -> None:
        """Display current configuration in a formatted way"""
        print("\n" + "=" * 70)
        print("LOADED CONFIGURATION")
        print("=" * 70)
        
        search = self.config['search']
        print(f"\nSearch Configuration:")
        print(f"  Terms ({len(search['terms'])}):")
        for term in search['terms']:
            print(f"    - {term}")
        print(f"  Locations ({len(search['locations'])}):")
        for loc in search['locations']:
            print(f"    - {loc['location']} ({loc['country']})")
        print(f"  Platforms: {', '.join(search['platforms'])}")
        print(f"  Results per term: {search['results_per_term']}")
        print(f"  Days old: {search['days_old']}")
    
    @staticmethod
    def create_example_config(output_path: str = "config.example.json") -> None:
        """Create an example configuration file"""
        example = {
            "_comment": "Job Collection System Configuration",
            "search": {
                "terms": [
                    "QA Engineer",
                    "Test Engineer",
                    "Software Tester",
                    "Quality Assurance Engineer",
                    "Test Automation Engineer"
                ],
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
                "_note": "Set to null to disable filters",
                "job_type": None,
                "is_remote": None
            },
            "_valid_platforms": ["indeed", "glassdoor", "linkedin", "zip_recruiter"],
            "_valid_job_types": ["fulltime", "parttime", "contract", "internship"],
            "_valid_verbose_levels": "0=silent, 1=basic, 2=detailed"
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(example, f, indent=2, ensure_ascii=False)
        
        print(f"Example configuration created: {output_path}")

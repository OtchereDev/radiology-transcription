#!/usr/bin/env python3
"""
Integration with Open Medical Dictionary
Loads and processes external medical dictionaries
"""

import json
import os
from typing import Dict, List, Optional

class OpenMedicalDictionary:
    """Load and integrate open source medical dictionaries"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.medical_dict = {}
        self.radiology_terms = {}
        self.abbreviations = {}
        
        # Load dictionaries
        self.load_dictionaries()
    
    def load_dictionaries(self):
        """Load all available medical dictionaries"""
        try:
            self.medical_dict = self._load_json_file("medical_dict.json")
            self.radiology_terms = self._load_json_file("radiology_terms.json")
            self.abbreviations = self._load_json_file("abbreviations.json")
        except Exception as e:
            print(f"Warning: Could not load medical dictionaries: {e}")
            self._create_fallback_dictionaries()
    
    def _load_json_file(self, filename: str) -> Dict:
        """Load JSON file from data directory"""
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            print(f"Warning: {filepath} not found")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing {filepath}: {e}")
            return {}
    
    def _create_fallback_dictionaries(self):
        """Create basic fallback dictionaries if files aren't available"""
        self.medical_dict = {
            "medical_terms": {
                "cardiovascular": ["heart", "cardiac", "coronary"],
                "pulmonary": ["lung", "pulmonary", "respiratory"],
                "gastrointestinal": ["stomach", "intestinal", "hepatic"],
                "neurological": ["brain", "neurological", "cerebral"]
            }
        }
        
        self.abbreviations = {
            "common_medical": {
                "bp": "blood pressure",
                "hr": "heart rate",
                "ct": "computed tomography",
                "mri": "magnetic resonance imaging"
            }
        }
    
    def get_medical_terms_by_category(self, category: str) -> List[str]:
        """Get medical terms by category"""
        medical_terms = self.medical_dict.get("medical_terms", {})
        return medical_terms.get(category, [])
    
    def get_all_medical_terms(self) -> List[str]:
        """Get all medical terms as flat list"""
        all_terms = []
        medical_terms = self.medical_dict.get("medical_terms", {})
        
        for category_terms in medical_terms.values():
            all_terms.extend(category_terms)
        
        # Add medications and procedures
        all_terms.extend(self.medical_dict.get("medications", []))
        all_terms.extend(self.medical_dict.get("procedures", []))
        
        return list(set(all_terms))
    
    def get_radiology_terms(self) -> Dict[str, List[str]]:
        """Get specialized radiology terms"""
        return self.radiology_terms
    
    def get_abbreviations(self) -> Dict[str, str]:
        """Get flattened abbreviations dictionary"""
        flat_abbrevs = {}
        for category in self.abbreviations.values():
            flat_abbrevs.update(category)
        return flat_abbrevs
    
    def expand_abbreviation(self, abbrev: str) -> Optional[str]:
        """Expand a medical abbreviation"""
        all_abbrevs = self.get_abbreviations()
        return all_abbrevs.get(abbrev.lower())
    
    def search_terms(self, query: str) -> List[str]:
        """Search for terms containing query"""
        query_lower = query.lower()
        all_terms = self.get_all_medical_terms()
        
        matching_terms = [
            term for term in all_terms 
            if query_lower in term.lower()
        ]
        
        return matching_terms
    
    def get_dictionary_stats(self) -> Dict:
        """Get statistics about loaded dictionaries"""
        medical_terms_count = sum(
            len(terms) for terms in self.medical_dict.get("medical_terms", {}).values()
        )
        
        radiology_terms_count = sum(
            len(terms) for terms in self.radiology_terms.values()
        )
        
        abbreviations_count = sum(
            len(abbrevs) for abbrevs in self.abbreviations.values()
        )
        
        return {
            "medical_terms": medical_terms_count,
            "radiology_terms": radiology_terms_count,
            "abbreviations": abbreviations_count,
            "medications": len(self.medical_dict.get("medications", [])),
            "procedures": len(self.medical_dict.get("procedures", [])),
            "total_terms": len(self.get_all_medical_terms())
        }

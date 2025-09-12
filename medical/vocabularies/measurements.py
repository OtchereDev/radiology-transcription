#!/usr/bin/env python3
"""
Measurement Recognition and Processing for Radiology Transcription
Handles various medical measurements, units, and automatic conversions
"""

import re
from typing import Dict, List, Tuple, Optional

class MeasurementProcessor:
    """Process and standardize medical measurements"""
    
    def __init__(self):
        self.units = self._build_units_vocabulary()
        self.measurement_patterns = self._build_measurement_patterns()
        self.conversion_factors = self._build_conversion_factors()
        self.measurement_corrections = self._build_measurement_corrections()
        self.specialized_measurements = self._build_specialized_measurements()
    
    def _build_units_vocabulary(self):
        """Medical measurement units"""
        return {
            'length': {
                'primary': ['millimeter', 'mm', 'centimeter', 'cm', 'meter', 'm'],
                'variations': ['millimeters', 'centimeters', 'meters', 'mms', 'cms']
            },
            'volume': {
                'primary': ['milliliter', 'ml', 'liter', 'l', 'cubic centimeter', 'cc'],
                'variations': ['milliliters', 'liters', 'mls', 'cubic cm', 'cm3']
            },
            'weight': {
                'primary': ['gram', 'g', 'kilogram', 'kg', 'milligram', 'mg'],
                'variations': ['grams', 'kilograms', 'milligrams', 'mgs', 'kgs']
            },
            'angle': {
                'primary': ['degree', 'degrees', '°', 'radian', 'radians'],
                'variations': ['deg', 'degs']
            },
            'density': {
                'primary': ['hounsfield unit', 'hu', 'hounsfield units'],
                'variations': ['housefield unit', 'housefield units', 'hus']
            },
            'radioactivity': {
                'primary': ['becquerel', 'bq', 'curie', 'ci', 'millicurie', 'mci'],
                'variations': ['megabecquerel', 'mbq', 'gigabecquerel', 'gbq']
            },
            'suv': {
                'primary': ['suv', 'standardized uptake value', 'suv max', 'suv mean'],
                'variations': ['standardize uptake value', 'standard uptake value']
            },
            'pressure': {
                'primary': ['mmhg', 'millimeters of mercury', 'pascal', 'pa'],
                'variations': ['mm hg', 'mm of mercury', 'millimeter of mercury']
            },
            'time': {
                'primary': ['second', 'seconds', 'minute', 'minutes', 'hour', 'hours'],
                'variations': ['sec', 'secs', 'min', 'mins', 'hr', 'hrs']
            }
        }
    
    def _build_measurement_patterns(self):
        """Regex patterns for different measurement types"""
        return {
            'basic_measurement': r'(\d+(?:\.\d+)?)\s*(?:x|by|×)\s*(\d+(?:\.\d+)?)\s*(?:x|by|×)?\s*(\d+(?:\.\d+)?)?\s*(mm|cm|m)\b',
            'single_measurement': r'(\d+(?:\.\d+)?)\s*(mm|cm|m|ml|cc|g|kg|mg|degrees?|°|hu)\b',
            'range_measurement': r'(\d+(?:\.\d+)?)\s*(?:to|-)\s*(\d+(?:\.\d+)?)\s*(mm|cm|m|ml|cc|g|kg|mg|degrees?|°|hu)\b',
            'hounsfield_units': r'(\d+)\s*(?:hounsfield units?|hu)\b',
            'suv_values': r'(?:suv|standardized uptake value)\s*(?:max|mean|peak)?\s*(?:of|is|=)?\s*(\d+(?:\.\d+)?)',
            'blood_pressure': r'(\d+)\s*(?:over|/)\s*(\d+)\s*(?:mmhg|mm hg)?\b',
            'fraction': r'(\d+)/(\d+)',
            'percentage': r'(\d+(?:\.\d+)?)%',
            'contrast_timing': r'(\d+)\s*(?:seconds?|minutes?)\s*(?:post|after)\s*(?:contrast|injection)',
            'angle_measurement': r'(\d+(?:\.\d+)?)\s*(?:degrees?|°)\s*(?:of\s*)?(?:angulation|angle|rotation)?',
            'volume_calculation': r'(\d+(?:\.\d+)?)\s*(?:x|×)\s*(\d+(?:\.\d+)?)\s*(?:x|×)\s*(\d+(?:\.\d+)?)\s*=\s*(\d+(?:\.\d+)?)\s*(ml|cc|cm³)',
            'enhancement_timing': r'(\d+)\s*(?:seconds?|minutes?)\s*(?:arterial|venous|delayed|equilibrium)\s*phase'
        }
    
    def _build_conversion_factors(self):
        """Unit conversion factors"""
        return {
            'length': {
                'mm_to_cm': 0.1,
                'cm_to_mm': 10,
                'cm_to_m': 0.01,
                'm_to_cm': 100
            },
            'volume': {
                'ml_to_l': 0.001,
                'l_to_ml': 1000,
                'cc_to_ml': 1,
                'ml_to_cc': 1
            },
            'weight': {
                'mg_to_g': 0.001,
                'g_to_mg': 1000,
                'g_to_kg': 0.001,
                'kg_to_g': 1000
            },
            'radioactivity': {
                'bq_to_mbq': 0.000001,
                'mbq_to_bq': 1000000,
                'ci_to_bq': 37000000000,
                'mci_to_mbq': 37
            }
        }
    
    def _build_measurement_corrections(self):
        """Common speech recognition corrections for measurements"""
        return {
            'millimeter': ['millimeters', 'mill meter', 'milli meter'],
            'centimeter': ['centimeters', 'centi meter'],
            'hounsfield units': ['housefield units', 'hownsfield units', 'hounsfield unit'],
            'standardized uptake value': ['standardize uptake value', 'standard uptake value'],
            'degrees': ['degree', 'deg'],
            'milliliters': ['milliliter', 'mill liter'],
            'cubic centimeter': ['cubic cm', 'cc']
        }
    
    def _build_specialized_measurements(self):
        """Specialized measurements for different imaging modalities"""
        return {
            'ct_measurements': [
                'hounsfield units', 'hu', 'density measurements',
                'attenuation values', 'contrast enhancement',
                'arterial phase enhancement', 'venous phase enhancement',
                'delayed enhancement', 'washout characteristics'
            ],
            'mri_measurements': [
                'signal intensity', 'diffusion coefficient', 'adc values',
                'apparent diffusion coefficient', 'perfusion parameters',
                'cerebral blood flow', 'cbf', 'cerebral blood volume', 'cbv',
                'mean transit time', 'mtt', 't1 relaxation time', 't2 relaxation time'
            ],
            'ultrasound_measurements': [
                'resistive index', 'ri', 'pulsatility index', 'pi',
                'peak systolic velocity', 'psv', 'end diastolic velocity', 'edv',
                'systolic to diastolic ratio', 'sd ratio',
                'intima media thickness', 'imt'
            ],
            'nuclear_measurements': [
                'standardized uptake value', 'suv', 'suv max', 'suv mean',
                'suv peak', 'metabolic tumor volume', 'mtv',
                'total lesion glycolysis', 'tlg', 'target to background ratio',
                'retention index', 'washout rate'
            ],
            'mammography_measurements': [
                'breast density', 'ace', 'almost entirely fatty',
                'scattered fibroglandular', 'heterogeneously dense',
                'extremely dense', 'birads density'
            ],
            'cardiac_measurements': [
                'ejection fraction', 'ef', 'fractional shortening', 'fs',
                'cardiac output', 'co', 'stroke volume', 'sv',
                'left ventricular mass', 'lv mass', 'wall thickness',
                'interventricular septal thickness', 'ivst'
            ]
        }
    
    def process_measurements(self, text: str) -> Tuple[str, List[Dict]]:
        """Process and standardize measurements in text"""
        processed_text = text
        measurements_found = []
        
        # Process different types of measurements
        for pattern_name, pattern in self.measurement_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                measurement_info = self._extract_measurement_info(match, pattern_name)
                if measurement_info:
                    measurements_found.append(measurement_info)
                    # Replace with standardized format
                    standardized = self._standardize_measurement(measurement_info)
                    processed_text = processed_text.replace(match.group(), standardized)
        
        return processed_text, measurements_found
    
    def _extract_measurement_info(self, match, pattern_name: str) -> Optional[Dict]:
        """Extract measurement information from regex match"""
        groups = match.groups()
        
        if pattern_name == 'basic_measurement':
            # Handle 3D measurements like "15 x 12 x 8 mm"
            dims = [float(g) for g in groups[:3] if g is not None]
            unit = groups[-1]
            return {
                'type': 'dimensional',
                'dimensions': dims,
                'unit': unit,
                'original': match.group(),
                'volume': self._calculate_volume(dims) if len(dims) == 3 else None
            }
        
        elif pattern_name == 'single_measurement':
            value = float(groups[0])
            unit = groups[1]
            return {
                'type': 'single',
                'value': value,
                'unit': unit,
                'original': match.group(),
                'converted': self._convert_units(value, unit)
            }
        
        elif pattern_name == 'hounsfield_units':
            value = int(groups[0])
            return {
                'type': 'density',
                'value': value,
                'unit': 'HU',
                'original': match.group(),
                'interpretation': self._interpret_hounsfield(value)
            }
        
        elif pattern_name == 'suv_values':
            value = float(groups[0])
            return {
                'type': 'suv',
                'value': value,
                'unit': 'SUV',
                'original': match.group(),
                'interpretation': self._interpret_suv(value)
            }
        
        elif pattern_name == 'blood_pressure':
            systolic = int(groups[0])
            diastolic = int(groups[1])
            return {
                'type': 'blood_pressure',
                'systolic': systolic,
                'diastolic': diastolic,
                'unit': 'mmHg',
                'original': match.group()
            }
        
        return None
    
    def _calculate_volume(self, dimensions: List[float]) -> float:
        """Calculate volume from dimensions"""
        if len(dimensions) == 3:
            return dimensions[0] * dimensions[1] * dimensions[2]
        return 0
    
    def _convert_units(self, value: float, unit: str) -> Dict:
        """Convert units to standard formats"""
        conversions = {}
        unit_lower = unit.lower()
        
        if unit_lower in ['mm', 'millimeter', 'millimeters']:
            conversions['cm'] = value * 0.1
            conversions['m'] = value * 0.001
        elif unit_lower in ['cm', 'centimeter', 'centimeters']:
            conversions['mm'] = value * 10
            conversions['m'] = value * 0.01
        elif unit_lower in ['ml', 'milliliter', 'milliliters']:
            conversions['l'] = value * 0.001
            conversions['cc'] = value
        
        return conversions
    
    def _interpret_hounsfield(self, value: int) -> str:
        """Interpret Hounsfield unit values"""
        if value < -100:
            return "fat density"
        elif -100 <= value < 0:
            return "low density"
        elif 0 <= value < 20:
            return "water density"
        elif 20 <= value < 40:
            return "soft tissue density"
        elif 40 <= value < 80:
            return "muscle density"
        elif 80 <= value < 200:
            return "high density"
        elif value >= 200:
            return "bone/calcified density"
        else:
            return "density measurement"
    
    def _interpret_suv(self, value: float) -> str:
        """Interpret SUV values"""
        if value < 2.5:
            return "low metabolic activity"
        elif 2.5 <= value < 5.0:
            return "moderate metabolic activity"
        elif 5.0 <= value < 10.0:
            return "high metabolic activity"
        else:
            return "very high metabolic activity"
    
    def _standardize_measurement(self, measurement: Dict) -> str:
        """Standardize measurement format"""
        if measurement['type'] == 'dimensional':
            dims_str = ' × '.join(f"{d:.1f}" for d in measurement['dimensions'])
            result = f"{dims_str} {measurement['unit']}"
            if measurement.get('volume'):
                result += f" (volume: {measurement['volume']:.1f} {measurement['unit']}³)"
            return result
        
        elif measurement['type'] == 'single':
            return f"{measurement['value']:.1f} {measurement['unit']}"
        
        elif measurement['type'] == 'density':
            return f"{measurement['value']} HU ({measurement['interpretation']})"
        
        elif measurement['type'] == 'suv':
            return f"SUV {measurement['value']:.1f} ({measurement['interpretation']})"
        
        elif measurement['type'] == 'blood_pressure':
            return f"{measurement['systolic']}/{measurement['diastolic']} mmHg"
        
        return measurement.get('original', '')
    
    def enhance_measurement_context(self, text: str, measurements: List[Dict]) -> str:
        """Add contextual information to measurements"""
        enhanced_text = text
        
        for measurement in measurements:
            if measurement['type'] == 'dimensional' and len(measurement['dimensions']) == 3:
                volume = measurement['volume']
                if volume and volume > 0:
                    # Add volume information for lesions
                    volume_comment = f" (calculated volume: {volume:.1f} mm³"
                    if volume >= 1000:
                        volume_comment += f" or {volume/1000:.1f} cm³"
                    volume_comment += ")"
                    enhanced_text = enhanced_text.replace(
                        measurement['original'],
                        measurement['original'] + volume_comment
                    )
        
        return enhanced_text
    
    def get_measurement_stats(self) -> Dict:
        """Get statistics about measurement processing capabilities"""
        total_patterns = len(self.measurement_patterns)
        total_units = sum(len(category['primary']) + len(category.get('variations', []))
                         for category in self.units.values())
        total_specialized = sum(len(measurements) 
                             for measurements in self.specialized_measurements.values())
        
        return {
            'total_patterns': total_patterns,
            'total_units': total_units,
            'specialized_measurements': total_specialized,
            'conversion_factors': len(self.conversion_factors),
            'measurement_corrections': len(self.measurement_corrections)
        }
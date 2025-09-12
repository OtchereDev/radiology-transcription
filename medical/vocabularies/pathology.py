#!/usr/bin/env python3
"""
Pathology Terminology for Radiology Transcription
Comprehensive pathological findings and descriptors
"""

class PathologyVocabularies:
    """Pathological terminology and descriptors for radiology"""
    
    def __init__(self):
        self.lesion_descriptors = self._build_lesion_descriptors()
        self.enhancement_patterns = self._build_enhancement_patterns()
        self.morphology_terms = self._build_morphology_terms()
        self.distribution_patterns = self._build_distribution_patterns()
        self.signal_characteristics = self._build_signal_characteristics()
        self.pathology_corrections = self._build_pathology_corrections()
    
    def _build_lesion_descriptors(self):
        """Lesion descriptors for various imaging modalities"""
        return {
            'density_ct': [
                'hypodense', 'hyperdense', 'isodense', 'mixed density',
                'low density', 'high density', 'heterogeneous density',
                'homogeneous density', 'water density', 'fat density',
                'soft tissue density', 'calcific density', 'osseous density'
            ],
            'echogenicity_us': [
                'hypoechoic', 'hyperechoic', 'anechoic', 'isoechoic',
                'echogenic', 'echolucent', 'complex echogenicity',
                'heterogeneous echogenicity', 'homogeneous echogenicity'
            ],
            'signal_mri': [
                'hyperintense', 'hypointense', 'isointense', 'mixed signal',
                'high signal', 'low signal', 'intermediate signal',
                'heterogeneous signal', 'homogeneous signal'
            ],
            'general_descriptors': [
                'well-defined', 'ill-defined', 'sharply defined', 'poorly defined',
                'circumscribed', 'non-circumscribed', 'encapsulated',
                'infiltrative', 'expansile', 'destructive', 'sclerotic',
                'lytic', 'mixed lytic and sclerotic', 'permeative'
            ]
        }
    
    def _build_enhancement_patterns(self):
        """Enhancement patterns for contrast studies"""
        return {
            'enhancement_degree': [
                'enhancing', 'non-enhancing', 'hypoenhancing', 'hyperenhancing',
                'mild enhancement', 'moderate enhancement', 'marked enhancement',
                'intense enhancement', 'avid enhancement', 'minimal enhancement'
            ],
            'enhancement_pattern': [
                'homogeneous enhancement', 'heterogeneous enhancement',
                'rim enhancement', 'peripheral enhancement', 'central enhancement',
                'nodular enhancement', 'linear enhancement', 'septal enhancement',
                'ring enhancement', 'target enhancement', 'spoke-wheel enhancement'
            ],
            'temporal_enhancement': [
                'arterial phase enhancement', 'venous phase enhancement',
                'delayed enhancement', 'persistent enhancement', 'washout',
                'early enhancement', 'late enhancement', 'prolonged enhancement',
                'rapid washout', 'delayed washout', 'no washout'
            ],
            'enhancement_characteristics': [
                'centripetal enhancement', 'centrifugal enhancement',
                'progressive enhancement', 'transient enhancement',
                'plateau enhancement', 'continuous enhancement',
                'discontinuous enhancement', 'patchy enhancement'
            ]
        }
    
    def _build_morphology_terms(self):
        """Morphological descriptors"""
        return {
            'shape': [
                'round', 'oval', 'lobulated', 'multilobulated', 'irregular',
                'spiculated', 'stellate', 'geographic', 'serpiginous',
                'crescentic', 'linear', 'branching', 'nodular', 'plaque-like',
                'mass-like', 'focal', 'diffuse'
            ],
            'margins': [
                'smooth margins', 'irregular margins', 'lobulated margins',
                'spiculated margins', 'well-defined margins', 'ill-defined margins',
                'sharp margins', 'indistinct margins', 'microlobulated margins',
                'obscured margins', 'circumscribed margins'
            ],
            'internal_architecture': [
                'solid', 'cystic', 'complex', 'septated', 'multiloculated',
                'unilocular', 'thick-walled', 'thin-walled', 'debris-filled',
                'fluid-filled', 'air-filled', 'fat-containing', 'calcified',
                'necrotic', 'hemorrhagic'
            ],
            'surface_characteristics': [
                'smooth surface', 'irregular surface', 'bosselated surface',
                'papillary surface', 'villous surface', 'granular surface',
                'coarse surface', 'fine surface', 'nodular surface'
            ]
        }
    
    def _build_distribution_patterns(self):
        """Distribution patterns of pathology"""
        return {
            'spatial_distribution': [
                'symmetric', 'asymmetric', 'bilateral', 'unilateral',
                'focal', 'multifocal', 'diffuse', 'segmental', 'lobar',
                'regional', 'global', 'patchy', 'confluent', 'scattered'
            ],
            'anatomical_distribution': [
                'central', 'peripheral', 'peribronchial', 'perivascular',
                'subpleural', 'periportal', 'centrilobular', 'panlobular',
                'paraseptal', 'random distribution', 'upper lobe predominant',
                'lower lobe predominant', 'basilar predominant'
            ],
            'temporal_distribution': [
                'acute', 'subacute', 'chronic', 'progressive', 'stable',
                'resolving', 'waxing and waning', 'episodic', 'persistent',
                'transient', 'intermittent', 'recurrent'
            ]
        }
    
    def _build_signal_characteristics(self):
        """MRI signal characteristics"""
        return {
            't1_characteristics': [
                't1 hyperintense', 't1 hypointense', 't1 isointense',
                'bright on t1', 'dark on t1', 'intermediate t1 signal',
                't1 shortening', 't1 prolongation'
            ],
            't2_characteristics': [
                't2 hyperintense', 't2 hypointense', 't2 isointense',
                'bright on t2', 'dark on t2', 'intermediate t2 signal',
                't2 shortening', 't2 prolongation', 't2 shine-through'
            ],
            'flair_characteristics': [
                'flair hyperintense', 'flair hypointense', 'flair isointense',
                'flair suppression', 'incomplete flair suppression',
                'bright on flair', 'dark on flair'
            ],
            'dwi_characteristics': [
                'restricted diffusion', 'facilitated diffusion', 'free diffusion',
                'dwi hyperintense', 'dwi hypointense', 'adc dark', 'adc bright',
                'diffusion restriction', 'no diffusion restriction'
            ],
            'susceptibility_characteristics': [
                'susceptibility artifact', 'blooming artifact', 'paramagnetic',
                'diamagnetic', 'ferromagnetic', 'hemosiderin staining',
                'calcification', 'hemorrhage', 'iron deposition'
            ]
        }
    
    def _build_pathology_corrections(self):
        """Common speech recognition corrections for pathology terms"""
        return {
            # Enhancement patterns
            'hypoenhancing': ['hypo enhancing', 'hypoenhanced'],
            'hyperenhancing': ['hyper enhancing', 'hyperenhanced'],
            'rim enhancement': ['rim enhancing', 'peripheral enhancement'],
            'centripetal enhancement': ['centripetal enhancing'],
            'centrifugal enhancement': ['centrifugal enhancing'],
            
            # Morphology
            'lobulated': ['lobular', 'lobu lated'],
            'multilobulated': ['multi lobulated', 'multi lobular'],
            'spiculated': ['spiculate', 'spicular'],
            'septated': ['septate', 'septa ted'],
            'multiloculated': ['multi loculated', 'multi locular'],
            
            # MRI signals
            'hyperintense': ['hyper intense', 'hyperintensity'],
            'hypointense': ['hypo intense', 'hypointensity'],
            'isointense': ['iso intense', 'isointensity'],
            'restricted diffusion': ['restriction diffusion', 'diffusion restricted'],
            'facilitated diffusion': ['facilitated diffusion', 'unrestricted diffusion'],
            
            # CT density
            'hypodense': ['hypo dense', 'hypodensity'],
            'hyperdense': ['hyper dense', 'hyperdensity'],
            'isodense': ['iso dense', 'isodensity'],
            
            # Ultrasound
            'hypoechoic': ['hypo echoic', 'hypoechoaic'],
            'hyperechoic': ['hyper echoic', 'hyperechoaic'],
            'anechoic': ['an echoic', 'anechoaic'],
            'isoechoic': ['iso echoic', 'isoechoaic'],
            
            # General terms
            'well-defined': ['well defined', 'welldefined'],
            'ill-defined': ['ill defined', 'illdefined'],
            'circumscribed': ['circumscribed', 'well circumscribed'],
            'hemorrhagic': ['hemorrhage', 'hemorrhagic'],
            'heterogeneous': ['heterogenous', 'hetero geneous'],
            'homogeneous': ['homogenous', 'homo geneous']
        }
    
    def get_pathology_by_modality(self, modality: str) -> dict:
        """Get pathology terms specific to imaging modality"""
        modality_terms = {}
        
        if modality.lower() in ['ct', 'computed tomography']:
            modality_terms.update({
                'density': self.lesion_descriptors['density_ct'],
                'enhancement': self.enhancement_patterns['enhancement_degree'] + 
                              self.enhancement_patterns['enhancement_pattern'],
                'morphology': self.morphology_terms['shape'] + 
                             self.morphology_terms['margins']
            })
        
        elif modality.lower() in ['mri', 'magnetic resonance']:
            modality_terms.update({
                'signal': self.lesion_descriptors['signal_mri'] + 
                         self.signal_characteristics['t1_characteristics'] + 
                         self.signal_characteristics['t2_characteristics'],
                'enhancement': self.enhancement_patterns['enhancement_degree'] + 
                              self.enhancement_patterns['enhancement_pattern'],
                'diffusion': self.signal_characteristics['dwi_characteristics']
            })
        
        elif modality.lower() in ['ultrasound', 'us', 'sonography']:
            modality_terms.update({
                'echogenicity': self.lesion_descriptors['echogenicity_us'],
                'morphology': self.morphology_terms['shape'] + 
                             self.morphology_terms['internal_architecture']
            })
        
        return modality_terms
    
    def get_all_pathology_terms(self):
        """Get all pathology terms as a flat list"""
        all_terms = []
        
        categories = [
            self.lesion_descriptors, self.enhancement_patterns,
            self.morphology_terms, self.distribution_patterns,
            self.signal_characteristics
        ]
        
        for category in categories:
            for subcategory_terms in category.values():
                all_terms.extend(subcategory_terms)
        
        return list(set(all_terms))
    
    def get_pathology_corrections(self):
        """Get pathology corrections dictionary"""
        return self.pathology_corrections
    
    def classify_finding_severity(self, terms: list) -> str:
        """Classify finding severity based on descriptive terms"""
        high_concern_terms = [
            'irregular', 'spiculated', 'infiltrative', 'destructive',
            'marked enhancement', 'rim enhancement', 'restricted diffusion',
            'heterogeneous enhancement', 'ill-defined', 'invasive'
        ]
        
        moderate_concern_terms = [
            'lobulated', 'heterogeneous', 'complex', 'septated',
            'moderate enhancement', 'peripheral enhancement'
        ]
        
        low_concern_terms = [
            'well-defined', 'circumscribed', 'homogeneous', 'simple',
            'thin-walled', 'smooth', 'no enhancement', 'stable'
        ]
        
        terms_lower = [term.lower() for term in terms]
        
        high_score = sum(1 for term in high_concern_terms if any(term in t for t in terms_lower))
        moderate_score = sum(1 for term in moderate_concern_terms if any(term in t for t in terms_lower))
        low_score = sum(1 for term in low_concern_terms if any(term in t for t in terms_lower))
        
        if high_score > 0:
            return "high_concern"
        elif moderate_score > 0 and low_score == 0:
            return "moderate_concern"
        elif low_score > 0:
            return "low_concern"
        else:
            return "indeterminate"
    
    def get_pathology_stats(self):
        """Get statistics about pathology vocabularies"""
        return {
            'lesion_descriptors': sum(len(terms) for terms in self.lesion_descriptors.values()),
            'enhancement_patterns': sum(len(terms) for terms in self.enhancement_patterns.values()),
            'morphology_terms': sum(len(terms) for terms in self.morphology_terms.values()),
            'distribution_patterns': sum(len(terms) for terms in self.distribution_patterns.values()),
            'signal_characteristics': sum(len(terms) for terms in self.signal_characteristics.values()),
            'pathology_corrections': len(self.pathology_corrections),
            'total_pathology_terms': len(self.get_all_pathology_terms())
        }
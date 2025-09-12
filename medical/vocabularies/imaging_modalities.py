#!/usr/bin/env python3
"""
Imaging Modality Vocabularies for Radiology Transcription
Contains specialized terminology for different imaging modalities
"""

class ImagingVocabularies:
    """Comprehensive imaging modality vocabularies"""
    
    def __init__(self):
        self.ct_vocabulary = self._build_ct_vocabulary()
        self.mri_vocabulary = self._build_mri_vocabulary()
        self.xray_vocabulary = self._build_xray_vocabulary()
        self.ultrasound_vocabulary = self._build_ultrasound_vocabulary()
        self.nuclear_vocabulary = self._build_nuclear_vocabulary()
        self.mammography_vocabulary = self._build_mammography_vocabulary()
        self.interventional_vocabulary = self._build_interventional_vocabulary()
        
        # Common corrections for speech recognition errors
        self.modality_corrections = self._build_modality_corrections()
    
    def _build_ct_vocabulary(self):
        """CT scan terminology"""
        return {
            'techniques': [
                'computed tomography', 'ct scan', 'ct angiography', 'cta',
                'ct urography', 'ctu', 'ct enterography', 'cte',
                'ct colonography', 'ctc', 'ct perfusion', 'ct calcium score',
                'dual energy ct', 'dect', 'spectral ct'
            ],
            'protocols': [
                'non-contrast', 'pre-contrast', 'post-contrast', 'arterial phase',
                'venous phase', 'delayed phase', 'portal venous phase',
                'equilibrium phase', 'nephrographic phase', 'excretory phase',
                'pulmonary embolism protocol', 'pe protocol', 'runoff study',
                'triple phase', 'multiphase'
            ],
            'anatomy_specific': [
                'axial images', 'coronal reformats', 'sagittal reformats',
                'multiplanar reformats', 'mpr', 'maximum intensity projection', 'mip',
                'minimum intensity projection', 'minip', 'volume rendering', 'vrt',
                'curved planar reformats', 'cpr'
            ],
            'findings': [
                'hounsfield units', 'hu', 'hypodense', 'hyperdense', 'isodense',
                'hypoenhancing', 'hyperenhancing', 'enhancing', 'non-enhancing',
                'rim enhancing', 'heterogeneously enhancing', 'homogeneously enhancing'
            ],
            'pathology': [
                'ground glass opacities', 'ggo', 'consolidation', 'atelectasis',
                'pneumothorax', 'pleural effusion', 'mediastinal lymphadenopathy',
                'pulmonary nodule', 'pulmonary mass', 'tree-in-bud',
                'honeycombing', 'traction bronchiectasis'
            ]
        }
    
    def _build_mri_vocabulary(self):
        """MRI sequences and terminology"""
        return {
            'sequences': [
                'magnetic resonance imaging', 'mri', 't1 weighted', 't1w',
                't2 weighted', 't2w', 'flair', 'fluid attenuated inversion recovery',
                'diffusion weighted imaging', 'dwi', 'apparent diffusion coefficient', 'adc',
                'gradient echo', 'gre', 'susceptibility weighted imaging', 'swi',
                'perfusion weighted imaging', 'pwi', 'dynamic susceptibility contrast', 'dsc',
                'dynamic contrast enhanced', 'dce', 'arterial spin labeling', 'asl'
            ],
            'protocols': [
                'pre-gadolinium', 'post-gadolinium', 'gadolinium enhanced',
                'fat saturated', 'fat suppressed', 'stir', 'short tau inversion recovery',
                'chemical shift imaging', 'in-phase', 'out-of-phase',
                'mrcp', 'magnetic resonance cholangiopancreatography',
                'mra', 'magnetic resonance angiography', 'mrv', 'magnetic resonance venography'
            ],
            'findings': [
                'hyperintense', 'hypointense', 'isointense', 'signal intensity',
                'restricted diffusion', 'facilitated diffusion', 'vasogenic edema',
                'cytotoxic edema', 'hemorrhage', 'hemosiderin', 'susceptibility artifact',
                'blooming artifact', 'chemical shift artifact', 'motion artifact'
            ],
            'brain_specific': [
                'white matter lesions', 'periventricular', 'subcortical',
                'corpus callosum', 'brainstem', 'cerebellum', 'basal ganglia',
                'thalamus', 'internal capsule', 'corona radiata',
                'centrum semiovale', 'juxtacortical'
            ],
            'spine_specific': [
                'cervical spine', 'thoracic spine', 'lumbar spine', 'sacral spine',
                'disc herniation', 'disc protrusion', 'disc extrusion',
                'central stenosis', 'foraminal stenosis', 'facet arthropathy',
                'ligamentum flavum', 'posterior longitudinal ligament'
            ]
        }
    
    def _build_xray_vocabulary(self):
        """X-ray terminology and positioning"""
        return {
            'projections': [
                'anteroposterior', 'ap', 'posteroanterior', 'pa', 'lateral',
                'oblique', 'right anterior oblique', 'rao', 'left anterior oblique', 'lao',
                'right posterior oblique', 'rpo', 'left posterior oblique', 'lpo',
                'decubitus', 'right lateral decubitus', 'left lateral decubitus',
                'upright', 'supine', 'prone', 'cross-table lateral'
            ],
            'techniques': [
                'digital radiography', 'dr', 'computed radiography', 'cr',
                'portable radiography', 'bedside radiography',
                'fluoroscopy', 'spot films', 'overhead films',
                'magnification views', 'cone down views'
            ],
            'findings': [
                'radiopaque', 'radiolucent', 'sclerotic', 'lytic',
                'osteopenia', 'osteoporosis', 'osteoarthritis',
                'joint space narrowing', 'osteophytes', 'subchondral sclerosis',
                'fracture', 'dislocation', 'subluxation'
            ],
            'chest_specific': [
                'cardiac silhouette', 'mediastinal contours', 'hilar structures',
                'costophrenic angles', 'cardiophrenic angles', 'aortic arch',
                'pulmonary vessels', 'interstitial markings', 'air bronchograms',
                'kerley b lines', 'cephalization'
            ]
        }
    
    def _build_ultrasound_vocabulary(self):
        """Ultrasound terminology"""
        return {
            'techniques': [
                'ultrasound', 'sonography', 'doppler ultrasound', 'color doppler',
                'power doppler', 'spectral doppler', 'pulsed wave doppler',
                'continuous wave doppler', 'duplex ultrasound',
                'contrast enhanced ultrasound', 'ceus'
            ],
            'findings': [
                'echogenic', 'hypoechoic', 'hyperechoic', 'anechoic', 'isoechoic',
                'heterogeneous', 'homogeneous', 'acoustic shadowing',
                'posterior enhancement', 'reverberation artifact',
                'mirror image artifact', 'side lobe artifact'
            ],
            'measurements': [
                'resistive index', 'ri', 'pulsatility index', 'pi',
                'peak systolic velocity', 'psv', 'end diastolic velocity', 'edv',
                'systolic to diastolic ratio', 'sd ratio'
            ],
            'obstetric': [
                'crown rump length', 'crl', 'biparietal diameter', 'bpd',
                'head circumference', 'hc', 'abdominal circumference', 'ac',
                'femur length', 'fl', 'estimated fetal weight', 'efw',
                'amniotic fluid index', 'afi', 'oligohydramnios', 'polyhydramnios'
            ]
        }
    
    def _build_nuclear_vocabulary(self):
        """Nuclear medicine and PET terminology"""
        return {
            'techniques': [
                'nuclear medicine', 'scintigraphy', 'gamma camera',
                'positron emission tomography', 'pet', 'pet ct', 'pet mri',
                'single photon emission computed tomography', 'spect', 'spect ct'
            ],
            'tracers': [
                'fluorodeoxyglucose', 'fdg', 'technetium', 'tc-99m',
                'iodine-123', 'i-123', 'iodine-131', 'i-131',
                'gallium-67', 'ga-67', 'indium-111', 'in-111',
                'thallium-201', 'tl-201'
            ],
            'measurements': [
                'standardized uptake value', 'suv', 'suv max', 'suv mean',
                'metabolic tumor volume', 'mtv', 'total lesion glycolysis', 'tlg',
                'counts per minute', 'cpm', 'megabecquerel', 'mbq',
                'millicurie', 'mci'
            ],
            'findings': [
                'increased uptake', 'decreased uptake', 'photopenic',
                'hypermetabolic', 'hypometabolic', 'metabolically active',
                'physiologic uptake', 'pathologic uptake', 'background activity'
            ]
        }
    
    def _build_mammography_vocabulary(self):
        """Mammography and breast imaging terminology"""
        return {
            'techniques': [
                'mammography', 'digital mammography', 'tomosynthesis',
                'breast mri', 'breast ultrasound', 'contrast enhanced mammography',
                'cem', 'automated breast ultrasound', 'abus'
            ],
            'positioning': [
                'craniocaudal', 'cc', 'mediolateral oblique', 'mlo',
                'mediolateral', 'ml', 'lateromedial', 'lm',
                'exaggerated craniocaudal', 'xccl', 'spot compression',
                'magnification views', 'rolled views'
            ],
            'birads': [
                'bi-rads', 'breast imaging reporting and data system',
                'bi-rads 0', 'bi-rads 1', 'bi-rads 2', 'bi-rads 3',
                'bi-rads 4', 'bi-rads 5', 'bi-rads 6',
                'incomplete assessment', 'negative', 'benign',
                'probably benign', 'suspicious abnormality', 'highly suggestive of malignancy',
                'known biopsy proven malignancy'
            ],
            'findings': [
                'mass', 'calcifications', 'microcalcifications', 'macrocalcifications',
                'architectural distortion', 'asymmetry', 'developing asymmetry',
                'global asymmetry', 'focal asymmetry', 'skin thickening',
                'nipple retraction', 'trabecular thickening'
            ],
            'descriptors': [
                'round', 'oval', 'irregular', 'lobulated', 'spiculated',
                'circumscribed', 'obscured', 'microlobulated', 'indistinct',
                'amorphous', 'coarse heterogeneous', 'fine pleomorphic',
                'fine linear branching', 'clustered', 'segmental', 'regional',
                'diffuse', 'linear', 'ductal'
            ]
        }
    
    def _build_interventional_vocabulary(self):
        """Interventional radiology terminology"""
        return {
            'procedures': [
                'angioplasty', 'stent placement', 'embolization',
                'chemoembolization', 'tace', 'radioembolization', 'tare',
                'ablation', 'radiofrequency ablation', 'rfa',
                'microwave ablation', 'mwa', 'cryoablation',
                'biopsy', 'fine needle aspiration', 'fna', 'core needle biopsy'
            ],
            'access': [
                'femoral artery', 'radial artery', 'brachial artery',
                'jugular vein', 'subclavian vein', 'femoral vein',
                'micropuncture technique', 'seldinger technique',
                'ultrasound guidance', 'fluoroscopic guidance', 'ct guidance'
            ],
            'devices': [
                'guidewire', 'catheter', 'microcatheter', 'balloon catheter',
                'stent', 'stent graft', 'coils', 'particles', 'plugs',
                'covered stent', 'drug eluting stent', 'bare metal stent'
            ],
            'complications': [
                'hemorrhage', 'hematoma', 'pseudoaneurysm', 'arteriovenous fistula',
                'dissection', 'perforation', 'thrombosis', 'embolism',
                'contrast extravasation', 'contrast nephropathy'
            ]
        }
    
    def _build_modality_corrections(self):
        """Common speech recognition corrections for imaging modalities"""
        return {
            # CT corrections
            'computed tomography': ['computer tomography', 'computed photography'],
            'ct scan': ['cat scan', 'ct can'],
            'hounsfield units': ['hounsfield units', 'housefield units', 'hownsfield units'],
            
            # MRI corrections
            'magnetic resonance imaging': ['magnetic resonant imaging', 'magnetic residence imaging'],
            't1 weighted': ['t one weighted', 'tea one weighted'],
            't2 weighted': ['t two weighted', 'tea two weighted'],
            'flair': ['flare', 'fler'],
            'gadolinium': ['gadolinium', 'gadalinium'],
            
            # General corrections
            'anteroposterior': ['anterior posterior', 'ap'],
            'posteroanterior': ['posterior anterior', 'pa'],
            'mediolateral': ['medio lateral', 'ml'],
            'craniocaudal': ['cranio caudal', 'cc'],
            
            # Ultrasound corrections
            'hypoechoic': ['hypo echoic', 'hypoechoaic'],
            'hyperechoic': ['hyper echoic', 'hyperechoaic'],
            'anechoic': ['an echoic', 'anechoaic'],
            
            # Nuclear medicine corrections
            'fluorodeoxyglucose': ['fluoro deoxyglucose', 'fluorine deoxyglucose'],
            'standardized uptake value': ['standardize uptake value', 'standard uptake value'],
            'positron emission tomography': ['positron emission photography']
        }
    
    def get_all_terms(self):
        """Get all terminology as a flat list for processing"""
        all_terms = []
        
        vocabularies = [
            self.ct_vocabulary, self.mri_vocabulary, self.xray_vocabulary,
            self.ultrasound_vocabulary, self.nuclear_vocabulary,
            self.mammography_vocabulary, self.interventional_vocabulary
        ]
        
        for vocab in vocabularies:
            for category_terms in vocab.values():
                all_terms.extend(category_terms)
        
        return list(set(all_terms))  # Remove duplicates
    
    def get_corrections_dict(self):
        """Get all corrections as a dictionary"""
        return self.modality_corrections
    
    def get_vocabulary_stats(self):
        """Get statistics about loaded vocabularies"""
        return {
            'ct_terms': sum(len(terms) for terms in self.ct_vocabulary.values()),
            'mri_terms': sum(len(terms) for terms in self.mri_vocabulary.values()),
            'xray_terms': sum(len(terms) for terms in self.xray_vocabulary.values()),
            'ultrasound_terms': sum(len(terms) for terms in self.ultrasound_vocabulary.values()),
            'nuclear_terms': sum(len(terms) for terms in self.nuclear_vocabulary.values()),
            'mammography_terms': sum(len(terms) for terms in self.mammography_vocabulary.values()),
            'interventional_terms': sum(len(terms) for terms in self.interventional_vocabulary.values()),
            'total_corrections': len(self.modality_corrections)
        }
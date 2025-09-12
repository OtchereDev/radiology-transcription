#!/usr/bin/env python3
"""
Anatomical Vocabularies for Radiology Transcription
Comprehensive anatomy terminology organized by body systems
"""

class AnatomyVocabularies:
    """Comprehensive anatomical vocabularies for radiology"""
    
    def __init__(self):
        self.cardiovascular = self._build_cardiovascular()
        self.pulmonary = self._build_pulmonary()
        self.gastrointestinal = self._build_gastrointestinal()
        self.genitourinary = self._build_genitourinary()
        self.musculoskeletal = self._build_musculoskeletal()
        self.neurological = self._build_neurological()
        self.endocrine = self._build_endocrine()
        self.hematologic = self._build_hematologic()
        
        # Cross-sectional anatomy
        self.cross_sectional = self._build_cross_sectional()
        
        # Anatomical orientations and landmarks
        self.orientations = self._build_orientations()
        
        # Common anatomy corrections
        self.anatomy_corrections = self._build_anatomy_corrections()
    
    def _build_cardiovascular(self):
        """Cardiovascular system anatomy"""
        return {
            'heart': [
                'heart', 'cardiac', 'myocardium', 'pericardium', 'endocardium',
                'right atrium', 'left atrium', 'right ventricle', 'left ventricle',
                'tricuspid valve', 'mitral valve', 'pulmonary valve', 'aortic valve',
                'interventricular septum', 'interatrial septum', 'apex',
                'coronary arteries', 'left main coronary', 'right coronary artery',
                'left anterior descending', 'lad', 'circumflex', 'posterior descending',
                'cardiac chambers', 'atrial appendage'
            ],
            'vessels': [
                'aorta', 'ascending aorta', 'aortic arch', 'descending aorta',
                'thoracic aorta', 'abdominal aorta', 'aortic root',
                'brachiocephalic trunk', 'left common carotid', 'left subclavian',
                'carotid arteries', 'vertebral arteries', 'basilar artery',
                'circle of willis', 'internal carotid', 'external carotid',
                'subclavian arteries', 'axillary arteries', 'brachial arteries',
                'radial arteries', 'ulnar arteries', 'femoral arteries',
                'popliteal arteries', 'tibial arteries', 'peroneal arteries',
                'superior vena cava', 'inferior vena cava', 'pulmonary veins',
                'jugular veins', 'subclavian veins', 'iliac veins'
            ]
        }
    
    def _build_pulmonary(self):
        """Pulmonary system anatomy"""
        return {
            'airways': [
                'trachea', 'carina', 'main bronchi', 'right main bronchus',
                'left main bronchus', 'lobar bronchi', 'segmental bronchi',
                'subsegmental bronchi', 'bronchioles', 'terminal bronchioles',
                'respiratory bronchioles', 'alveolar ducts', 'alveoli'
            ],
            'lungs': [
                'right lung', 'left lung', 'right upper lobe', 'right middle lobe',
                'right lower lobe', 'left upper lobe', 'left lower lobe',
                'lingula', 'lung apices', 'lung bases', 'costophrenic angles',
                'cardiophrenic angles', 'horizontal fissure', 'oblique fissures',
                'pulmonary hilum', 'hila', 'pleura', 'pleural space',
                'visceral pleura', 'parietal pleura', 'pleural effusion'
            ],
            'mediastinum': [
                'mediastinum', 'anterior mediastinum', 'middle mediastinum',
                'posterior mediastinum', 'superior mediastinum',
                'mediastinal lymph nodes', 'paratracheal nodes', 'hilar nodes',
                'subcarinal nodes', 'aortopulmonary window', 'prevascular space',
                'retrotracheal space', 'paraesophageal space'
            ]
        }
    
    def _build_gastrointestinal(self):
        """Gastrointestinal system anatomy"""
        return {
            'upper_gi': [
                'esophagus', 'gastroesophageal junction', 'stomach', 'gastric fundus',
                'gastric body', 'gastric antrum', 'pylorus', 'duodenum',
                'duodenal bulb', 'duodenal sweep', 'ligament of treitz'
            ],
            'small_bowel': [
                'small bowel', 'small intestine', 'jejunum', 'ileum',
                'terminal ileum', 'ileocecal valve', 'mesentery',
                'small bowel loops', 'jejunal loops', 'ileal loops'
            ],
            'large_bowel': [
                'large bowel', 'colon', 'cecum', 'appendix', 'ascending colon',
                'hepatic flexure', 'transverse colon', 'splenic flexure',
                'descending colon', 'sigmoid colon', 'rectum', 'anal canal',
                'rectosigmoid junction', 'anorectal junction'
            ],
            'liver': [
                'liver', 'hepatic', 'right lobe', 'left lobe', 'caudate lobe',
                'quadrate lobe', 'segment i', 'segment ii', 'segment iii',
                'segment iv', 'segment v', 'segment vi', 'segment vii',
                'segment viii', 'portal vein', 'hepatic artery', 'hepatic veins',
                'right hepatic vein', 'middle hepatic vein', 'left hepatic vein',
                'porta hepatis', 'falciform ligament', 'gallbladder fossa'
            ],
            'biliary': [
                'gallbladder', 'cholecystic', 'gallbladder fundus', 'gallbladder body',
                'gallbladder neck', 'cystic artery', 'cystic duct', 'common hepatic duct',
                'common bile duct', 'cbd', 'intrahepatic bile ducts',
                'right hepatic duct', 'left hepatic duct', 'ampulla of vater',
                'sphincter of oddi'
            ],
            'pancreas': [
                'pancreas', 'pancreatic head', 'uncinate process', 'pancreatic neck',
                'pancreatic body', 'pancreatic tail', 'pancreatic duct',
                'main pancreatic duct', 'accessory pancreatic duct',
                'duct of wirsung', 'duct of santorini'
            ],
            'spleen': [
                'spleen', 'splenic', 'splenic hilum', 'splenic artery',
                'splenic vein', 'short gastric vessels', 'splenorenal ligament',
                'gastrosplenic ligament'
            ]
        }
    
    def _build_genitourinary(self):
        """Genitourinary system anatomy"""
        return {
            'kidneys': [
                'kidneys', 'renal', 'right kidney', 'left kidney',
                'renal cortex', 'renal medulla', 'renal pyramids', 'renal papillae',
                'renal calyces', 'minor calyces', 'major calyces', 'renal pelvis',
                'renal hilum', 'renal sinus', 'renal capsule', 'perinephric fat',
                'paranephric fat', 'gerota fascia', 'renal arteries', 'renal veins'
            ],
            'ureters': [
                'ureters', 'ureteral', 'right ureter', 'left ureter',
                'ureteropelvic junction', 'upj', 'ureterovesical junction', 'uvj',
                'ureteral orifices', 'intramural ureters'
            ],
            'bladder': [
                'bladder', 'urinary bladder', 'bladder wall', 'bladder neck',
                'trigone', 'bladder dome', 'posterior wall', 'lateral walls',
                'anterior wall', 'detrusor muscle'
            ],
            'male': [
                'prostate', 'prostatic', 'prostate gland', 'peripheral zone',
                'transition zone', 'central zone', 'anterior zone',
                'seminal vesicles', 'vas deferens', 'epididymis', 'testicles',
                'testes', 'scrotal contents', 'spermatic cord'
            ],
            'female': [
                'uterus', 'uterine', 'cervix', 'cervical', 'vagina', 'ovaries',
                'fallopian tubes', 'endometrium', 'myometrium', 'parametrium',
                'adnexa', 'pouch of douglas', 'rectovesical pouch'
            ]
        }
    
    def _build_musculoskeletal(self):
        """Musculoskeletal system anatomy"""
        return {
            'spine': [
                'cervical spine', 'thoracic spine', 'lumbar spine', 'sacrum', 'coccyx',
                'c1', 'c2', 'atlas', 'axis', 'odontoid process', 'dens',
                'vertebral bodies', 'spinous processes', 'transverse processes',
                'laminae', 'pedicles', 'facet joints', 'zygapophyseal joints',
                'neural foramina', 'spinal canal', 'central canal',
                'intervertebral discs', 'disc spaces', 'annulus fibrosus',
                'nucleus pulposus', 'ligamentum flavum', 'posterior longitudinal ligament',
                'anterior longitudinal ligament', 'interspinous ligaments',
                'supraspinous ligaments'
            ],
            'extremities': [
                'shoulder', 'humerus', 'radius', 'ulna', 'scapula', 'clavicle',
                'glenohumeral joint', 'acromioclavicular joint', 'sternoclavicular joint',
                'rotator cuff', 'supraspinatus', 'infraspinatus', 'subscapularis', 'teres minor',
                'elbow', 'wrist', 'carpal bones', 'metacarpals', 'phalanges',
                'hip', 'pelvis', 'femur', 'tibia', 'fibula', 'patella',
                'acetabulum', 'femoral head', 'femoral neck', 'greater trochanter',
                'knee', 'menisci', 'cruciate ligaments', 'collateral ligaments',
                'ankle', 'talus', 'calcaneus', 'navicular', 'cuboid', 'cuneiforms',
                'metatarsals', 'toe phalanges'
            ],
            'joints': [
                'synovial joints', 'cartilage', 'joint space', 'joint effusion',
                'synovium', 'joint capsule', 'ligaments', 'tendons',
                'bursae', 'menisci', 'labrum', 'articular cartilage'
            ]
        }
    
    def _build_neurological(self):
        """Neurological system anatomy"""
        return {
            'brain': [
                'brain', 'cerebrum', 'cerebellum', 'brainstem', 'midbrain',
                'pons', 'medulla oblongata', 'frontal lobe', 'parietal lobe',
                'temporal lobe', 'occipital lobe', 'insula', 'limbic system',
                'corpus callosum', 'basal ganglia', 'caudate nucleus', 'putamen',
                'globus pallidus', 'thalamus', 'hypothalamus', 'hippocampus',
                'amygdala', 'internal capsule', 'corona radiata', 'centrum semiovale'
            ],
            'ventricles': [
                'lateral ventricles', 'third ventricle', 'fourth ventricle',
                'cerebral aqueduct', 'aqueduct of sylvius', 'choroid plexus',
                'cerebrospinal fluid', 'csf', 'ventricular system'
            ],
            'vasculature': [
                'circle of willis', 'anterior cerebral artery', 'middle cerebral artery',
                'posterior cerebral artery', 'anterior communicating artery',
                'posterior communicating artery', 'basilar artery', 'vertebral arteries',
                'carotid siphon', 'superior sagittal sinus', 'transverse sinuses',
                'sigmoid sinuses', 'straight sinus', 'confluence of sinuses'
            ],
            'spine_neuro': [
                'spinal cord', 'cervical cord', 'thoracic cord', 'lumbar cord',
                'conus medullaris', 'cauda equina', 'filum terminale',
                'central gray matter', 'white matter tracts', 'nerve roots',
                'dorsal root ganglia'
            ]
        }
    
    def _build_endocrine(self):
        """Endocrine system anatomy"""
        return {
            'glands': [
                'pituitary gland', 'anterior pituitary', 'posterior pituitary',
                'adenohypophysis', 'neurohypophysis', 'infundibulum',
                'thyroid gland', 'thyroid lobes', 'thyroid isthmus',
                'parathyroid glands', 'adrenal glands', 'adrenal cortex',
                'adrenal medulla', 'pancreatic islets', 'islets of langerhans'
            ],
            'thyroid': [
                'right thyroid lobe', 'left thyroid lobe', 'thyroid isthmus',
                'pyramidal lobe', 'thyroglossal duct', 'thyroid nodules',
                'thyroid cartilage', 'cricoid cartilage'
            ]
        }
    
    def _build_hematologic(self):
        """Hematologic and lymphatic anatomy"""
        return {
            'lymph_nodes': [
                'lymph nodes', 'lymphadenopathy', 'cervical lymph nodes',
                'supraclavicular lymph nodes', 'axillary lymph nodes',
                'mediastinal lymph nodes', 'hilar lymph nodes', 'abdominal lymph nodes',
                'mesenteric lymph nodes', 'retroperitoneal lymph nodes',
                'pelvic lymph nodes', 'inguinal lymph nodes'
            ],
            'spleen_hemato': [
                'spleen', 'splenic', 'red pulp', 'white pulp', 'splenic artery',
                'splenic vein', 'accessory spleen', 'splenomegaly'
            ],
            'bone_marrow': [
                'bone marrow', 'red marrow', 'yellow marrow', 'marrow signal',
                'marrow edema', 'marrow infiltration'
            ]
        }
    
    def _build_cross_sectional(self):
        """Cross-sectional anatomy for CT/MRI"""
        return {
            'head_neck': [
                'nasopharynx', 'oropharynx', 'hypopharynx', 'larynx',
                'vocal cords', 'epiglottis', 'aryepiglottic folds',
                'piriform sinuses', 'vallecula', 'tongue base',
                'parotid glands', 'submandibular glands', 'sublingual glands',
                'masticator space', 'parapharyngeal space', 'retropharyngeal space',
                'prevertebral space', 'carotid space'
            ],
            'chest': [
                'suprasternal notch', 'manubrium', 'sternum', 'xiphoid process',
                'intercostal spaces', 'costochondral junctions', 'sternoclavicular joints',
                'thoracic inlet', 'thoracic outlet', 'diaphragm',
                'hemidiaphragms', 'cardiophrenic recesses', 'costophrenic recesses'
            ],
            'abdomen': [
                'retroperitoneum', 'peritoneum', 'peritoneal cavity',
                'mesentery', 'omentum', 'lesser omentum', 'greater omentum',
                'hepatorenal recess', 'paracolic gutters', 'pelvis',
                'rectovesical pouch', 'pouch of douglas', 'presacral space'
            ]
        }
    
    def _build_orientations(self):
        """Anatomical orientations and directional terms"""
        return {
            'directions': [
                'anterior', 'posterior', 'superior', 'inferior', 'medial', 'lateral',
                'proximal', 'distal', 'cranial', 'caudal', 'dorsal', 'ventral',
                'superficial', 'deep', 'central', 'peripheral'
            ],
            'positions': [
                'supine', 'prone', 'lateral', 'decubitus', 'upright', 'seated',
                'standing', 'recumbent', 'trendelenburg', 'reverse trendelenburg',
                'left lateral decubitus', 'right lateral decubitus'
            ],
            'planes': [
                'axial', 'coronal', 'sagittal', 'oblique', 'transverse',
                'frontal plane', 'sagittal plane', 'transverse plane',
                'parasagittal', 'paracoronal'
            ],
            'quadrants': [
                'right upper quadrant', 'ruq', 'right lower quadrant', 'rlq',
                'left upper quadrant', 'luq', 'left lower quadrant', 'llq',
                'epigastrium', 'periumbilical', 'hypogastrium', 'suprapubic'
            ]
        }
    
    def _build_anatomy_corrections(self):
        """Common speech recognition corrections for anatomical terms"""
        return {
            # Cardiovascular
            'myocardium': ['myocardial', 'my cardium'],
            'pericardium': ['peri cardium', 'pericardial'],
            'interventricular septum': ['inter ventricular septum'],
            'left anterior descending': ['left anterior descending artery'],
            
            # Pulmonary
            'costophrenic angles': ['costo phrenic angles', 'cardiophrenic angles'],
            'pleural effusion': ['plural effusion', 'pleural fusion'],
            'pneumothorax': ['pneumo thorax', 'new mo thorax'],
            
            # Gastrointestinal
            'gastroesophageal junction': ['gastro esophageal junction', 'ge junction'],
            'ligament of treitz': ['ligament of trits', 'treitz ligament'],
            'hepatocellular': ['hepato cellular', 'hepatocellular'],
            
            # Genitourinary
            'ureteropelvic junction': ['uretero pelvic junction', 'upj'],
            'ureterovesical junction': ['uretero vesical junction', 'uvj'],
            'perinephric fat': ['peri nephric fat', 'perineal fat'],
            
            # Musculoskeletal
            'zygapophyseal joints': ['zygapophysial joints', 'facet joints'],
            'intervertebral discs': ['inter vertebral discs', 'intervertebral disc'],
            'ligamentum flavum': ['ligamentum flavum', 'ligament flavum'],
            
            # Neurological
            'corpus callosum': ['corpus callosum', 'corpus collosum'],
            'aqueduct of sylvius': ['aqueduct of silvius', 'sylvian aqueduct'],
            'basal ganglia': ['basal ganglion', 'basel ganglia'],
            
            # General anatomical terms
            'peritoneum': ['peritoneal', 'peritonium'],
            'retroperitoneum': ['retro peritoneum', 'retroperitoneal'],
            'lymphadenopathy': ['lymph adenopathy', 'lymphadinopathy']
        }
    
    def get_all_anatomy_terms(self):
        """Get all anatomical terms as a flat list"""
        all_terms = []
        
        systems = [
            self.cardiovascular, self.pulmonary, self.gastrointestinal,
            self.genitourinary, self.musculoskeletal, self.neurological,
            self.endocrine, self.hematologic, self.cross_sectional,
            self.orientations
        ]
        
        for system in systems:
            for category_terms in system.values():
                all_terms.extend(category_terms)
        
        return list(set(all_terms))
    
    def get_anatomy_corrections(self):
        """Get anatomy corrections dictionary"""
        return self.anatomy_corrections
    
    def get_anatomy_stats(self):
        """Get statistics about loaded anatomy vocabularies"""
        return {
            'cardiovascular_terms': sum(len(terms) for terms in self.cardiovascular.values()),
            'pulmonary_terms': sum(len(terms) for terms in self.pulmonary.values()),
            'gastrointestinal_terms': sum(len(terms) for terms in self.gastrointestinal.values()),
            'genitourinary_terms': sum(len(terms) for terms in self.genitourinary.values()),
            'musculoskeletal_terms': sum(len(terms) for terms in self.musculoskeletal.values()),
            'neurological_terms': sum(len(terms) for terms in self.neurological.values()),
            'endocrine_terms': sum(len(terms) for terms in self.endocrine.values()),
            'hematologic_terms': sum(len(terms) for terms in self.hematologic.values()),
            'cross_sectional_terms': sum(len(terms) for terms in self.cross_sectional.values()),
            'orientation_terms': sum(len(terms) for terms in self.orientations.values()),
            'anatomy_corrections': len(self.anatomy_corrections)
        }
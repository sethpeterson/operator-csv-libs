import logging, sys, copy
from .images import Image

class ClusterServiceVersion:


    LATEST_IMAGE_INDICATOR   = '-latest'
    RELATED_IMAGE_IDENTIFIER = 'olm.relatedImage.'

    def __init__(self, csv, name=None, target_version=None, replaces=None, skiprange=None, logger=None):
        self.original_csv = csv
        self.csv = copy.deepcopy(self.original_csv)
    
        self.original_operator_images    = []
        self.operator_images             = []
        self.annotation_related_images   = []
        self.spec_related_images         = []

        # Holds the version information
        self.version = ''
        self.major_minor = ''
        self.versioned_name = ''
        self.replaces = None
        self.skiprange = None
        self.replaces = replaces

        # If name is not provided, we can try extrapolate it
        if name:
            self.name = name
        else:
            self.name = self.csv['metadata']['name'].split('.')[0]

        if skiprange:
            self.skiprange = skiprange
            
        if target_version:
            self.set_version(target_version)

        if logger:
            self.log = logger
        else:
            self._setup_basic_logger()

        # Extract some other useful info
        self._get_operator_images()
        self._get_related_images()

    def set_version(self, version):
        """Set the target version for the CSV

        Arguments:
            version {string} -- Target version in semver format X.Y.Z with optional -nnnn for pre-release
        """
        self.version = version
        self.versioned_name = '{}.v{}'.format(self.name, self.version)
        self._update_version_references()

    def set_replaces(self, replaces):
        """ Set the release that this replaces

        Arguments:
            replaces {string} -- The versioned name of the csv that this csv replaces
        """
        self.replaces = replaces
        self.csv['spec']['replaces'] = self.replaces

    def set_image_pullsecret(self, name):
        """ Set the image pull secret for all operator deployment deployments. Overwrites any existing pull secret

        Arguments:
            name {string|list} -- String or list of strings containing name of the pull secret to add
        """
        if isinstance(name, str):
            p = [{'name': name}]
        else:
            p = [ {'name': x} for x in name ]
        
        for d in self.csv['spec']['install']['spec']['deployments']:
            d['spec']['template']['spec']['imagePullSecrets'] = p

    def add_image_pullsecret(self, name):
        """ Add image pull secret for all operator deployment deployments. Existing pull secrets will be kept

        Arguments:
            name {string|list} -- String or list of strings containing name of the pull secret to add
        """
        if isinstance(name, str):
            p = [{'name': name}]
        else:
            p = [ {'name': x} for x in name ]
        
        for d in self.csv['spec']['install']['spec']['deployments']:
            if not 'imagePullSecrets' in d['spec']['template']['spec']:
                d['spec']['template']['spec']['imagePullSecrets'] = []
            # Add the new pull secrets
            d['spec']['template']['spec']['imagePullSecrets'] = p    

    def generate_spec_relatedImages(self):
        """ Generates spec.relatedImages based on information found in operator deployment annotations marked with 'olm.relatedImage.*'
        """
        self.spec_related_images=self.annotation_related_images
        if 'relatedImages' in self.csv['spec']:
            self.log.debug('Resetting existing spec.relatedImages')
        self.csv['spec']['relatedImages'] = []
        
        # Hold dict of all names and images so we can find conflicting information
        images_validation = {}
        for r in self.spec_related_images:
            if r.name in images_validation:
                self.log.debug('found previous entry for {}'.format(r.name))
                if r.image != images_validation[r.name]:
                    self.log.warning('Validation error: Found different values for {}: {} and {}'.format(r.name, r.image, images_validation[r.name]))
                    self.log.debug('overwriting')
                    self.csv['spec']['relatedImages'][r.name] = r.image
                    continue
            
            self.csv['spec']['relatedImages'].append({
                'name':     r.name,
                'image':    r.image
            })
    
    def get_owned_crds(self):
        """ Returns a list of owned CustomResourceDefinitions

        Returns:
            [list [dict]]: List of owned custom resource definitions as dict object
        """
        return self.csv['spec']['customresourcedefinitions']['owned']

    def get_updated_csv(self):
        """ Returns the updated CSV object

        Returns:
            [dict] -- CSV with updated version and image information
        """
        # Merge in the updates that are done to Operatorimages and Operandimages
        self._update_operator_container_images()
        self._update_operand_images()

        return self.csv

    def get_replaces(self):
        """ Return String

        Returns:
            String -- Returns the csv file name with previous version
        """
        return self.csv['spec']['replaces']

    def get_operator_images(self):
        """ Return a list of images used for operator deployment

        Returns:
            [List of Images] -- Returns a List of Images as defined in Images class
        """
        return self.operator_images

    def get_annotation_related_images(self):
        """ Return a list of images found in 'olm.relatedImages.*' deployment annotations

        Returns:
            [List of Images] -- Returns a List of Images as defined in Images class
        """
        return self.annotation_related_images
      
    def _update_version_references(self):
        """ Update the version specifc fields based on self.version
        """
        self.csv['spec']['version'] = self.version
        self.csv['metadata']['name'] = self.versioned_name
        if len(self.versioned_name) > 63:
            self.log.warning('{} is longer than 63 characters, and may lead to problems'.format(self.name))
        
        if self.skiprange:
            self.csv['metadata']['annotations']['olm.skipRange'] = self.skiprange
        if self.replaces:
            self.csv['spec']['replaces'] = self.replaces
        else:
            if 'replaces' in self.csv['spec']:
                del(self.csv['spec']['replaces'])

    def _get_operator_images(self):
        """[Populate a list of all images that are used for the operator deployment]
        """
        for d in self.csv['spec']['install']['spec']['deployments']:
            for c in d['spec']['template']['spec']['containers']:
                o = Image(
                    deployment = d['name'],
                    container  = c['name'],
                    image      = c['image']
                )
                self.original_operator_images.append(o)
                self.operator_images.append(o)
                
    def _get_related_images(self):
        # Capture related images from annotations
        for d in self.csv['spec']['install']['spec']['deployments']:
            if not 'annotations' in d['spec']['template']['metadata']:
                continue
            for a in d['spec']['template']['metadata']['annotations']:
                if a.startswith(self.RELATED_IMAGE_IDENTIFIER):
                    o = Image(
                        deployment  = d['name'],
                        name        = a.replace(self.RELATED_IMAGE_IDENTIFIER, ''),
                        image       = d['spec']['template']['metadata']['annotations'][a]
                    )
                    self.annotation_related_images.append(o)

    def _update_operator_container_images(self):
        for image in self.operator_images:
            for d in self.csv['spec']['install']['spec']['deployments']:
                if d['name'] == image.deployment:
                    for c in d['spec']['template']['spec']['containers']:
                        if c['name'] == image.container:
                            c['image'] = image.image

    def _update_operand_images(self):
        # Update the annotations that has been updated
        for image in self.annotation_related_images:
            for d in self.csv['spec']['install']['spec']['deployments']:
                if d['name'] == image.deployment:
                    d['spec']['template']['metadata']['annotations'][self.RELATED_IMAGE_IDENTIFIER + image.name] = image.image

    def _setup_basic_logger(self):
        # Setup logging to stdout if we're not provided a logger
        self.log = logging.getLogger(__name__)
        out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S'))
        out_hdlr.setLevel(logging.INFO)
        self.log.addHandler(out_hdlr)
        self.log.setLevel(logging.INFO)
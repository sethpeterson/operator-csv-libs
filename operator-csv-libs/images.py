class Image:
    def __init__(self, name=None, image=None, deployment=None, container=None):
        """Object to hold information about a container or related image

        Keyword Arguments:
            image {string}      -- Image 
            name {string}       -- Name as identified in spec.relatedImages or olm.relatedImage annotatoin
            deployment {string} -- Name of deployment(default: {None})
            container {string}  -- Name of container (default: {None})
                
            

        """
        self.name       = name
        self.image      = image
        self.deployment = deployment
        self.container  = container
        self.tag        = None
        self.digest     = None

        # Everything before the last '/' should make up repo
        self.image_repo = '/'.join(image.split('/')[:-1])
        remainder = image.split('/')[-1]
        if '@' in remainder:
            self.image_name = remainder.split('@')[0]
            self.digest     = remainder.split('@')[1]
        elif ':' in remainder:
            self.image_name = remainder.split(':')[0]
            self.tag        = remainder.split(':')[1]
        else:
            self.image_name = remainder
            self.tag        = 'latest'

    def set_digest(self, digest):
        """Set image digest

        Arguments:
            digest {string} -- Digest in format <type>:<hash>
        """
        if self.digest:
            # If already have a digest set we need to carefully replace
            self.image = self.image.replace(self.digest, digest)
            self.digest = digest
        else:
            self.digest = digest
            # We're assuming that when we're called the existing image doesn't have a digest
            self.image = '{}@{}'.format(self.image.split(':')[0], digest)
        return True

    def set_tag(self, tag):
        """Set new tag for image. Will update self.image only if image is identified by tag, but not overwrite digest

        Arguments:
            tag {String} -- New tag to set
        """
        self.tag = tag
        if not self.digest:
            # We won't overwrite image info if we have digest
            self.image = '{}:{}'.format(self.image.split(':')[0], tag)
    
    def set_image_repo(self, repo):
        self.image      = self.image.replace(self.image_repo, repo)
        self.image_repo = repo
        return True
        
    
    def get_image_repo(self):
        """Returns the image_repo section of the overall image

        Returns:
            [string] -- [image repo i.e. quay.io/myrepo]
        """
        return self.image_repo

    def get_digest(self):
        """Returns image digest 

        Returns:
            [string] -- [digest in format <type>:<hash> ]
        """
        if hasattr(self, 'digest'):
            return self.digest
        else:
            return None

    def get_olm_name(self):
        """Return the name of the image. Typically associated with olm.relatedImage and spec.relatedImages

        Returns:
            [string] -- [Name]
        """
        return self.name
    
    def get_image_name(self):
        """Returns the image name, stripped of repo and tag/digest

        Returns:
            [string] -- [Name]
        """
        return self.image_name
    
    def get_tag(self):
        """Get the tag associated with an image if known

        Returns:
            [string] -- [tag]
        """
        if hasattr(self, 'tag'):
            return self.tag
        else:
            return None
    def get_image(self):
        """Return the full image 

        Returns:
            [string] -- [Full image in format <repo>/<name>[@digest][:tag]]
        """
        return self.image
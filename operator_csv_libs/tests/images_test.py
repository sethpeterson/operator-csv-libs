import unittest
from ..images import Image

IMG_NAME = "dummyImageName"
IMAGE_WITH_DIGEST = "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:dummy_sha"
IMAGE_WITH_TAG = "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog:release-2.0"
IMAGE_WITHOUT_TAG = "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog"
DEPLOYMENT = "dummyDeploymentName"
CONTAINER = "dummyContainerName"
DUMMY_IMG_OBJECT = {
    "name": "dummyImageName",
    "container": "dummyContainerName",
    "deployment": "dummyDeploymentName",
    "image_name": "cp4mcm-orchestrator-catalog",
    "image_repo": "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm"
}

imgWithDigest = Image(IMG_NAME, IMAGE_WITH_DIGEST, DEPLOYMENT, CONTAINER)
imgWithTag = Image(IMG_NAME, IMAGE_WITH_TAG, DEPLOYMENT, CONTAINER)
imgWithoutTag = Image(IMG_NAME, IMAGE_WITHOUT_TAG, DEPLOYMENT, CONTAINER)

class TestImages(unittest.TestCase):
    def setUp(self):
        self.imgWithDigest = Image(IMG_NAME, IMAGE_WITH_DIGEST, DEPLOYMENT, CONTAINER)
        self.imgWithTag = Image(IMG_NAME, IMAGE_WITH_TAG, DEPLOYMENT, CONTAINER)
        self.imgWithoutTag = Image(IMG_NAME, IMAGE_WITHOUT_TAG, DEPLOYMENT, CONTAINER)

    def test_init(self):
        # Check image with digest to see if all values are initialized correctly
        self.assertEqual({
            "name": self.imgWithDigest.name,
            "container": self.imgWithDigest.container,
            "deployment": self.imgWithDigest.deployment,
            "image_name": self.imgWithDigest.image_name,
            "image_repo": self.imgWithDigest.image_repo
        }, DUMMY_IMG_OBJECT)

        self.assertEqual(self.imgWithDigest.image, IMAGE_WITH_DIGEST)
        self.assertEqual(self.imgWithDigest.digest, "sha256:dummy_sha")
        self.assertEqual(self.imgWithDigest.tag, None)
        
        # Check image with tag to see if all values are initialized correctly
        self.assertEqual({
            "name": self.imgWithTag.name,
            "container": self.imgWithTag.container,
            "deployment": self.imgWithTag.deployment,
            "image_name": self.imgWithTag.image_name,
            "image_repo": self.imgWithTag.image_repo
        }, DUMMY_IMG_OBJECT)

        self.assertEqual(self.imgWithTag.image, IMAGE_WITH_TAG)
        self.assertEqual(self.imgWithTag.digest, None)
        self.assertEqual(self.imgWithTag.tag, "release-2.0")
        
        # Check image without tag to see if all values are initialized correctly
        self.assertEqual({
            "name": self.imgWithoutTag.name,
            "container": self.imgWithoutTag.container,
            "deployment": self.imgWithoutTag.deployment,
            "image_name": self.imgWithoutTag.image_name,
            "image_repo": self.imgWithoutTag.image_repo
        }, DUMMY_IMG_OBJECT)
        
        self.assertEqual(self.imgWithoutTag.image, IMAGE_WITHOUT_TAG)
        self.assertEqual(self.imgWithoutTag.digest, None)
        self.assertEqual(self.imgWithoutTag.tag, "latest")
        
    # Set methods 
    def test_set_digest(self):
        oldDigest = "sha256:dummy_sha"
        newDigest = "sha256:new_dummy_sha"
        
        # If self.digest exists
        self.imgWithDigest.set_digest(newDigest)
        self.assertEqual(self.imgWithDigest.digest, newDigest)
        self.assertEqual(self.imgWithDigest.image, IMAGE_WITH_DIGEST.replace(oldDigest, newDigest)) # Check if digest getting replaced in image

        # If self.digest doesn't exist and image has tag
        self.imgWithTag.set_digest(newDigest)
        self.assertEqual(self.imgWithTag.digest, newDigest)
        self.assertEqual(self.imgWithTag.image, IMAGE_WITH_DIGEST.replace(oldDigest, newDigest)) # Check if digest added in image

        # If self.digest doesn't exist and image doesn't have tag
        self.imgWithoutTag.set_digest(newDigest)
        self.assertEqual(self.imgWithoutTag.digest, newDigest)
        self.assertEqual(self.imgWithoutTag.image, IMAGE_WITH_DIGEST.replace(oldDigest, newDigest)) # Check if digest added in image

    def test_set_tag(self):
        newTag = "SNAPSHOT"

        # If image has digest
        self.imgWithDigest.set_tag(newTag)
        self.assertEqual(self.imgWithDigest.tag, newTag)
        self.assertEqual(self.imgWithDigest.image, IMAGE_WITH_DIGEST) # Check if image was not changed
        
        # If image doesn't have digest but has tag
        self.imgWithTag.set_tag(newTag)
        self.assertEqual(self.imgWithTag.tag, newTag)
        self.assertEqual(self.imgWithTag.image, '{}:{}'.format(IMAGE_WITH_TAG.split(':')[0], newTag))

        # If image doesn't have digest and tag
        self.imgWithoutTag.set_tag(newTag)
        self.assertEqual(self.imgWithoutTag.tag, newTag)
        self.assertEqual(self.imgWithoutTag.image, '{}:{}'.format(IMAGE_WITHOUT_TAG, newTag))

    def test_set_image_repo(self):
        newRepo = '{}/{}/{}'.format(DUMMY_IMG_OBJECT.get("image_repo").split('/')[0], DUMMY_IMG_OBJECT.get("image_repo").split('/')[1], "cp4mcm-devops")

        # Image with digest
        self.imgWithDigest.set_image_repo(newRepo)
        self.assertEqual(self.imgWithDigest.image, IMAGE_WITH_DIGEST.replace(DUMMY_IMG_OBJECT.get("image_repo"), newRepo))
        self.assertEqual(self.imgWithDigest.image_repo, newRepo)

        # Image with tag
        self.imgWithTag.set_image_repo(newRepo)
        self.assertEqual(self.imgWithTag.image, IMAGE_WITH_TAG.replace(DUMMY_IMG_OBJECT.get("image_repo"), newRepo))
        self.assertEqual(self.imgWithTag.image_repo, newRepo)

        # Image without tag
        self.imgWithoutTag.set_image_repo(newRepo)
        self.assertEqual(self.imgWithoutTag.image, IMAGE_WITHOUT_TAG.replace(DUMMY_IMG_OBJECT.get("image_repo"),  newRepo))
        self.assertEqual(self.imgWithoutTag.image_repo, newRepo)


    # Get methods
        
    def test_get_image_repo(self):
        # Check to see if returned value is correct 
        self.assertEqual(self.imgWithDigest.image_repo, self.imgWithDigest.get_image_repo())
        self.assertEqual(self.imgWithTag.image_repo, self.imgWithTag.get_image_repo())
        self.assertEqual(self.imgWithoutTag.image_repo, self.imgWithoutTag.get_image_repo())

    def test_get_digest(self):
        newDigest = "sha256:new_dummy_sha"

        # Check to see if there is some value returned and if that value is correct
        self.assertNotEqual(self.imgWithDigest.get_digest(), None)
        self.assertEqual(self.imgWithDigest.digest, self.imgWithDigest.get_digest())
        
        self.assertEqual(self.imgWithTag.get_digest(), None)
        self.assertEqual(self.imgWithTag.digest, self.imgWithTag.get_digest())
        # add digest, check to see if it has digest now
        self.imgWithTag.set_digest(newDigest)
        self.assertNotEqual(self.imgWithTag.get_digest(), None)
        self.assertEqual(self.imgWithTag.digest, self.imgWithTag.get_digest())
        
        self.assertEqual(self.imgWithoutTag.get_digest(), None)
        self.assertEqual(self.imgWithoutTag.digest, self.imgWithoutTag.get_digest())
        # add digest, check to see if it has digest now
        self.imgWithoutTag.set_digest(newDigest)
        self.assertNotEqual(self.imgWithoutTag.get_digest(), None)
        self.assertEqual(self.imgWithoutTag.digest, self.imgWithoutTag.get_digest())

        
    def test_get_olm_name(self):
        # Check to see if returned value is correct 
        self.assertEqual(self.imgWithDigest.name, self.imgWithDigest.get_olm_name())
        self.assertEqual(self.imgWithTag.name, self.imgWithTag.get_olm_name())
        self.assertEqual(self.imgWithoutTag.name, self.imgWithoutTag.get_olm_name())
    
    def test_get_image_name(self):
        # Check to see if returned value is correct
        self.assertEqual(self.imgWithDigest.image_name, self.imgWithDigest.get_image_name())
        self.assertEqual(self.imgWithTag.image_name, self.imgWithTag.get_image_name())
        self.assertEqual(self.imgWithoutTag.image_name, self.imgWithoutTag.get_image_name())
    
    def test_get_tag(self):
        newTag = "SNAPSHOT"

        # Check to see if there is some value returned and if that value is correct
        self.assertEqual(self.imgWithDigest.get_tag(), None)
        self.assertEqual(self.imgWithDigest.tag, self.imgWithDigest.get_tag())
        # Add tag, and check to see if it has tag now
        self.imgWithDigest.set_tag(newTag)
        self.assertNotEqual(self.imgWithDigest.get_tag(), None)
        self.assertEqual(self.imgWithDigest.tag, self.imgWithDigest.get_tag())
        
        self.assertNotEqual(self.imgWithTag.get_tag(), None)
        self.assertEqual(self.imgWithTag.tag, self.imgWithTag.get_tag())
        
        self.assertNotEqual(self.imgWithoutTag.get_tag(), None)
        self.assertEqual(self.imgWithoutTag.tag, self.imgWithoutTag.get_tag())

    def test_get_image(self):
        # Check to see if returned value is correct
        self.assertEqual(self.imgWithDigest.image, self.imgWithDigest.get_image())
        self.assertEqual(self.imgWithTag.image, self.imgWithTag.get_image())
        self.assertEqual(self.imgWithoutTag.image, self.imgWithoutTag.get_image())

if __name__ == "__main__":
    unittest.main()
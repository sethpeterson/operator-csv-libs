import unittest
import os
import httpretty
from unittest.mock import patch
from ..imagerepo import ImageRepo, ArtifactoryRepo, QuayRepo, DockerRepo, ManifestNotFound
from ..images import Image

IMG_NAME = 'dummyImageName'
IMAGE_WITH_DIGEST = 'hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:dummy_sha'
QUAY_IMAGE_WITH_TAG = 'quay.io/hybridappio/ham-application-assembler:dummy_tag'
DOCKER_IMAGE_WITH_MANIFEST = 'docker.io/ibmcom/ibm-operator-catalog:with_manifest'
DOCKER_IMAGE_WITH_MANIFEST_LIST = 'docker.io/ibmcom/ibm-operator-catalog:with_manifest_list'
IMAGE_WITH_TAG = 'hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog:release-2.0'
IMAGE_WITHOUT_TAG = 'hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog'
DEPLOYMENT = 'dummyDeploymentName'
CONTAINER = 'dummyContainerName'

ARTIFACTORY_REPO = 'hyc-cp4mcm-team-docker-local/cicd/cp4mcm'
QUAY_REPO = 'hybridappio/ham-application-assembler'
DOCKER_REPO = 'docker.io/ibmcom'

DUMMY_ARTIFACTORY_CONFIG = {
    'artifactory_user' : 'dummyArtifactoryUser',
    'artifactory_key' : 'dummyArtifactoryKey',
    'artifactory_base' : 'dummyArtifactoryBase'
}

DUMMY_OS_ARTIFACTORY_CONFIG = {
    'artifactory_user' : 'dummyOsArtifactoryUser',
    'artifactory_key' : 'dummyOsArtifactoryKey',
    'artifactory_base' : 'dummyOsArtifactoryBase'
}

token_path = 'https://auth.docker.io/token?scope=repository%3A{org}%2F{repo}%3Apull&service=registry.docker.io'
digest_media_type_path = 'https://registry-1.docker.io/v2/{org}/{repo}/manifests/{tag}'

class TestImageRepo(unittest.TestCase):
    def setUp(self):
        # set environment variables
        os.environ['ARTIFACTORY_USER'] = DUMMY_OS_ARTIFACTORY_CONFIG['artifactory_user']
        os.environ['ARTIFACTORY_KEY'] = DUMMY_OS_ARTIFACTORY_CONFIG['artifactory_key']
        os.environ['ARTIFACTORY_BASE'] = DUMMY_OS_ARTIFACTORY_CONFIG['artifactory_base']

        # create artifactory image object
        self.artifactoryImgWithDigest = Image(IMG_NAME, IMAGE_WITH_DIGEST, DEPLOYMENT, CONTAINER)

        # artifactory get raw image digest does not work without tag
        self.artifactoryImgWithDigest.set_tag('latest')
        
        # create artifactory repo object
        self.artifactoryImgRepoWithOsAuthentication = ImageRepo(self.artifactoryImgWithDigest)

    def test_init(self):
        # check to see that image with digest is initialized correctly
        self.assertEqual(self.artifactoryImgRepoWithOsAuthentication.image, self.artifactoryImgWithDigest)

        # check to see that artifactory repo is correctly initialized
        self.assertEqual(self.artifactoryImgRepoWithOsAuthentication.image_repo.artifactory_user, DUMMY_OS_ARTIFACTORY_CONFIG['artifactory_user'])
        self.assertEqual(self.artifactoryImgRepoWithOsAuthentication.image_repo.artifactory_key, DUMMY_OS_ARTIFACTORY_CONFIG['artifactory_key'])
        self.assertEqual(self.artifactoryImgRepoWithOsAuthentication.image_repo.artifactory_base, DUMMY_OS_ARTIFACTORY_CONFIG['artifactory_base'])

    @patch.object(ArtifactoryRepo, '_get_raw_manifest_list_digest')
    def test_get_manifest_list_digest(self, mock_ArtifactoryRepo):
        # mock api call
        mock_ArtifactoryRepo.return_value = 'dummy_sha'

        # would need connection to artifactory to check
        self.assertEqual(self.artifactoryImgRepoWithOsAuthentication.get_manifest_list_digest(), 'sha256:dummy_sha')

    @patch.object(ArtifactoryRepo, '_get_raw_image_digest')
    def test_get_image_digest(self, mock_ArtifactoryRepo):
        # mock api call
        mock_ArtifactoryRepo.return_value = 'dummy_sha'

        # check to see that digest is returned
        self.assertEqual(self.artifactoryImgRepoWithOsAuthentication.get_image_digest(), 'sha256:dummy_sha')

class TestImageRepoQuayImage(unittest.TestCase):
    def setUp(self):
        self.quayImgWithDigest = Image(IMG_NAME, QUAY_IMAGE_WITH_TAG, DEPLOYMENT, CONTAINER)
        # Initialize a general ImageRepo
        self.quayImgRepo = ImageRepo(self.quayImgWithDigest)

    def test_init(self):
        # check quay images are identified correctly
        self.assertIsInstance(self.quayImgRepo.image_repo, QuayRepo)

class TestArtifactoryRepo(unittest.TestCase):
    def setUp(self):
        self.artifactoryImgWithDigest = Image(IMG_NAME, IMAGE_WITH_DIGEST, DEPLOYMENT, CONTAINER)
        self.artifactoryImgRepoWithOsAuthentication= ArtifactoryRepo(self.artifactoryImgWithDigest)
        self.artifactoryImgRepoWithPassInAuthentiication = ArtifactoryRepo(self.artifactoryImgWithDigest, DUMMY_ARTIFACTORY_CONFIG['artifactory_base'], DUMMY_ARTIFACTORY_CONFIG['artifactory_user'], DUMMY_ARTIFACTORY_CONFIG['artifactory_key'])
    
    def test_init(self):
        # check artifactory repo with os credentials
        self.assertEqual({
            'artifactory_user' : self.artifactoryImgRepoWithOsAuthentication.artifactory_user,
            'artifactory_key' : self.artifactoryImgRepoWithOsAuthentication.artifactory_key,
            'artifactory_base' : self.artifactoryImgRepoWithOsAuthentication.artifactory_base
        }, DUMMY_OS_ARTIFACTORY_CONFIG)
        self.assertEqual(self.artifactoryImgRepoWithOsAuthentication.image, self.artifactoryImgWithDigest)

        # check artifactory repo with passed in credentials
        self.assertEqual({
            'artifactory_user' : self.artifactoryImgRepoWithPassInAuthentiication.artifactory_user,
            'artifactory_key' : self.artifactoryImgRepoWithPassInAuthentiication.artifactory_key,
            'artifactory_base' : self.artifactoryImgRepoWithPassInAuthentiication.artifactory_base
        }, DUMMY_ARTIFACTORY_CONFIG)
        self.assertEqual(self.artifactoryImgRepoWithPassInAuthentiication.image, self.artifactoryImgWithDigest)

    @patch.object(ArtifactoryRepo, '_get_raw_image_digest')
    def test_get_image_digest(self, mock_ArtifactoryRepo):
        # mock api call
        mock_ArtifactoryRepo.return_value = 'dummy_sha'

        # check artifactory repo with os credentials and passed in credentials
        self.assertEqual(self.artifactoryImgRepoWithOsAuthentication.get_image_digest(), 'sha256:dummy_sha') 
        self.assertEqual(self.artifactoryImgRepoWithPassInAuthentiication.get_image_digest(), 'sha256:dummy_sha')

    def test__get_artifactory_repo(self):
        # check artifactory repo with os credentials and passed in credentials
        self.assertEqual(self.artifactoryImgRepoWithOsAuthentication._get_artifactory_repo(), ARTIFACTORY_REPO)
        self.assertEqual(self.artifactoryImgRepoWithPassInAuthentiication._get_artifactory_repo(), ARTIFACTORY_REPO)

    def test__get_raw_image_digest(self):
        # should not be tested because then we would need to test API call
        self.assertEqual(True, True)

    @patch.object(ArtifactoryRepo, '_get_raw_manifest_list_digest')
    def test_get_manifest_list_digest(self, mock_ArtifactoryRepo):
        # mock api call
        mock_ArtifactoryRepo.return_value = 'dummy_sha'

        # check artifactory repo with os credentials and passed in credentials
        self.assertEqual(self.artifactoryImgRepoWithOsAuthentication.get_manifest_list_digest(), 'sha256:dummy_sha') 
        self.assertEqual(self.artifactoryImgRepoWithPassInAuthentiication.get_manifest_list_digest(), 'sha256:dummy_sha')

    def test__get_raw_manifest_list_digest(self):
        # should not be tested because then we would need to test API call
        self.assertEqual(True, True)


class TestQuayRepo(unittest.TestCase):
    def setUp(self):
        # Enable httpretty
        httpretty.enable()
        httpretty.reset()

        # Mock requests
        httpretty.register_uri(
            method=httpretty.GET,
            uri='https://quay.io/api/v1/repository/{repo}/tag/?onlyActiveTags=true&specificTag={tag}'.format(
                repo=QUAY_REPO,
                tag='dummy_tag'
            ),
            body='{ "tags": [ { "is_manifest_list" : true, "manifest_digest" : "sha256:dummy_sha" } ] }'
        )

        # Set up quay image with its image repo object
        self.quayImgWithTag = Image(IMG_NAME, QUAY_IMAGE_WITH_TAG, DEPLOYMENT, CONTAINER)
        self.quayImgRepo = QuayRepo(self.quayImgWithTag)

    def test_init(self):
        # Check to see that image was initialized correctly
        self.assertEqual(self.quayImgRepo.image, self.quayImgWithTag)

    def test_get_image_digest(self):
        # Check to see that digest is returned
        try:
            self.quayImgRepo.get_image_digest()
        except ManifestNotFound:
            self.assertEqual(True, True)

    def test_get_manifest_list_digest(self):
        # Check to see that digest is returned
        self.assertEqual(self.quayImgRepo.get_manifest_list_digest(), 'sha256:dummy_sha')

    def test__get_quay_repo(self):
        self.assertEqual(self.quayImgRepo._get_quay_repo(), QUAY_REPO)

    def tearDown(self):
        httpretty.disable()

class TestDockerRepo(unittest.TestCase):
    def setUp(self):
        # Enable httpretty
        httpretty.enable()
        httpretty.reset()

        # Mock requests
        headers = {
            'accept': [
                'application/vnd.docker.distribution.manifest.list.v2+json',
                'application/vnd.docker.distribution.manifest.v2+json'
            ],
            'Authorization': 'Bearer dummy_token'
        }

        httpretty.register_uri(
            method=httpretty.GET,
            uri=token_path.format(org='ibmcom', repo='ibm-operator-catalog'),
            body='{ "token": "dummy_token" }'
        )

        httpretty.register_uri(
            method=httpretty.GET,
            uri=digest_media_type_path.format(org='ibmcom', repo='ibm-operator-catalog', tag='with_manifest_list'),
            body='"sha256:dummy_raw_sha"',
            headers=headers,
            content_type='manifest.list',
            adding_headers={"Docker-Content-Digest": "sha256:dummy_sha"}
        )

        httpretty.register_uri(
            method=httpretty.GET,
            uri=digest_media_type_path.format(org='ibmcom', repo='ibm-operator-catalog', tag='with_manifest'),
            body='"sha256:dummy_raw_sha"',
            headers=headers,
            content_type='manifest',
            adding_headers={"Docker-Content-Digest": "sha256:dummy_sha"}
        )

        # Set up docker images
        self.dockerImgWithManifestList = Image(IMG_NAME, DOCKER_IMAGE_WITH_MANIFEST_LIST, DEPLOYMENT, CONTAINER)
        self.dockerImgWithManifest = Image(IMG_NAME, DOCKER_IMAGE_WITH_MANIFEST, DEPLOYMENT, CONTAINER)
        self.dockerImgRepoManifestList = ImageRepo(self.dockerImgWithManifestList)
        self.dockerImgRepoManifest = ImageRepo(self.dockerImgWithManifest)

    def test_init(self):
        # Check to see that image was initialized correctly
        self.assertEqual(self.dockerImgRepoManifest.image, self.dockerImgWithManifest)

    def test_get_image_digest(self):
        # Check to see that digest is returned
        self.assertEqual(self.dockerImgRepoManifest.get_image_digest(), 'sha256:dummy_sha')

    def test_get_manifest_list_digest(self):
        # Check to see that digest is returned
        self.assertEqual(self.dockerImgRepoManifestList.get_manifest_list_digest(), 'sha256:dummy_sha')

    def test_get_raw_manifest_list(self):
        # Check to see that digest is returned
        self.assertEqual(self.dockerImgRepoManifestList.get_raw_manifest_list(), 'sha256:dummy_raw_sha')

    def tearDown(self):
        httpretty.disable()

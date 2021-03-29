import unittest
from operator_csv_libs.operatorimage import Operatorimage

IMAGE_WITH_DIGEST = (
    "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/" +
    "cp4mcm-orchestrator-catalog@sha256:dummy_sha"
)
NEW_IMAGE_WTIH_DIGEST = (
    "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/" +
    "cp4mcm-orchestrator-catalog@sha256:new_dummy_sha"
)
IMAGE_WITH_TAG = "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog:release-2.0"


class TestOperatorimage(unittest.TestCase):
    def setUp(self):
        self.deployment = 'dummyDeployment'
        self.container = 'dummyContainer'
        self.dummyOperatorimageDigest = Operatorimage(
            deployment=self.deployment,
            container=self.container,
            image=IMAGE_WITH_DIGEST
        )
        self.dummyOperatorimageTag = Operatorimage(
            deployment=self.deployment,
            container=self.container,
            image=IMAGE_WITH_TAG
        )

    def test_init(self):
        # Check that deployment and conainer are set correctly
        self.assertEqual(self.dummyOperatorimageDigest.deployment, self.deployment)
        self.assertEqual(self.dummyOperatorimageDigest.container, self.container)

        # Check image with digest is set correctly
        self.assertEqual(self.dummyOperatorimageDigest.image, IMAGE_WITH_DIGEST)
        self.assertEqual(
            self.dummyOperatorimageDigest.image_repo,
            'hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm'
        )
        self.assertEqual(self.dummyOperatorimageDigest.image_name, 'cp4mcm-orchestrator-catalog')
        self.assertEqual(self.dummyOperatorimageDigest.digest, 'sha256:dummy_sha')
        self.assertEqual(self.dummyOperatorimageDigest.tag, None)

        # Check image with tag is set correctly
        self.assertEqual(self.dummyOperatorimageTag.image, IMAGE_WITH_TAG)
        self.assertEqual(
            self.dummyOperatorimageTag.image_repo,
            'hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm'
        )
        self.assertEqual(self.dummyOperatorimageTag.image_name, 'cp4mcm-orchestrator-catalog')
        self.assertEqual(self.dummyOperatorimageTag.tag, 'release-2.0')
        self.assertEqual(self.dummyOperatorimageTag.digest, None)

    def test_set_digest(self):
        # Update digest
        self.dummyOperatorimageTag.set_digest('sha256:new_dummy_sha')

        # Check that digest was updated
        self.assertEqual(self.dummyOperatorimageTag.digest, 'sha256:new_dummy_sha')
        self.assertEqual(self.dummyOperatorimageTag.image, NEW_IMAGE_WTIH_DIGEST)

import unittest
import pytest
import copy
import os, yaml
from ..csv import ClusterServiceVersion, _literal, _literal_presenter
from ..images import Image

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


relatedImageSHA1 = "b955bc2952a78bd884896ea88b3325920891cfbb6a36ec5014d1a621eb68c51a"
relatedImageSHA2 = "fe8c229a9c23fc204a93a638e8fd1fe440023d41c7e53fa0b2e50eee34c95836"
relatedImageSHA3 = "eed601bbe53f9f772b408a5c7c05fc2a3fde93e1da32144ffd2b0bd0cf2577aa"
relatedImageSHA4 = "cd76c3abc060b3708b8c2835dc66477932dc5869f2dca8060faf4b01ce9533af"

containerImageSHA1 = "e2356fc61b08c77c1117a2c9c0d21660ade76abd285f9d9fd9ef3e3930d16f98"
newContainerImageSHA1 =  "b8094a55d0684d3a3d8fd1b0486282e5684c5fa576633878b38d764ce823525b"

dummyOwnedCustomResourceDefinitions = [{
    "description": "customresourcedefinitionsDummyDescription",
    "displayName": "customresourcedefinitionsDummyDisplayName",
    "kind": "customresourcedefinitionsDummyKind",
    "name": "customresourcedefinitionsDummyName",
    "version": "customresourcedefinitionsDummyVersion"
}]

dummyAnnotations = {
    "productVersion": "dummyProductVersion",
    "olm.relatedImage.dummyRelatedImages1": "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}".format(relatedImageSHA1),
    "olm.relatedImage.dummyRelatedImages2": "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}".format(relatedImageSHA2),
    "olm.relatedImage.dummyRelatedImages3": "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}".format(relatedImageSHA3)
}

dummyRelatedImages = [
    {"image": "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}".format(relatedImageSHA1), "name": "dummyRelatedImages1"},
    {"image": "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}".format(relatedImageSHA2), "name": "dummyRelatedImages2"}
]

dummyContainers = [
    {"image": "hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}".format(containerImageSHA1), "name": "containerImageDummyName1"}
]

dummyImagePullSecrets = [
    {"name": "dummyImagePullSecretsName"}
]

DUMMY_CSV = {
    "apiVersion": "apiVersionDummy",
    "kind": "ClusterServiceVersion",
    "metadata": {
        "annotations": {
            "olm.skipRange": "metadataDummySkipRange"
        },
        "name": "metadataDummyName"
    },
    "spec": {
        "customresourcedefinitions": {
            "owned": dummyOwnedCustomResourceDefinitions
        },
        "install": {
            "spec": {
                "deployments": [{
                    "name": "deploymentsDummyName",
                    "spec": {
                        "template": {
                            "metadata": {
                                "annotations": dummyAnnotations
                            },
                            "spec": {
                                "containers": dummyContainers,
                                "imagePullSecrets": dummyImagePullSecrets
                            }
                        }
                    }
                }]
            }
        },
        "relatedImages": dummyRelatedImages,
        "replaces": "dummyReplaces",
        "version": "dummyVersion"
    }
}


class TestCSV(unittest.TestCase):
    def setUp(self):
        self.csvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        self.csvWithParams = ClusterServiceVersion(DUMMY_CSV, 'newName', 'newTargetVersion', 'newReplaces', 'newSkipRange', 'newLogger')

        self.operatorImage1 = Image(
            deployment='deploymentsDummyName',
            container='containerImageDummyName1',
            image='hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}'.format(containerImageSHA1)
        )
        self.newOperatorImage1 = Image(
            deployment='deploymentsDummyName',
            container='containerImageDummyName1',
            image='hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}'.format(newContainerImageSHA1)
        )

        self.Image1 = Image(
            deployment='deploymentsDummyName',
            name='dummyRelatedImages1',
            image='hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}'.format(relatedImageSHA1)
        )
        self.Image2 = Image(
            deployment='deploymentsDummyName',
            name='dummyRelatedImages2',
            image='hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}'.format(relatedImageSHA2)
            )
        self.Image3 = Image(
            deployment='deploymentsDummyName',
            name='dummyRelatedImages3',
            image='hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}'.format(relatedImageSHA3)
        )
        self.Image4 = Image(
            deployment='deploymentsDummyName',
            name='dummyRelatedImages4',
            image='hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}'.format(relatedImageSHA4)
        )

    def test_init(self):
        testAnnotationRelatedImages = [self.Image1, self.Image2, self.Image3]
        TEST_DUMMY_CSV = copy.deepcopy(DUMMY_CSV)

        # check to see that all varaibles and csv are correct
        self.assertEqual(self.csvWithoutParams.original_csv, DUMMY_CSV)
        self.assertEqual(self.csvWithoutParams.csv, DUMMY_CSV)

        # should only be one image in original_operator_images and operator_images
        self.assertEqual(self.csvWithoutParams.operator_images, self.csvWithoutParams.original_operator_images)
        self.assertEqual(len(self.csvWithoutParams.original_operator_images), 1)
        self.assertEqual(len(self.csvWithoutParams.operator_images), 1)
        # check to see that the correct image was stored
        self.assertEqual(self.csvWithoutParams.operator_images[0].deployment, self.operatorImage1.deployment)
        self.assertEqual(self.csvWithoutParams.operator_images[0].container, self.operatorImage1.container)
        self.assertEqual(self.csvWithoutParams.operator_images[0].image, self.operatorImage1.image)
        # should be three annotation related images
        self.assertEqual(len(self.csvWithoutParams.annotation_related_images), 3)
        for imageIndex in range(3):
            # check to see that the correct image was stored
            self.assertEqual(self.csvWithoutParams.annotation_related_images[imageIndex].name, testAnnotationRelatedImages[imageIndex].name)
            self.assertEqual(self.csvWithoutParams.annotation_related_images[imageIndex].image, testAnnotationRelatedImages[imageIndex].image)
            self.assertEqual(self.csvWithoutParams.annotation_related_images[imageIndex].deployment, testAnnotationRelatedImages[imageIndex].deployment)
        self.assertEqual(self.csvWithoutParams.spec_related_images, [])
        self.assertEqual(self.csvWithoutParams.name, 'metadataDummyName')
        self.assertEqual(self.csvWithoutParams.version, '')
        self.assertEqual(self.csvWithoutParams.major_minor, '')
        self.assertEqual(self.csvWithoutParams.versioned_name, '')
        self.assertEqual(self.csvWithoutParams.replaces, None)
        self.assertEqual(self.csvWithoutParams.skiprange, None)

        # create test dummy csv for csv with parameters
        TEST_DUMMY_CSV['spec']['replaces'] = 'newReplaces'
        TEST_DUMMY_CSV['spec']['version'] = 'newTargetVersion'
        TEST_DUMMY_CSV['metadata']['name'] = '{}.v{}'.format('newName', 'newTargetVersion')
        TEST_DUMMY_CSV['metadata']['annotations']['olm.skipRange'] = 'newSkipRange'

        # check to see that all variables and csv are correct
        self.assertEqual(self.csvWithParams.original_csv, DUMMY_CSV)
        self.assertEqual(self.csvWithParams.csv, TEST_DUMMY_CSV)
        # should only be one image in original_operator_images and operator_images
        self.assertEqual(self.csvWithParams.operator_images, self.csvWithParams.original_operator_images)
        self.assertEqual(len(self.csvWithParams.original_operator_images), 1)
        self.assertEqual(len(self.csvWithParams.operator_images), 1)
        # check to see that the correct image was stored
        self.assertEqual(self.csvWithParams.operator_images[0].deployment, self.operatorImage1.deployment)
        self.assertEqual(self.csvWithParams.operator_images[0].container, self.operatorImage1.container)
        self.assertEqual(self.csvWithParams.operator_images[0].image, self.operatorImage1.image)
        # should be three annotation related images
        self.assertEqual(len(self.csvWithParams.annotation_related_images), 3)
        for imageIndex in range(3):
            # check to see that the correct image was stored
            self.assertEqual(self.csvWithParams.annotation_related_images[imageIndex].name, testAnnotationRelatedImages[imageIndex].name)
            self.assertEqual(self.csvWithParams.annotation_related_images[imageIndex].image, testAnnotationRelatedImages[imageIndex].image)
            self.assertEqual(self.csvWithParams.annotation_related_images[imageIndex].deployment, testAnnotationRelatedImages[imageIndex].deployment)
        self.assertEqual(self.csvWithParams.spec_related_images, [])
        self.assertEqual(self.csvWithParams.name, 'newName')
        self.assertEqual(self.csvWithParams.version, 'newTargetVersion')
        self.assertEqual(self.csvWithParams.major_minor, '')
        self.assertEqual(self.csvWithParams.versioned_name, '{}.v{}'.format('newName', 'newTargetVersion'))
        self.assertEqual(self.csvWithParams.replaces, 'newReplaces')
        self.assertEqual(self.csvWithParams.skiprange, 'newSkipRange')

    def test_set_deployments_annotations(self, key=None, value=None):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        TEST_DUMMY_CSV = copy.deepcopy(DUMMY_CSV)
        testDummyAnnotations = copy.deepcopy(dummyAnnotations)

        # check to see that function returns correct csv
        newCloudpakVersion = 'newDummyCloudpakVersion'
        newProductVersion = 'newDummyProductVersion'
        testDummyAnnotations['cloudpakVersion'] = newCloudpakVersion
        testcsvWithoutParams.set_deployments_annotations(key='cloudpakVersion', value=newCloudpakVersion)
        testDummyAnnotations['productVersion'] = newProductVersion
        testcsvWithoutParams.set_deployments_annotations('productVersion', newProductVersion)
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['metadata']['annotations'] = testDummyAnnotations
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

        # check to see if function works without specifiying parameter
        newCloudpakVersion = 'newDummyCloudpakVersion2'
        newProductVersion = 'newDummyProductVersion2'
        testDummyAnnotations['cloudpakVersion'] = newCloudpakVersion
        testcsvWithoutParams.set_deployments_annotations(key='cloudpakVersion', value=newCloudpakVersion)
        testDummyAnnotations['productVersion'] = newProductVersion
        testcsvWithoutParams.set_deployments_annotations('productVersion', newProductVersion)
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['metadata']['annotations'] = testDummyAnnotations
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

        # check to see that it will not add anything if annotations doesn't exiist
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['metadata'].pop('annotations')
        testcsvWithoutParams.csv['spec']['install']['spec']['deployments'][0]['spec']['template']['metadata'].pop('annotations')
        testcsvWithoutParams.set_deployments_annotations('productVersion', newProductVersion)
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

    def test_set_container_image_annotation(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        TEST_DUMMY_CSV = copy.deepcopy(DUMMY_CSV)
        testImage = testcsvWithoutParams.get_operator_images()[0]

        # set container image
        testcsvWithoutParams.set_container_image_annotation(testImage)

        # check to see that CSV was updated correctly
        TEST_DUMMY_CSV['metadata']['annotations']['containerImage'] = testImage.image
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

        # test with containerImage already definded
        TEST_DUMMY_CSV['metadata']['annotations']['containerImage'] = 'newContainerImage'
        testcsvWithoutParamsDefined = ClusterServiceVersion(TEST_DUMMY_CSV)
        TEST_DUMMY_CSV['metadata']['annotations']['containerImage'] = testImage.image
        testcsvWithoutParamsDefined.set_container_image_annotation(testImage)
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

    def test_set_version(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)

        # set new version
        testcsvWithoutParams.set_version('newVersion')

        # check to see if varaible version and version_name is changed
        self.assertEqual(testcsvWithoutParams.version, 'newVersion')
        self.assertEqual(testcsvWithoutParams.versioned_name, '{}.v{}'.format('metadataDummyName','newVersion'))
        # check to see if changes were made in csv
        self.assertEqual(testcsvWithoutParams.csv['spec']['version'], 'newVersion')
        self.assertEqual(testcsvWithoutParams.csv['metadata']['name'], '{}.v{}'.format('metadataDummyName','newVersion'))
        self.assertEqual('replaces' not in testcsvWithoutParams.csv['spec'], True)

    def test_set_replaces(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)

        # set new replaces
        testcsvWithoutParams.set_replaces('newReplaces')

        # check to see if variable replaces is changed
        self.assertEqual(testcsvWithoutParams.replaces, 'newReplaces')
        self.assertEqual(testcsvWithoutParams.csv['spec']['replaces'], 'newReplaces')

    def test_set_image_pullsecret(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        TEST_DUMMY_CSV = copy.deepcopy(DUMMY_CSV)
        testDummyImagePullSecrets = []

        #  check to see if one image pull secret will be added
        testDummyImagePullSecrets.append({'name': 'newImagePullSecretsName'})
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['imagePullSecrets'] = testDummyImagePullSecrets
        testcsvWithoutParams.set_image_pullsecret('newImagePullSecretsName')
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

        # check to see if it will add if more than one image pull secret
        testcsvWithoutParams.set_image_pullsecret(['newImagePullSecretsName1', 'newImagePullSecretsName2', 'newImagePullSecretsName3'])
        testDummyImagePullSecrets[0]['name'] = 'newImagePullSecretsName1'
        testDummyImagePullSecrets.append({'name': 'newImagePullSecretsName2'})
        testDummyImagePullSecrets.append({'name': 'newImagePullSecretsName3'})
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['imagePullSecrets'] = testDummyImagePullSecrets
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

    def test_add_image_pullsecret(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        TEST_DUMMY_CSV = copy.deepcopy(DUMMY_CSV)
        testDummyImagePullSecrets = TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['imagePullSecrets']

        # check to see if one image pull secret will be added
        testDummyImagePullSecrets.append({'name': 'newImagePullSecretsName'})
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['imagePullSecrets'] = testDummyImagePullSecrets
        testcsvWithoutParams.add_image_pullsecret('newImagePullSecretsName')
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

        # check to see if it will add if image pull secrets does not exists
        testDummyImagePullSecrets = []
        testDummyImagePullSecrets.append({'name': 'newImagePullSecretsName'})
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['imagePullSecrets'] = testDummyImagePullSecrets
        testcsvWithoutParams.csv['spec']['install']['spec']['deployments'][0]['spec']['template']['spec'].pop('imagePullSecrets')
        self.assertEqual('imagePullSecrets' not in testcsvWithoutParams.csv['spec']['install']['spec']['deployments'][0]['spec']['template']['spec'], True)
        testcsvWithoutParams.add_image_pullsecret('newImagePullSecretsName')
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

        # check to see if it will add if more than one image pull secret
        testcsvWithoutParams.csv['spec']['install']['spec']['deployments'][0]['spec']['template']['spec'].pop('imagePullSecrets')
        testcsvWithoutParams.add_image_pullsecret(['newImagePullSecretsName1', 'newImagePullSecretsName2', 'newImagePullSecretsName3'])
        testDummyImagePullSecrets[0]['name'] = 'newImagePullSecretsName1'
        testDummyImagePullSecrets.append({'name': 'newImagePullSecretsName2'})
        testDummyImagePullSecrets.append({'name': 'newImagePullSecretsName3'})
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['imagePullSecrets'] = testDummyImagePullSecrets
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

    def test_generate_spec_relatedImages(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        testDummyRelatedImages = copy.deepcopy(dummyRelatedImages)
        TEST_DUMMY_CSV = copy.deepcopy(DUMMY_CSV)

        # check to see if csv was changed with new related images based on annotated related images
        testDummyRelatedImages.append({
            'image': 'hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}'.format(relatedImageSHA3),
            'name': 'dummyRelatedImages3'
        })
        TEST_DUMMY_CSV['spec']['relatedImages'] = testDummyRelatedImages
        testcsvWithoutParams.generate_spec_relatedImages()
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

    def test_get_owned_crds(self):
        # check to see if function returns original values
        self.assertEqual(self.csvWithoutParams.get_owned_crds(), dummyOwnedCustomResourceDefinitions)

    def test_get_updated_csv(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        testDummyAnnotations = copy.deepcopy(dummyAnnotations)
        testDummyContainers = []
        TEST_DUMMY_CSV = copy.deepcopy(DUMMY_CSV)

        # check to see if function returns original csv
        self.assertEqual(testcsvWithoutParams.get_updated_csv(), TEST_DUMMY_CSV)

        # make changes to csv and see if changes are reflected
        testDummyAnnotations['olm.relatedImage.dummyRelatedImages4'] = 'hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}'.format(relatedImageSHA4)
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['metadata']['annotations'] = testDummyAnnotations
        testDummyContainers.append({'image': self.newOperatorImage1.image, 'name':  self.newOperatorImage1.container})
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['containers'] = testDummyContainers
        # update csv object
        testcsvWithoutParams.operator_images = [self.newOperatorImage1]
        testcsvWithoutParams.annotation_related_images = [self.Image1, self.Image2, self.Image3, self.Image4]
        # check to see if changes were made to csv were correct
        self.assertEqual(testcsvWithoutParams.get_updated_csv(), TEST_DUMMY_CSV)

    def test_get_replaces(self):
        # call function to return replaces from csv
        self.assertEqual(self.csvWithoutParams.get_replaces(), 'dummyReplaces')

    def test_get_operator_images(self):
        # call function to return operator images and check that the right images are returned
        operatorImages = self.csvWithoutParams.get_operator_images()

        # should only be one image
        self.assertEqual(len(operatorImages), 1)
        operatorImage = operatorImages[0]
        self.assertEqual(operatorImage.deployment, self.operatorImage1.deployment)
        self.assertEqual(operatorImage.container, self.operatorImage1.container)
        self.assertEqual(operatorImage.image, self.operatorImage1.image)

    def test_get_annotation_related_images(self):
        testAnnotationRelatedImages = [self.Image1, self.Image2, self.Image3]

        # call function to return annotation related images and check to see if the right images are returned
        annotationRelatedImages = self.csvWithoutParams.get_annotation_related_images()

        # should be three images
        self.assertEqual(len(annotationRelatedImages), 3)
        for imageIndex in range(len(annotationRelatedImages)):
            self.assertEqual(annotationRelatedImages[imageIndex].name, testAnnotationRelatedImages[imageIndex].name)
            self.assertEqual(annotationRelatedImages[imageIndex].image, testAnnotationRelatedImages[imageIndex].image)
            self.assertEqual(annotationRelatedImages[imageIndex].deployment, testAnnotationRelatedImages[imageIndex].deployment)

    def test__update_version_references(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        testcsvWithParams = ClusterServiceVersion(DUMMY_CSV, 'newName', 'newTargetVersion', 'newReplaces', 'newSkipRange', 'newLogger')

        # values in csv should not match value in variables since no params passed in when initializing
        self.assertNotEqual(testcsvWithoutParams.csv['spec']['version'], testcsvWithoutParams.version)
        self.assertNotEqual(testcsvWithoutParams.csv['metadata']['name'], testcsvWithoutParams.versioned_name)
        self.assertNotEqual(testcsvWithoutParams.csv['metadata']['annotations']['olm.skipRange'], testcsvWithoutParams.skiprange)
        self.assertNotEqual(testcsvWithoutParams.csv['spec']['replaces'], testcsvWithoutParams.replaces)
        # call function for csv without parameters
        testcsvWithoutParams._update_version_references()
        # check to see if values in csv were updated, even though there were no changes
        self.assertEqual(testcsvWithoutParams.version, '')
        self.assertEqual(testcsvWithoutParams.csv['spec']['version'], '')
        self.assertEqual(testcsvWithoutParams.versioned_name, '')
        self.assertEqual(testcsvWithoutParams.csv['metadata']['name'], '')
        self.assertEqual(testcsvWithoutParams.skiprange, None)
        self.assertNotEqual(testcsvWithoutParams.csv['metadata']['annotations']['olm.skipRange'], None)
        self.assertEqual(testcsvWithoutParams.csv['metadata']['annotations']['olm.skipRange'], 'metadataDummySkipRange') #skipRange does not change
        self.assertEqual(testcsvWithoutParams.replaces, None)
        self.assertEqual('replaces' not in testcsvWithoutParams.csv['spec'], True) # replaces is removed

        # function is already called when csv is created with version, check to see if values are updated correctly
        self.assertEqual(testcsvWithParams.csv['spec']['version'], testcsvWithParams.version)
        self.assertEqual(testcsvWithParams.csv['spec']['version'], 'newTargetVersion')
        self.assertEqual(testcsvWithParams.csv['metadata']['name'], testcsvWithParams.versioned_name)
        self.assertEqual(testcsvWithParams.csv['metadata']['name'], 'newName.vnewTargetVersion')
        self.assertEqual(testcsvWithParams.csv['metadata']['annotations']['olm.skipRange'], testcsvWithParams.skiprange)
        self.assertEqual(testcsvWithParams.csv['metadata']['annotations']['olm.skipRange'], 'newSkipRange')
        self.assertEqual(testcsvWithParams.csv['spec']['replaces'], testcsvWithParams.replaces)
        self.assertEqual(testcsvWithParams.csv['spec']['replaces'], 'newReplaces')

    def test__get_operator_images(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        # remove any values in original operator images and operator images
        testcsvWithoutParams.original_operator_images = []
        testcsvWithoutParams.operator_images = []
        self.assertEqual(testcsvWithoutParams.original_operator_images, [])
        self.assertEqual(testcsvWithoutParams.operator_images, [])

        # call function to populate all images
        testcsvWithoutParams._get_operator_images()

        # should only be one image
        self.assertEqual(len(testcsvWithoutParams.original_operator_images), 1)
        self.assertEqual(len(testcsvWithoutParams.operator_images), 1)
        # check to see that the correct image was stored
        self.assertEqual(testcsvWithoutParams.operator_images[0].deployment, self.operatorImage1.deployment)
        self.assertEqual(testcsvWithoutParams.operator_images[0].container, self.operatorImage1.container)
        self.assertEqual(testcsvWithoutParams.operator_images[0].image, self.operatorImage1.image)
        # check to see that both images are the same for operator images list and orignal operator images list
        self.assertEqual(testcsvWithoutParams.operator_images[0], testcsvWithoutParams.original_operator_images[0])

    def test__get_related_images(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        testAnnotationRelatedImages = [self.Image1, self.Image2, self.Image3]
        # remove any values in annotation related images list
        testcsvWithoutParams.annotation_related_images = []
        self.assertEqual(testcsvWithoutParams.annotation_related_images, [])

        # call function to populate all images
        testcsvWithoutParams._get_related_images()

        # should be three images
        self.assertEqual(len(testcsvWithoutParams.annotation_related_images), 3)
        for imageIndex in range(len(testcsvWithoutParams.annotation_related_images)):
            # check to see that correct image was stored
            self.assertEqual(testcsvWithoutParams.annotation_related_images[imageIndex].name, testAnnotationRelatedImages[imageIndex].name)
            self.assertEqual(testcsvWithoutParams.annotation_related_images[imageIndex].image, testAnnotationRelatedImages[imageIndex].image)
            self.assertEqual(testcsvWithoutParams.annotation_related_images[imageIndex].deployment, testAnnotationRelatedImages[imageIndex].deployment)

    def test__update_operator_container_images(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        testDummyContainers = []
        TEST_DUMMY_CSV = copy.deepcopy(DUMMY_CSV)

        # make changes to csv and see if changes are reflected
        testDummyContainers.append({'image': self.newOperatorImage1.image, 'name': self.newOperatorImage1.container})
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['spec']['containers'] = testDummyContainers

        # update operator image
        testcsvWithoutParams.operator_images = [self.newOperatorImage1]
        # update csv and check to see if those changes are correct
        testcsvWithoutParams._update_operator_container_images()
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

    def test___update_operand_images(self):
        testcsvWithoutParams = ClusterServiceVersion(DUMMY_CSV)
        testDummyAnnotations = copy.deepcopy(dummyAnnotations)
        TEST_DUMMY_CSV = copy.deepcopy(DUMMY_CSV)

        # make changes to csv and see if changes are reflected
        testDummyAnnotations['olm.relatedImage.dummyRelatedImages4'] = 'hyc-cp4mcm-team-docker-local.artifactory.swg-devops.com/cicd/cp4mcm/cp4mcm-orchestrator-catalog@sha256:{}'.format(relatedImageSHA4)
        TEST_DUMMY_CSV['spec']['install']['spec']['deployments'][0]['spec']['template']['metadata']['annotations'] = testDummyAnnotations
        # add more annotation realted images
        testcsvWithoutParams.annotation_related_images = [self.Image1, self.Image2, self.Image3, self.Image4]
        # update csv and check to see if those changes are correct
        testcsvWithoutParams._update_operand_images()
        self.assertEqual(testcsvWithoutParams.csv, TEST_DUMMY_CSV)

    def test__get_deployments(self):
        # Read in sample files
        with open(THIS_DIR + '/test_files/valid_operator_deployment.yaml', 'r') as stream:
            deployment_sample = yaml.safe_load(stream)
        with open(THIS_DIR + '/test_files/valid_csv.yaml', 'r') as stream:
            csv_sample = yaml.safe_load(stream)

        c = ClusterServiceVersion(csv_sample)

        # Increasing the maxdiff lets us see all the context on how the yaml failed
        self.maxDiff = None

         ## Assert that dpeloyment is as expected
        operator_deployment_variations = [
            {}, # default values
            {'api_version': 'apps/v1', 'kind': 'Deployment'},
        ]

        for variation in operator_deployment_variations:
            with self.subTest(variation=variation):
                deployments = c.get_operator_deployments(**variation)

                # We expect a dict back
                self.assertIsInstance(deployments, list)

                # Ensure we only got a single deployment
                self.assertEqual(len(deployments), 1)

                # Ensure deployment is valid
                self.assertDictEqual(deployments[0], deployment_sample)

        ## Assert that original CSV did not get changed at all
        self.assertEqual(c.csv, c.original_csv)

    def test__get_formatted_csv(self):
        # Read in sample files
        with open(THIS_DIR + '/test_files/valid_csv_formatted.yaml', 'r') as stream:
            csv_sample_formatted = yaml.safe_load(stream)
        
        # Read in sample files
        with open(THIS_DIR + '/test_files/valid_csv.yaml', 'r') as stream:
            csv_sample = yaml.safe_load(stream)

        c = ClusterServiceVersion(csv_sample)

        # Increasing the maxdiff lets us see all the context on how the yaml failed
        self.maxDiff = None

        # Ensure that data has not been changed
        self.assertDictEqual(yaml.safe_load(c.get_formatted_csv()), csv_sample_formatted)

        # Ensure that format has been maintained
        yaml.add_representer(_literal, _literal_presenter)
        csv_sample_formatted['metadata']['annotations']['alm-examples'] = _literal(csv_sample_formatted['metadata']['annotations']['alm-examples'])
        self.assertEqual(c.get_formatted_csv(), yaml.dump(csv_sample_formatted, default_flow_style=False))

    def test__setup_basic_logger(self):
        # should not be tested because it only sets up logger
        self.assertEqual(True, True)

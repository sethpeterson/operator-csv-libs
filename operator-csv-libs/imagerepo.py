from .images import Image
from artifactory import ArtifactoryPath
import os, sys
import requests

class ImageRepo:
    """ This is a class to provide a general interface to query container image registry servers.
        Hacked together in a hurry, will probably be refactored to be more pythonic - if there's a better way to do this
    """
    def __init__(self, image, logger=None):
        self.image = image

        # Check for some well known repos
        if 'artifactory' in self.image.get_image_repo():
            self.image_repo = ArtifactoryRepo(self.image)
        elif 'quay.io' in self.image.get_image_repo():
            self.image_repo = QuayRepo(self.image)

        else:
            raise RepoTypeNotImplemented('Unknown repository type for image {}'.format(image.get_image()))

    def get_manifest_list_digest(self):
        return self.image_repo.get_manifest_list_digest()

    def get_image_digest(self):
        return self.image_repo.get_image_digest()


class ArtifactoryRepo:
    # Allow credentials to be shared between instances
    _artifactory_user = None
    _artifactory_key = None
    _artifactory_base = None

    def __init__(self, image, artifactory_base=None, artifactory_user=None, artifactory_key=None, logger=None):
        self.image = image
        
        # Always give provided credential preference
        if artifactory_user:
            self.artifactory_user = artifactory_user
        elif self._artifactory_user:
            self.artifactory_user = self._artifactory_user
        elif 'ARTIFACTORY_USER' in os.environ:
            # Go to environment variables if we don't have them as class variable either
            self._artifactory_user = os.getenv('ARTIFACTORY_USER')
            self.artifactory_user = self._artifactory_user
        else:
            # This is where we should panic and throw some orderly exception
            raise MissingCredentials("No artifactory user provided or found in ARTIFACTORY_USER environment variable")
        
        if artifactory_key:
            self.artifactory_key = artifactory_key
        elif self._artifactory_key:
            self.artifactory_key = self._artifactory_key
        elif 'ARTIFACTORY_KEY' in os.environ:
            self._artifactory_key = os.getenv('ARTIFACTORY_KEY')
            self.artifactory_key = self._artifactory_key
        else:
            # This is where we should panic and throw some orderly exception
            raise MissingCredentials("No artifactory key provided or found in ARTIFACTORY_KEY environment variable")

        if artifactory_base:
            self.artifactory_base = artifactory_base
        elif self._artifactory_base:
            self.artifactory_base = self._artifactory_base
        elif 'ARTIFACTORY_BASE' in os.environ:
            self._artifactory_base = os.getenv('ARTIFACTORY_BASE')
            self.artifactory_base = self._artifactory_base
        else:
            # This is where we should panic and throw some orderly exception
            raise MissingCredentials("No artifactory base provided or found in ARTIFACTORY_BASE environment variable")

    def get_image_digest(self):
        # We know we're always querying for sha256
        return 'sha256:{}'.format(self._get_raw_image_digest())

    def _get_artifactory_repo(self):
        # For artifactory we need to massage the repo string a bit
        ### Split out all directories after artifactory.com/
        p = '/'.join(self.image.get_image_repo().split('/')[1:])
        ### Split out the first part of repo.artifactory.com 
        r = self.image.get_image_repo().split('.')[0]
        return '{}/{}'.format(r, p)

    
    def _get_raw_image_digest(self):
        manifestpath = '/'.join([
                        self.artifactory_base,
                        self._get_artifactory_repo(), # We have to massage the repo for artifactory
                        self.image.get_image_name(),
                        self.image.get_tag(),
                        "manifest.json"
                    ])
        manifest_path = ArtifactoryPath(manifestpath, auth=(self.artifactory_user, self.artifactory_key))

        try:
            return ArtifactoryPath.stat(manifest_path).sha256
        except FileNotFoundError as e:
            raise ManifestNotFound(e)


    def get_manifest_list_digest(self):
        # We know we're always querying for sha256
        return 'sha256:{}'.format(self._get_raw_manifest_list_digest())

    def _get_raw_manifest_list_digest(self):
        listpath = '/'.join([
                        self.artifactory_base,
                        self._get_artifactory_repo(), # We have to massage the repo for artifactory
                        self.image.get_image_name(),
                        self.image.get_tag(),
                        "list.manifest.json"
                    ])
        list_path = ArtifactoryPath(listpath, auth=(self.artifactory_user, self.artifactory_key))

        try:
            return ArtifactoryPath.stat(list_path).sha256
        except FileNotFoundError as e:
            raise ManifestListNotFound(e)

class QuayRepo:

    QUAY_BASE_URL = 'https://quay.io/api/v1/repository'

    def __init__(self, image):
        self.image = image

    def get_image_digest(self):
        return self._get_digest(manifest_list=False)

    def get_manifest_list_digest(self):
        return self._get_digest(manifest_list=True)


    def _get_digest(self, manifest_list):
        url = '/'.join([
                        self.QUAY_BASE_URL,
                        self._get_quay_repo(),
                        'tag',
                        '?onlyActiveTags=true&specificTag='
                ])
        
        resp = requests.get(url + self.image.get_tag())

        if resp.status_code == 403:
            raise MissingCredentials(resp.text)
        elif resp.status_code == 404:
            if manifest_list:
                raise ManifestListNotFound(resp.text)
            else:
                raise ManifestNotFound(resp.text)
        elif not resp.status_code == 200:
            raise Exception(resp.text)

        # Since we query for specific tag we expect single response
        tags = resp.json()['tags']
        if len(tags) > 1:
            raise Exception('Expected 1 tag, found {}. {}'.format(len(tags), tags))
        for t in tags:
            if t['is_manifest_list'] == manifest_list:
                return t['manifest_digest']
            else:
                if manifest_list:
                    raise ManifestListNotFound('Tag {} is not manifest list'.format(self.image.get_tag()))
                else:
                    raise ManifestNotFound('Tag {} is a manifest list'.format(self.image.get_tag()))
                    


    def _get_quay_repo(self):
        r = self.image.get_image_repo().replace('quay.io/','')
        return '/'.join([r, self.image.get_image_name()])

class MissingCredentials(Exception):
    pass

class RepoTypeNotImplemented(Exception):
    pass

class ManifestListNotFound(Exception):
    pass

class ManifestNotFound(Exception):
    pass
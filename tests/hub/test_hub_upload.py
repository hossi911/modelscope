# Copyright (c) Alibaba, Inc. and its affiliates.
import os
import shutil
import tempfile
import unittest

from modelscope.hub.api import HubApi
from modelscope.hub.constants import Licenses, ModelVisibility
from modelscope.hub.repository import Repository
from modelscope.hub.upload import upload_folder
from modelscope.utils.constant import ModelFile
from modelscope.utils.logger import get_logger
from modelscope.utils.test_utils import test_level
from .test_utils import TEST_ACCESS_TOKEN1, delete_credential

logger = get_logger()


class HubUploadTest(unittest.TestCase):

    def setUp(self):
        logger.info('SetUp')
        self.api = HubApi()
        self.user = os.environ.get('TEST_MODEL_ORG', 'citest')
        logger.info(self.user)
        self.create_model_name = '%s/%s' % (self.user, 'test_model_upload')
        temporary_dir = tempfile.mkdtemp()
        self.work_dir = temporary_dir
        self.model_dir = os.path.join(temporary_dir, self.create_model_name)
        self.finetune_path = os.path.join(self.work_dir, 'finetune_path')
        self.repo_path = os.path.join(self.work_dir, 'repo_path')
        os.mkdir(self.finetune_path)
        os.system("echo '{}'>%s"
                  % os.path.join(self.finetune_path, ModelFile.CONFIGURATION))

    def tearDown(self):
        logger.info('TearDown')
        shutil.rmtree(self.model_dir, ignore_errors=True)
        self.api.delete_model(model_id=self.create_model_name)

    def test_upload_exits_repo_master(self):
        logger.info('basic test for upload!')
        self.api.login(TEST_ACCESS_TOKEN1)
        self.api.create_model(
            model_id=self.create_model_name,
            visibility=ModelVisibility.PUBLIC,
            license=Licenses.APACHE_V2)
        os.system("echo '111'>%s"
                  % os.path.join(self.finetune_path, 'add1.py'))
        upload_folder(
            model_id=self.create_model_name, model_dir=self.finetune_path)
        Repository(model_dir=self.repo_path, clone_from=self.create_model_name)
        assert os.path.exists(os.path.join(self.repo_path, 'add1.py'))
        shutil.rmtree(self.repo_path, ignore_errors=True)
        os.system("echo '222'>%s"
                  % os.path.join(self.finetune_path, 'add2.py'))
        upload_folder(
            model_id=self.create_model_name,
            model_dir=self.finetune_path,
            revision='new_revision/version1')
        Repository(
            model_dir=self.repo_path,
            clone_from=self.create_model_name,
            revision='new_revision/version1')
        assert os.path.exists(os.path.join(self.repo_path, 'add2.py'))
        shutil.rmtree(self.repo_path, ignore_errors=True)
        os.system("echo '333'>%s"
                  % os.path.join(self.finetune_path, 'add3.py'))
        upload_folder(
            model_id=self.create_model_name,
            model_dir=self.finetune_path,
            revision='new_revision/version2',
            commit_message='add add3.py')
        Repository(
            model_dir=self.repo_path,
            clone_from=self.create_model_name,
            revision='new_revision/version2')
        assert os.path.exists(os.path.join(self.repo_path, 'add2.py'))
        assert os.path.exists(os.path.join(self.repo_path, 'add3.py'))
        shutil.rmtree(self.repo_path, ignore_errors=True)
        add4_path = os.path.join(self.finetune_path, 'temp')
        os.mkdir(add4_path)
        os.system("echo '444'>%s" % os.path.join(add4_path, 'add4.py'))
        upload_folder(
            model_id=self.create_model_name,
            model_dir=self.finetune_path,
            revision='new_revision/version1')
        Repository(
            model_dir=self.repo_path,
            clone_from=self.create_model_name,
            revision='new_revision/version1')
        assert os.path.exists(os.path.join(add4_path, 'add4.py'))
        shutil.rmtree(self.repo_path, ignore_errors=True)

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_upload_non_exists_repo(self):
        logger.info('test upload non exists repo!')
        self.api.login(TEST_ACCESS_TOKEN1)
        os.system("echo '111'>%s"
                  % os.path.join(self.finetune_path, 'add1.py'))
        upload_folder(
            model_id=self.create_model_name,
            model_dir=self.finetune_path,
            revision='new_model_new_revision',
            visibility=ModelVisibility.PUBLIC,
            license=Licenses.APACHE_V2)
        Repository(
            model_dir=self.repo_path,
            clone_from=self.create_model_name,
            revision='new_model_new_revision')
        assert os.path.exists(os.path.join(self.repo_path, 'add1.py'))
        shutil.rmtree(self.repo_path, ignore_errors=True)

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_upload_without_token(self):
        logger.info('test upload without login!')
        self.api.login(TEST_ACCESS_TOKEN1)
        delete_credential()
        try:
            upload_folder(
                model_id=self.create_model_name,
                model_dir=self.finetune_path,
                visibility=ModelVisibility.PUBLIC,
                license=Licenses.APACHE_V2)
        except Exception as e:
            logger.info(e)
            self.api.login(TEST_ACCESS_TOKEN1)
            upload_folder(
                model_id=self.create_model_name,
                model_dir=self.finetune_path,
                visibility=ModelVisibility.PUBLIC,
                license=Licenses.APACHE_V2)
            Repository(
                model_dir=self.repo_path, clone_from=self.create_model_name)
            assert os.path.exists(
                os.path.join(self.repo_path, 'configuration.json'))
            shutil.rmtree(self.repo_path, ignore_errors=True)

    @unittest.skipUnless(test_level() >= 0, 'skip test in current test level')
    def test_upload_invalid_repo(self):
        logger.info('test upload to invalid repo!')
        self.api.login(TEST_ACCESS_TOKEN1)
        try:
            upload_folder(
                model_id='%s/%s' % ('speech_tts', 'invalid_model_test'),
                model_dir=self.finetune_path,
                visibility=ModelVisibility.PUBLIC,
                license=Licenses.APACHE_V2)
        except Exception as e:
            logger.info(e)
            upload_folder(
                model_id=self.create_model_name,
                model_dir=self.finetune_path,
                visibility=ModelVisibility.PUBLIC,
                license=Licenses.APACHE_V2)
            Repository(
                model_dir=self.repo_path, clone_from=self.create_model_name)
            assert os.path.exists(
                os.path.join(self.repo_path, 'configuration.json'))
            shutil.rmtree(self.repo_path, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()

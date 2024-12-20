# This function is adapted from a private project.
# Original project: https://github.com/mannmi/TPRO
# Author: mannmi
# Date: last modified Nov 29, 2023
# (reduced version of)

import unittest
import os
from src.config_loader.configLoader import YmlLoader


class TestYmlLoader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print(f"======== {cls.__name__}========")

    def setUp(self):
        # print(f"Running config.yml: {self._testMethodName}")
        conf = "/app/tests/TestData/config.yml"
        test_file = "/app/tests/TestData/tmpConfig.yml"
        # use os to copy the file
        os.system(f'cp {conf} {test_file}')
        self.ymlLoader = YmlLoader(test_file)

    def test_yml_loader_data(self):
        print(f"Running test ====> {self._testMethodName}")
        data_read = self.ymlLoader.data
        ref_string = {'System': {'ProjectRoot': 'F:\\PycharmProjects\\TPRO', 'chunksize': '10 ** 1', 'delimiter': ';',
                                'encoding': 'utf-8', 'lineterminator': '\\n', 'projectRoot_file': 'appDemoAsync.py'},
                     'acceskeys': {'HUGGINGFACE_TOKEN': 'hf_testtoken'}, 'bertModel': [
                {'filter': {'model_name': 'unitary/unbiased-toxic-roberta', 'model_path': '/models/filtration_model'}}],
                     'combinedModel': {
                         'contains': {'-gpt2': {'model_name': 'joined-Model', 'model_path': 'models/joined-Model'}}},
                     'gpt2Model': [{'gpt2': {'GPT2LMHeadModel': 'gpt2', 'GPT2Tokenizer': 'gpt2', 'model_name': 'gpt2',
                                             'model_path': 'models/gpt2_model'}}, {
                                       'gpt2-german': {'GPT2LMHeadModel': 'dbmdz/german-gpt2',
                                                       'GPT2Tokenizer': 'dbmdz/german-gpt2',
                                                       'model_name': 'dbmdz/german-gpt2',
                                                       'model_path': 'models/german-gpt2'}}]}
        self.assertEqual(data_read, ref_string)

    def test_yml_loader_keyAcces(self):
        print(f"Running test ====> {self._testMethodName}")
        data_read = self.ymlLoader.data['System']['delimiter']
        ref_string = ';'
        self.assertEqual(data_read, ref_string)

    def test_yml_loader_changeKey(self):
        print(f"Running test ====> {self._testMethodName}")
        data_read = self.ymlLoader.data['System']['delimiter']
        ref_string = ';'
        self.assertEqual(data_read, ref_string)


if __name__ == '__main__':
    unittest.main()
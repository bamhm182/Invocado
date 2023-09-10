"""test_terraform.py

Tests for the Terraform class
"""

import git
import os
import sys
import unittest

from unittest.mock import MagicMock, patch, call

sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../../../src/middleware')))

import invocado  # noqa: E402


class TerraformTestClass(unittest.TestCase):
    def setUp(self):
        self.state = invocado._state.State()
        self.terraform = invocado.plugins.Terraform(self.state)
        self.terraform.db = MagicMock()

    @patch('glob.glob')
    def test_add_configs_to_db(self, mock_glob):
        self.terraform.db.terraform_dir = '/tmp/terraform'
        mock_glob.return_value = [
            '/tmp/terraform/one/main.tf',
            '/tmp/terraform/two/main.tf',
            '/tmp/terraform/three/zebra/main.tf',
            '/tmp/terraform/three/apple/main.tf',
            '/tmp/terraform/three/taco/main.tf',
        ]
        expected_adds = [
            'one',
            'three/apple',
            'three/taco',
            'three/zebra',
            'two',
        ]

        self.terraform.add_configs_to_db()

        self.terraform.db.add_tf_folders.assert_called_with(expected_adds)

    @patch('shutil.rmtree')
    @patch('git.Repo')
    def test_clone_repo(self, mock_git, mock_rmtree):
        self.terraform.db.terraform_repo = 'https://github.com/someone/something.git'
        self.terraform.db.terraform_dir = '/tmp/terraform_repo'
        mock_git.return_value.remotes.origin.urls = ['https://github.com/someone/something.git']

        self.terraform.clone_repo()
        mock_rmtree.assert_not_called()
        mock_git.return_value.git.reset.assert_called_with('--hard')
        mock_git.return_value.remotes.origin.pull.assert_called_with()

    @patch('shutil.rmtree')
    @patch('builtins.input')
    @patch('git.Repo')
    def test_clone_repo_first_clone(self, mock_git, mock_input, mock_rmtree):
        self.terraform.db.terraform_repo = 'https://github.com/someone/something.git'
        self.terraform.db.terraform_dir = '/tmp/terraform_repo_not_real'
        real_function = self.terraform.clone_repo
        self.terraform.clone_repo = MagicMock()

        mock_git.side_effect = git.exc.NoSuchPathError('No such path')

        real_function()

        mock_git.assert_has_calls([
            call('/tmp/terraform_repo_not_real'),
            call.clone_from('https://github.com/someone/something.git', '/tmp/terraform_repo_not_real'),
            call.clone_from().remotes.origin.urls.__contains__('https://github.com/someone/something.git')
        ])

    @patch('shutil.rmtree')
    @patch('builtins.input')
    @patch('git.Repo')
    def test_clone_repo_no_repo(self, mock_git, mock_input, mock_rmtree):
        self.terraform.db.terraform_repo = None
        mock_input.return_value = 'https://github.com/someone/something.git'
        self.terraform.db.terraform_dir = '/tmp/terraform_repo'
        mock_git.return_value.remotes.origin.urls = ['https://github.com/someone/something.git']

        self.terraform.clone_repo()

        mock_input.assert_called_with('Terraform Repo URL: ')
        mock_rmtree.assert_not_called()

    @patch('shutil.rmtree')
    @patch('builtins.input')
    @patch('git.Repo')
    def test_clone_repo_no_reset(self, mock_git, mock_input, mock_rmtree):
        self.terraform.db.terraform_repo = None
        mock_input.return_value = 'https://github.com/someone/something.git'
        self.terraform.db.terraform_dir = '/tmp/terraform_repo'
        mock_git.return_value.remotes.origin.urls = ['https://github.com/someone/something.git']

        self.terraform.clone_repo(reset=False)

        mock_input.assert_called_with('Terraform Repo URL: ')
        mock_rmtree.assert_not_called()
        mock_git.return_value.git.reset.assert_not_called()

    @patch('shutil.rmtree')
    @patch('builtins.input')
    @patch('git.Repo')
    def test_clone_repo_not_in_origin(self, mock_git, mock_input, mock_rmtree):
        real_function = self.terraform.clone_repo
        self.terraform.clone_repo = MagicMock()
        self.terraform.clone_repo.return_value = 'recursed'
        self.terraform.db.terraform_repo = None
        mock_input.return_value = 'https://github.com/someone/somethingelse.git'
        self.terraform.db.terraform_dir = '/tmp/terraform_repo'
        mock_git.return_value.remotes.origin.urls.side_effect = ['https://github.com/someone/something.git']

        self.assertEqual('recursed', real_function())

        mock_input.assert_called_with('Terraform Repo URL: ')
        mock_rmtree.assert_called_with('/tmp/terraform_repo')
        self.terraform.clone_repo.assert_called_with()

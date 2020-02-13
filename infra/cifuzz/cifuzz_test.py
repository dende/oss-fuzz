# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Test the functionality of the cifuzz module's functions:
1. Building fuzzers.
2. Running fuzzers.
"""

import os
import sys
import tempfile
import unittest
import unittest.mock

# pylint: disable=wrong-import-position
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cifuzz
import fuzz_target

# NOTE: This integration test relies on
# https://github.com/google/oss-fuzz/tree/master/projects/example project
EXAMPLE_PROJECT = 'example'


class BuildFuzzersIntegrationTest(unittest.TestCase):
  """Test build_fuzzers function in the utils module."""

  def test_valid_commit(self):
    """Test building fuzzers with valid inputs."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      out_path = os.path.join(tmp_dir, 'out')
      os.mkdir(out_path)
      self.assertTrue(
          cifuzz.build_fuzzers(
              EXAMPLE_PROJECT,
              'oss-fuzz',
              tmp_dir,
              commit_sha='0b95fe1039ed7c38fea1f97078316bfc1030c523'))
      self.assertTrue(os.path.exists(os.path.join(out_path, 'do_stuff_fuzzer')))

  def test_valid_pull_request(self):
    """Test building fuzzers with valid pull request."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      out_path = os.path.join(tmp_dir, 'out')
      os.mkdir(out_path)
      self.assertTrue(
          cifuzz.build_fuzzers(EXAMPLE_PROJECT,
                               'oss-fuzz',
                               tmp_dir,
                               pr_ref='refs/pull/1757/merge'))
      self.assertTrue(os.path.exists(os.path.join(out_path, 'do_stuff_fuzzer')))

  def test_invalid_pull_request(self):
    """Test building fuzzers with invalid pull request."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      out_path = os.path.join(tmp_dir, 'out')
      os.mkdir(out_path)
      self.assertFalse(
          cifuzz.build_fuzzers(EXAMPLE_PROJECT,
                               'oss-fuzz',
                               tmp_dir,
                               pr_ref='ref-1/merge'))

  def test_invalid_project_name(self):
    """Test building fuzzers with invalid project name."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      self.assertFalse(
          cifuzz.build_fuzzers(
              'not_a_valid_project',
              'oss-fuzz',
              tmp_dir,
              commit_sha='0b95fe1039ed7c38fea1f97078316bfc1030c523'))

  def test_invalid_repo_name(self):
    """Test building fuzzers with invalid repo name."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      self.assertFalse(
          cifuzz.build_fuzzers(
              EXAMPLE_PROJECT,
              'not-real-repo',
              tmp_dir,
              commit_sha='0b95fe1039ed7c38fea1f97078316bfc1030c523'))

  def test_invalid_commit_sha(self):
    """Test building fuzzers with invalid commit SHA."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      with self.assertRaises(AssertionError):
        cifuzz.build_fuzzers(EXAMPLE_PROJECT,
                             'oss-fuzz',
                             tmp_dir,
                             commit_sha='')

  def test_invalid_workspace(self):
    """Test building fuzzers with invalid workspace."""
    self.assertFalse(
        cifuzz.build_fuzzers(
            EXAMPLE_PROJECT,
            'oss-fuzz',
            'not/a/dir',
            commit_sha='0b95fe1039ed7c38fea1f97078316bfc1030c523',
        ))


class RunFuzzersIntegrationTest(unittest.TestCase):
  """Test build_fuzzers function in the cifuzz module."""

  def test_valid(self):
    """Test run_fuzzers with a valid build."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      out_path = os.path.join(tmp_dir, 'out')
      os.mkdir(out_path)
      self.assertTrue(
          cifuzz.build_fuzzers(
              EXAMPLE_PROJECT,
              'oss-fuzz',
              tmp_dir,
              commit_sha='0b95fe1039ed7c38fea1f97078316bfc1030c523'))
      self.assertTrue(os.path.exists(os.path.join(out_path, 'do_stuff_fuzzer')))
      run_success, bug_found = cifuzz.run_fuzzers(5, tmp_dir, EXAMPLE_PROJECT)
    self.assertTrue(run_success)
    self.assertTrue(bug_found)

  def test_invlid_build(self):
    """Test run_fuzzers with an invalid build."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      out_path = os.path.join(tmp_dir, 'out')
      os.mkdir(out_path)
      run_success, bug_found = cifuzz.run_fuzzers(5, tmp_dir, EXAMPLE_PROJECT)
    self.assertFalse(run_success)
    self.assertFalse(bug_found)

  def test_invalid_fuzz_seconds(self):
    """Tests run_fuzzers with an invalid fuzz seconds."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      out_path = os.path.join(tmp_dir, 'out')
      os.mkdir(out_path)
      run_success, bug_found = cifuzz.run_fuzzers(0, tmp_dir, EXAMPLE_PROJECT)
    self.assertFalse(run_success)
    self.assertFalse(bug_found)

  def test_invalid_out_dir(self):
    """Tests run_fuzzers with an invalid out directory."""
    run_success, bug_found = cifuzz.run_fuzzers(5, 'not/a/valid/path', EXAMPLE_PROJECT)
    self.assertFalse(run_success)
    self.assertFalse(bug_found)


class ParseOutputUnitTest(unittest.TestCase):
  """Test parse_fuzzer_output function in the cifuzz module."""

  def test_parse_valid_output(self):
    """Checks that the parse fuzzer output can correctly parse output."""
    test_case_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'test_files')
    test_output_path = os.path.join(test_case_path, 'example_fuzzer_output.txt')
    test_summary_path = os.path.join(test_case_path, 'bug_summary_example.txt')
    with tempfile.TemporaryDirectory() as tmp_dir:
      with open(test_output_path, 'r') as test_fuzz_output:
        cifuzz.parse_fuzzer_output(test_fuzz_output.read(), tmp_dir)
      result_files = ['bug_summary.txt']
      self.assertCountEqual(os.listdir(tmp_dir), result_files)

      # Compare the bug summaries.
      with open(os.path.join(tmp_dir, 'bug_summary.txt'), 'r') as bug_summary:
        detected_summary = bug_summary.read()
      with open(os.path.join(test_summary_path), 'r') as bug_summary:
        real_summary = bug_summary.read()
      self.assertEqual(detected_summary, real_summary)

  def test_parse_invalid_output(self):
    """Checks that no files are created when an invalid input was given."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      cifuzz.parse_fuzzer_output('not a valid output_string', tmp_dir)
      self.assertEqual(len(os.listdir(tmp_dir)), 0)


class ReproduceIntegrationTest(unittest.TestCase):
  """Test that only reproducible bugs are reported by CIFuzz."""

  def test_reproduce_true(self):
    """Checks CIFuzz reports an error when a crash is reproducible."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      out_path = os.path.join(tmp_dir, 'out')
      os.mkdir(out_path)
      self.assertTrue(
          cifuzz.build_fuzzers(
              EXAMPLE_PROJECT,
              'oss-fuzz',
              tmp_dir,
              commit_sha='0b95fe1039ed7c38fea1f97078316bfc1030c523'))
      with unittest.mock.patch.object(fuzz_target.FuzzTarget,
                                      'is_reproducible',
                                      return_value=True):
        run_success, bug_found = cifuzz.run_fuzzers(5, tmp_dir, EXAMPLE_PROJECT)
        self.assertTrue(run_success)
        self.assertTrue(bug_found)

  def test_reproduce_false(self):
    """Checks CIFuzz doesn't report an error when a crash isn't reproducible."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      out_path = os.path.join(tmp_dir, 'out')
      os.mkdir(out_path)
      self.assertTrue(
          cifuzz.build_fuzzers(
              EXAMPLE_PROJECT,
              'oss-fuzz',
              tmp_dir,
              commit_sha='0b95fe1039ed7c38fea1f97078316bfc1030c523'))
      with unittest.mock.patch.object(fuzz_target.FuzzTarget,
                                      'is_reproducible',
                                      return_value=False):
        run_success, bug_found = cifuzz.run_fuzzers(5, tmp_dir, EXAMPLE_PROJECT)
        self.assertTrue(run_success)
        self.assertFalse(bug_found)


class GetLatestBuildVersionUnitTest(unittest.TestCase):
  """Test the get_lastest_build_version function in the cifuzz module."""

  def test_get_valid_project(self):
    """Checks the latest build can be retrieved from gcs."""
    latest_build = cifuzz.get_lastest_build_version('yara')
    self.assertIsNotNone(latest_build)
    self.assertTrue(latest_build.endswith('.zip'))
    self.assertTrue('address' in latest_build)

    latest_build = cifuzz.get_lastest_build_version('envoy')
    self.assertIsNotNone(latest_build)
    self.assertTrue(latest_build.endswith('.zip'))
    self.assertTrue('address' in latest_build)


  def test_get_invalid_project(self):
    """Checks the latest build will return None when project doesn't exist."""
    self.assertIsNone(cifuzz.get_lastest_build_version('Not-a-project'))
    self.assertIsNone(cifuzz.get_lastest_build_version(''))


class DownloadOldBuildDirIntegrationTests(unittest.TestCase):
  """Test the download_old_build_dir in function in the cifuzz module."""

  def test_build_and_run_valid(self):
    """Tests that a project can be built and run using an old build."""

  def test_get_valid_project(self):
    """Checks the latest build can be retrieved from gcs."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      old_build_path = cifuzz.download_old_build_dir('yara', tmp_dir)
      self.assertIsNotNone(old_build_path)
      self.assertNotEqual(0, len(os.listdir(old_build_path)))

      old_build_path = cifuzz.download_old_build_dir('gonids', tmp_dir)
      self.assertIsNotNone(old_build_path)
      self.assertNotEqual(0, len(os.listdir(old_build_path)))

  def test_get_invalid_project(self):
    """Checks the latest build will return None when project doesn't exist."""
    with tempfile.TemporaryDirectory() as tmp_dir:
      self.assertIsNone(cifuzz.download_old_build_dir('Not-a-project', tmp_dir))
      self.assertIsNone(cifuzz.download_old_build_dir('', tmp_dir))

  def test_invalid_build_dir(self):
    """Checks the latest build will return None when project doesn't exist."""
    self.assertIsNone(cifuzz.download_old_build_dir('yara', ''))
    self.assertIsNone(cifuzz.download_old_build_dir('envoy', '/not/a/dir'))


if __name__ == '__main__':
  unittest.main()

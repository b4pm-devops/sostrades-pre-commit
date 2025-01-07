# Copyright 2025 Capgemini
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the HeaderUpdater class."""

from datetime import datetime
from shutil import copy

import pytest
from files import AIRBUS_HEADER_FILE
from files import CORRECT_FILES
from files import EXPECTED_FILES_DIR
from files import FILES_DIR
from files import NO_HEADER_FILE

from header_updater_hook.update_headers import HeaderUpdater


@pytest.fixture
def header_updater() -> HeaderUpdater:
    """A HeaderUpdater object."""
    return HeaderUpdater()


@pytest.fixture
def today() -> str:
    """Today's date."""
    return datetime.today.strftime("%Y/%m/%d")


@pytest.fixture
def year() -> str:
    """The current year."""
    return datetime.today().strftime("%Y")


def test_update_header_added_file(header_updater, year, tmp_path) -> None:
    """Check that an added file with no header is correctly updated."""
    tmp_file = tmp_path / NO_HEADER_FILE
    copy(FILES_DIR / NO_HEADER_FILE, tmp_file)
    with (EXPECTED_FILES_DIR / NO_HEADER_FILE).open() as f:
        expected_ouptut = f.read().format(year)
    file_was_modified = header_updater.check_header_added(tmp_file)
    assert file_was_modified
    with tmp_file.open() as f:
        assert f.read() == expected_ouptut


def test_update_header_modified_file(header_updater: HeaderUpdater, today, year, tmp_path) -> None:
    """Check that a modified file with Airbus header is correctly updated."""
    tmp_file = tmp_path / AIRBUS_HEADER_FILE
    copy(FILES_DIR / AIRBUS_HEADER_FILE, tmp_file)
    with (EXPECTED_FILES_DIR / AIRBUS_HEADER_FILE).open() as f:
        expected_output = f.read().format(today, year)
    file_was_modified = header_updater.check_header_modified(tmp_file)
    assert file_was_modified
    with tmp_file.open() as f:
        assert f.read() == expected_output


@pytest.mark.parametrize("filename", CORRECT_FILES)
def test_update_header_correct_files(header_updater: HeaderUpdater, filename: str, tmp_path) -> None:
    """Check that files with correct headers are left unchanged."""
    initial_file = FILES_DIR / filename
    tmp_file = tmp_path / filename
    copy(initial_file, tmp_file)
    with initial_file.open() as f:
        expected_output = f.read()
    file_was_modified = header_updater.check_header_modified(tmp_file)
    assert not file_was_modified
    with tmp_file.open() as f:
        assert f.read() == expected_output

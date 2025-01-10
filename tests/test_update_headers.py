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
from pathlib import Path
from shutil import copy

import pytest

from sostrades_pre_commit.update_headers import HeaderUpdater

FILES_DIR = Path(__file__).parent / "files"
"""The directory containing the test input files."""

EXPECTED_FILES_DIR = FILES_DIR / "expected"
"""The directory containing the templates for the expected modified files."""

AIRBUS_HEADER_FILE = "airbus_header.py"
"""The file with an original Airbus header."""

CAP_HEADER_FILE = "cap_header.py"
"""The file with a Capgemini header."""

MODIFIED_HEADER_EXPECTED_FILE = "modified_header.py"
"""The expected file output for files with modified headers."""

MODIFIED_HEADER_SINGLE_DATE_FILE = "modified_header_single_date.py"
"""The file with a modified header and a single modification date."""

MODIFIED_HEADER_TWO_DATES_FILE = "modified_header_two_dates.py"
"""The file with a modified header and a two modification dates."""

NO_HEADER_FILE = "no_header.py"
"""The file with no header."""


@pytest.fixture
def header_updater() -> HeaderUpdater:
    """A HeaderUpdater object."""
    return HeaderUpdater()


@pytest.fixture
def today() -> str:
    """Today's date."""
    return datetime.today().strftime("%Y/%m/%d")


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


def test_update_header_cap_file(header_updater, tmp_path) -> None:
    """Check that a file with a Capgemini header is left unchanged."""
    initial_file = FILES_DIR / CAP_HEADER_FILE
    tmp_file = tmp_path / CAP_HEADER_FILE
    copy(initial_file, tmp_file)
    with initial_file.open() as f:
        expected_output = f.read()
    # Check in the case the file is added
    file_was_modified = header_updater.check_header_added(tmp_file)
    assert not file_was_modified
    with tmp_file.open() as f:
        assert f.read() == expected_output
    # Check in the case the file is modified
    file_was_modified = header_updater.check_header_modified(tmp_file)
    assert not file_was_modified
    with tmp_file.open() as f:
        assert f.read() == expected_output


def test_update_header_modified_file(header_updater, today, year, tmp_path) -> None:
    """Check that a modified file with Airbus header is correctly updated."""
    tmp_file = tmp_path / AIRBUS_HEADER_FILE
    copy(FILES_DIR / AIRBUS_HEADER_FILE, tmp_file)
    with (EXPECTED_FILES_DIR / AIRBUS_HEADER_FILE).open() as f:
        expected_output = f.read().format(today, year)
    file_was_modified = header_updater.check_header_modified(tmp_file)
    assert file_was_modified
    with tmp_file.open() as f:
        assert f.read() == expected_output


@pytest.mark.parametrize("filename", [MODIFIED_HEADER_SINGLE_DATE_FILE, MODIFIED_HEADER_TWO_DATES_FILE])
def test_update_header_modified_files(header_updater, today, year, filename, tmp_path) -> None:
    """Check that files with modified headers are correctly updated."""
    tmp_file = tmp_path / filename
    copy(FILES_DIR / filename, tmp_file)
    with (EXPECTED_FILES_DIR / MODIFIED_HEADER_EXPECTED_FILE).open() as f:
        expected_output = f.read().format(today, year)
    file_was_modified = header_updater.check_header_modified(tmp_file)
    assert file_was_modified
    with tmp_file.open() as f:
        assert f.read() == expected_output


def test_update_header_modified_files_correct(header_updater, today, year, tmp_path) -> None:
    """Check that a file with a modified header with the correct date is left
    unchanged."""
    tmp_file = tmp_path / MODIFIED_HEADER_EXPECTED_FILE
    with (EXPECTED_FILES_DIR / MODIFIED_HEADER_EXPECTED_FILE).open() as f:
        expected_output = f.read().format(today, year)
    with tmp_file.open("w") as f:
        f.write(expected_output)
    file_was_modified = header_updater.check_header_modified(tmp_file)
    assert not file_was_modified
    with tmp_file.open() as f:
        assert f.read() == expected_output

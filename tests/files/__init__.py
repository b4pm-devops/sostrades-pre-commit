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

"""The files for the HeaderUpdater tests."""

from pathlib import Path

FILES_DIR = Path.cwd()
"""The directory containing the test input files."""

EXPECTED_FILES_DIR = FILES_DIR / "expected"
"""The directory containing the templates for the expected modified files."""

AIRBUS_HEADER_FILE = "airbus_header.py"
"""The file with an original Airbus header."""

NO_HEADER_FILE = "no_header.py"
"""The file with no header."""

CORRECT_FILES = ["cap_header.py", "modified_header.py"]
"""The files with correct headers that shall be left unchanged."""

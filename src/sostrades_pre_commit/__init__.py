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

"""The pre-commit hooks for SoSTrades development."""

from __future__ import annotations

from pathlib import Path

APACHE_LICENSE_PATH: Path = Path(__file__).parent / "apache_license.txt"
"""The Capgemini header template file."""

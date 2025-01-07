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

"""A script that update the headers.

Called by pre-commit at every commit.
"""

from argparse import ArgumentParser
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

from git import Repo

from header_updater_hook import APACHE_LICENSE_PATH


class HeaderUpdater:
    """A class that checks and updates the headers of commited files."""

    AIRBUS_COPYRIGHT: str = "Copyright 2022 Airbus SAS"
    """The Airbus copyright line."""

    CAP_COPYRIGHT: str = "Copyright {} Capgemini"
    """The Capgemini copyright line, without the year."""

    HEADER_PATTERN: str = "'''\n{}\n'''"
    """The expected header pattern."""

    MODIFICATIONS_PATTERN = "Modifications on {}"
    """The pattern for the line added to modified files, without the Capgemini copyright."""

    airbus_header: str
    """The Airbus header."""

    cap_header: str
    """The Capgemini header."""

    modified_header: str
    """The Airbus header with the additional `Modifications...` line."""

    modified_header_regex: str
    """The regex to match the modifed Airbus license for any dates and year."""

    def __init__(self) -> None:  # noqa: D107
        with APACHE_LICENSE_PATH.open() as f:
            apache_license = f.read()

        # Set the Airbus header
        airbus_license = f"{self.AIRBUS_COPYRIGHT}\n\n{apache_license}"
        self.airbus_header = self.HEADER_PATTERN.format(airbus_license)

        # Set the Capgemini headers with the current date/year
        today = datetime.today().strftime("%Y/%m/%d")
        current_year = datetime.today().strftime("%Y")
        new_cap_copyright = self.CAP_COPYRIGHT.format(current_year)
        cap_license = f"{new_cap_copyright}\n\n{apache_license}"
        self.cap_header = self.HEADER_PATTERN.format(cap_license)
        modif_line = f"{self.MODIFICATIONS_PATTERN.format(today)} {new_cap_copyright}"
        modif_license_lines = [self.AIRBUS_COPYRIGHT, modif_line, "", apache_license]
        modified_license = "\n".join(modif_license_lines)
        self.modified_header = self.HEADER_PATTERN.format(modified_license)

    def update_headers(self, filenames: Iterable[str]) -> int:
        """Update the headers for a list of files.

        Args:
            files: The files to update.
            repo_dir: The path to the repo dir where the commit is being made.

        Returns:
            1 if some files were modified, 0 otherwise.
        """
        repo_dir = Path.cwd()
        repo = Repo(repo_dir)
        diff = repo.head.commit.diff(None)
        added = [*diff.iter_change_type("A")]
        modified = [*diff.iter_change_type("M")]
        files_were_changed = False

        for file_name in filenames:
            file_path = repo_dir / file_name
            if file_name in added:
                files_were_changed += self.check_header_added(file_path)
            elif file_name in modified:
                files_were_changed += self.check_header_modified(file_path)
            return int(files_were_changed)
        return None

    def check_header_added(self, file_path: Path) -> bool:
        """Check the header for an added file and change it if needed.

        Args:
            file_path: The path of the file to check.

        Returns:
            Whether the file was changed.
        """
        with file_path.open("w+") as f:
            file_content = f.read()
            if file_content.startswith(self.cap_header):
                return False
            new_file_content = self.cap_header + file_content
            f.write(new_file_content)
        return True

    def check_header_modified(self, file_path: Path) -> bool:
        """Check the header for a modified file and changes it if needed.

        If the file has the original Airbus header, replace it with the `modified` header.
        Else, this means that it must already have a Capgemini or `modified` header, so change nothing.

        Args:
            file_path: The path of the file to check.

        Returns:
            Whether the file was changed.
        """
        with file_path.open("w+") as f:
            file_content = f.read()
        if file_content.startswith(self.airbus_header):
            new_file_content = file_content.replace(self.airbus_header, self.modified_header)
            f.write(new_file_content)
            return True
        return False


def main() -> int:
    """The main script called by pre-commit."""
    parser = ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="filenames to check")
    args = parser.parse_args()
    header_updater = HeaderUpdater()
    files_were_modified = header_updater.update_headers(args.filenames)
    exit(int(not files_were_modified))

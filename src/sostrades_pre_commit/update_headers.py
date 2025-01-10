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
from re import search

from git import Repo

from sostrades_pre_commit import APACHE_LICENSE_PATH


class HeaderUpdater:
    """A class that checks and updates the headers of commited files."""

    AIRBUS_COPYRIGHT: str = "Copyright 2022 Airbus SAS"
    """The Airbus copyright line."""

    CAP_COPYRIGHT: str = "Copyright {} Capgemini"
    """The Capgemini copyright line, without the year."""

    HEADER_PATTERN: str = "'''\n{}\n'''\n"
    """The expected header pattern."""

    MODIFICATIONS_PATTERN = "Modifications on {}"
    """The pattern for the line added to modified files, without the Capgemini copyright."""

    airbus_header: str
    """The Airbus header."""

    cap_header: str
    """The Capgemini header."""

    modified_header: str
    """The Airbus header with the additional `Modifications...` line."""

    start_modif_regex: str
    """The regex to match the beginning of the `modified` header for already modified
    Airbus files."""

    today: str
    """Today's date in the Y/m/d format."""

    updated_modified_pattern: str
    """The pattern for the `Modifications on...` line
    for files that already have a `modified` header.
    It is made of the MODIFICATION_PATTERN and CAP_COPYRIGHT
    filled with the current date and year.
    It is to be filled with the first modification date of the file.
    """

    def __init__(self) -> None:  # noqa: D107
        with APACHE_LICENSE_PATH.open() as f:
            apache_license = f.read()

        # Set the Airbus header
        airbus_license = f"{self.AIRBUS_COPYRIGHT}\n\n{apache_license}"
        self.airbus_header = self.HEADER_PATTERN.format(airbus_license)

        # Set the beginning of the `modified` pattern for matching
        self.start_modif_regex = f"{self.MODIFICATIONS_PATTERN.format('(.+)')} {self.CAP_COPYRIGHT.format('20(..)')}"

        # Set the Capgemini headers with the current date/year
        self.today = datetime.today().strftime("%Y/%m/%d")
        current_year = datetime.today().strftime("%Y")
        new_cap_copyright = self.CAP_COPYRIGHT.format(current_year)
        cap_license = f"{new_cap_copyright}\n\n{apache_license}"
        self.cap_header = self.HEADER_PATTERN.format(cap_license)
        modif_line = f"{self.MODIFICATIONS_PATTERN.format(self.today)} {new_cap_copyright}"
        modif_license_lines = [self.AIRBUS_COPYRIGHT, modif_line, "", apache_license]
        modified_license = "\n".join(modif_license_lines)
        self.modified_header = self.HEADER_PATTERN.format(modified_license)
        modification_dates_pattern = "{}-" + self.today
        self.updated_modified_pattern = (
            f"{self.MODIFICATIONS_PATTERN.format(modification_dates_pattern)} {new_cap_copyright}"
        )

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
        added = [item.a_path for item in diff.iter_change_type("A")]
        modified = [item.a_path for item in diff.iter_change_type("M")]
        files_were_changed = False

        for file_name in filenames:
            file_path = repo_dir / file_name
            if file_name in added:
                files_were_changed += self.check_header_added(file_path)
            elif file_name in modified:
                files_were_changed += self.check_header_modified(file_path)
        return int(files_were_changed)

    def check_header_added(self, file_path: Path) -> bool:
        """Check the header for an added file and change it if needed.

        Args:
            file_path: The path of the file to check.

        Returns:
            Whether the file was changed.
        """
        with file_path.open() as f:
            file_content = f.read()
        if file_content.startswith(self.cap_header):
            return False
        new_file_content = self.cap_header + file_content
        with file_path.open("w") as f:
            f.write(new_file_content)
        return True

    def check_header_modified(self, file_path: Path) -> bool:
        """Check the header for a modified file and changes it if needed.

        If the file has the original Airbus header, replace it with the `modified` header.
        If it already has a `modified` header with an older date, update the modification dates and copyright.
        Else, change nothing.

        Args:
            file_path: The path of the file to check.

        Returns:
            Whether the file was changed.
        """
        with file_path.open() as f:
            file_content = f.read()
        if file_content.startswith(self.airbus_header):
            new_file_content = file_content.replace(self.airbus_header, self.modified_header)
        elif re_match := search(pattern=self.start_modif_regex, string=file_content):
            modif_line = re_match.group(0)
            modif_dates = modif_line.split(" ")[2].split("-")
            first_modif_date = modif_dates[0]
            second_modif_date = modif_dates[1] if len(modif_dates) > 1 else None
            if second_modif_date == self.today:
                # Header is already up to date; do nothing
                return False
            updated_modif_line = self.updated_modified_pattern.format(first_modif_date)
            new_file_content = file_content.replace(modif_line, updated_modif_line)
        else:
            return False
        with file_path.open("w") as f:
            f.write(new_file_content)
        return True


def main() -> int:
    """The main script called by pre-commit."""
    parser = ArgumentParser()
    parser.add_argument("filenames", nargs="*", help="filenames to check")
    args = parser.parse_args()
    header_updater = HeaderUpdater()
    files_were_modified = header_updater.update_headers(args.filenames)
    exit(int(files_were_modified))

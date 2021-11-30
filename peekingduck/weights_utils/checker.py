# Copyright 2021 AI Singapore
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Checks for model weights in weights folder.
"""

from pathlib import Path
from typing import List


def has_weights(root: Path, weights_paths: List[str]) -> bool:
    """Checks for model weight paths from weights folder.

    Args:
        root (:obj:`Path`): Path of ``peekingduck`` root folder.
        weights_paths (:obj:`List[str]`): List of files/directories to check
            whether model weights exist.
    Returns:
        (:obj:`bool`): ``True`` if specified files/directories in
        ``weights_paths`` exist, else ``False``.
    """
    # Check for whether weights dir even exist. If not make directory
    # Empty directory should then return False
    weights_dir = root.parent / "peekingduck_weights"
    if not weights_dir.exists():
        weights_dir.mkdir()
        return False

    return all((root / path).exists() for path in weights_paths)

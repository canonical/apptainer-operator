# Copyright 2025-2026 Vantage Compute Corporation
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

"""Manage and operate ``apptainer``."""

import shutil
from pathlib import Path

from charmed_hpc_libs.ops import AptLifecycleManager, systemctl

_APPARMOR_PROFILE_PATH = Path("/etc/apparmor.d/apptainer")
_APPARMOR_PROFILE = """\
abi <abi/4.0>,
include <tunables/global>
profile apptainer /usr/lib/@{multiarch}/apptainer/bin/starter flags=(unconfined) {
  userns,
}
"""


class ApptainerManager(AptLifecycleManager):
    """Manage the ``apptainer`` installation of a machine."""

    def __init__(self) -> None:
        super().__init__(
            "apptainer", additional_packages=["fuse2fs", "gocryptfs", "squashfuse", "uidmap"]
        )

        # Remove bindings from `AptLifecycleManager` and use overrides below.
        del self.install
        del self.remove

    @property
    def executable_path(self) -> Path:
        """Path to the ``apptainer`` executable on this machine.

        Raises:
            FileNotFoundError: If ``apptainer`` cannot be found on ``PATH``.
        """
        path = shutil.which("apptainer")
        if path is None:
            raise FileNotFoundError("`apptainer` executable not found on PATH")

        return Path(path)

    def install(self, *, update: bool = True) -> None:
        """Install ``apptainer`` and apply ``apptainer``-specific post-install configuration.

        Args:
            update: If `True`, update the `apt` cache before installing packages.
        """
        self._ops_manager.install(update=update)
        # FIXME: The `apptainer` package from Ubuntu Universe currently does not ship the required
        #   apparmor profile to enable `apptainer` to create unprivileged user namespaces when
        #   running containers. Apply our own custom profile here so that non-root users can
        #   successfully run containers while the fix for the package is worked on upstream
        #   in Debian.
        _APPARMOR_PROFILE_PATH.write_text(_APPARMOR_PROFILE)
        systemctl("reload", "apparmor")

    def remove(self, *, purge: bool = True) -> None:
        """Remove ``apptainer`` and clean up custom apparmor profile."""
        self._ops_manager.remove(purge=purge)
        _APPARMOR_PROFILE_PATH.unlink(missing_ok=True)
        systemctl("reload", "apparmor")

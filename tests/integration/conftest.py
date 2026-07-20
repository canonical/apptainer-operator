# Copyright 2025 Canonical Ltd.
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

"""Configure `apptainer` charm integration tests."""

import logging
import os
from collections.abc import Iterator
from pathlib import Path

import jubilant
import pytest

logger = logging.getLogger(__name__)
LOCAL_APPTAINER = Path(apptainer) if (apptainer := os.getenv("LOCAL_APPTAINER")) else None


@pytest.fixture(scope="session")
def juju(request: pytest.FixtureRequest) -> Iterator[jubilant.Juju]:
    """Yield wrapper for interfacing with the `juju` CLI command."""
    keep_models = bool(request.config.getoption("--keep-models"))

    with jubilant.temp_model(keep=keep_models) as juju:
        juju.wait_timeout = 10 * 60

        yield juju

        if request.session.testsfailed:
            log = juju.debug_log(limit=1000)
            print(log, end="")


@pytest.fixture(scope="module")
def base(request: pytest.FixtureRequest) -> str:
    """Get the base to deploy the `apptainer` charm on."""
    return request.config.getoption("--base")


@pytest.fixture(scope="module")
def apptainer() -> Path | str:
    """Get `apptainer` charm to use for integration tests.

     If the `LOCAL_APPTAINER` environment variable is not set,
    the `apptainer` charm will be pulled from Charmhub instead.

    Returns:
        `Path` object if using a local `apptainer` charm. `str` if pulling from Charmhub.
    """
    if not LOCAL_APPTAINER:
        logger.info("pulling `apptainer` charm from charmhub")
        return "apptainer"

    logger.info("using local `apptainer` charm located at %s", LOCAL_APPTAINER)
    return LOCAL_APPTAINER


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--base",
        action="store",
        default="ubuntu@26.04",
        help="the base to deploy the apptainer charm on during the integration tests",
    )
    parser.addoption(
        "--keep-models",
        action="store_true",
        default=False,
        help="keep temporarily created models",
    )

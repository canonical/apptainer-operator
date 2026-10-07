#!/usr/bin/env python3
# Copyright 2026 Canonical Ltd.
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

"""BDD step definitions for apptainer edge tests."""

from pytest_bdd import parsers, scenarios, then
from pytest_jubilant_bdd import Context

from constants import EDGE_FEATURES

scenarios(*EDGE_FEATURES)


@then(parsers.parse("the ssh output field '{field}' should be '{value}'"))
def assert_ssh_output_field(context: Context, field: str, value: str) -> None:
    """Assert a KEY=VALUE field is present in the next `juju ssh` output (LIFO order)."""
    output = context.ssh_results.pop()
    assert f"{field}={value}" in output


@then(parsers.parse("the ssh output should contain '{value}'"))
def assert_ssh_output_contents(context: Context, value: str) -> None:
    output = context.ssh_results.pop()
    assert value in output, f"Value '{value}' is not in output '{output}'"

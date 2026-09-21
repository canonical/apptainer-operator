#!/usr/bin/env just --justfile
# Copyright 2025-2026 Canonical Ltd.
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

# Manage charm test plans with gherkinator
mod gherkinator "tests/integration/"

uv := require("uv")

project_dir := justfile_directory()
src_dir := project_dir / "src"
tests_dir := project_dir / "tests"

export PY_COLORS := "1"
export PYTHONBREAKPOINT := "pdb.set_trace"
export PYTHONPATH := project_dir / "src"

uv_run := "uv run --frozen --extra dev"

[private]
default:
    @just help

# Prepare the local environment
setup: env

# Apply coding style standards to code
fmt: lock
    {{uv_run}} ruff format {{src_dir}} {{tests_dir}}
    {{uv_run}} ruff check --fix {{src_dir}} {{tests_dir}}

# Check code against coding style standards
lint: lock
    {{uv_run}} codespell {{src_dir}}
    {{uv_run}} ruff check {{src_dir}}

# Run static type checker on code
typecheck: lock
    {{uv_run}} pyright

# Run unit tests
unit *args: lock
    {{uv_run}} coverage run \
        --source {{src_dir}} \
        -m pytest \
        --tb native \
        -v -s {{args}} {{tests_dir / "unit"}}
    {{uv_run}} coverage report
    {{uv_run}} coverage xml -o {{project_dir / "cover" / "coverage.xml"}}

# Run integration tests
integration *args: lock
    #!/usr/bin/env bash
    set -euxo pipefail

    {{uv_run}} pytest \
        -v \
        --tb native \
        -s \
        --log-cli-level=INFO \
        {{args}} \
        {{tests_dir / "integration"}}

# Run tests for specified targets, or all tests if none specified
test *targets:
    #!/usr/bin/env bash
    if [ "{{targets}}" = "" ]; then
        just test-all
        exit 0
    fi

    for target in {{targets}}; do
        if just --show $target > /dev/null 2>&1; then
            echo "Running $target tests..."
            just $target
        else
            echo "$target tests not found, skipping."
            exit 1
        fi
    done

# Run all test suites
test-all: unit integration

# Build specified artifacts, or all artifacts if none specified
build *args:
    charmcraft -v pack {{args}}

# Clean project directory
clean:
    rm -rf {{project_dir / ".coverage"}}
    rm -rf {{project_dir / "cover"}}
    rm -rf {{project_dir / ".pytest_cache"}}
    rm -rf {{project_dir / ".ruff_cache"}}
    find {{project_dir}} -name __pycache__ -type d | xargs rm -rf
    rm -f {{project_dir / "apptainer.charm"}}
    rm -f {{project_dir / "apptainer_"}}*.charm

# Apply static checks
check: lint typecheck

# Regenerate uv.lock
lock:
    uv lock

# Create a development environment
env: lock
    uv sync --extra dev

# Upgrade uv.lock with the latest dependencies
upgrade:
    uv lock --upgrade

# Generate publishing token for Charmhub
generate-charmhub-token:
    charmcraft login \
        --export=.charmhub.secret \
        --charm=apptainer \
        --permission=package-manage-metadata \
        --permission=package-manage-releases \
        --permission=package-manage-revisions \
        --permission=package-view-metadata \
        --permission=package-view-releases \
        --permission=package-view-revisions \
        --ttl=31536000  # 365 days

# Show available recipes
help:
    @just --list --unsorted

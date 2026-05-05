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

variable "app_name" {
  description = "The Juju application name"
  type        = string
  default     = "apptainer"
}

variable "base" {
  description = "Operating system base to use for the deployed application (for example, ubuntu@24.04)"
  type        = string
  default     = null
}

variable "channel" {
  description = "Charm channel to deploy from"
  type        = string
  default     = "latest/beta"
}

variable "config" {
  description = "Map of charm configuration options"
  type        = map(string)
  default     = {}
}

variable "model_uuid" {
  description = "UUID of the Juju model to deploy the charm into"
  type        = string
  nullable    = false
}

variable "revision" {
  description = "Charm revision to deploy. Null deploys the latest on the given channel"
  type        = number
  default     = null
}

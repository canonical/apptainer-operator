# Apptainer operator

[![apptainer charm tests](https://github.com/canonical/apptainer-operator/actions/workflows/ci.yaml/badge.svg)](https://github.com/canonical/apptainer-operator/actions/workflows/ci.yaml)
[![Release to `latest/edge` channel on Charmhub](https://github.com/canonical/apptainer-operator/actions/workflows/release.yaml/badge.svg)](https://github.com/canonical/apptainer-operator/actions/workflows/release.yaml)
![GitHub License](https://img.shields.io/github/license/canonical/apptainer-operator)
[![Matrix](https://img.shields.io/matrix/ubuntu-hpc%3Amatrix.org?logo=matrix&label=ubuntu-hpc)](https://matrix.to/#/#hpc:ubuntu.com)

A [Juju](https://juju.is) charm for automating the full lifecycle operations of 
[Apptainer](https://apptainer.org), a secure and portable container platform designed 
for ease-of-use on shared systems and high-performance computing (HPC) environments.

## ✨ Getting Started

To deploy the Apptainer operator, you'll need to integrate it with a principal charm:

```shell
juju deploy ubuntu --base ubuntu@24.04
juju deploy apptainer --channel edge
juju integrate apptainer ubuntu
```

You can use `juju status` to inspect the deployment status with:

```text
$ juju status
Model              Controller              Cloud/Region         Version  SLA          Timestamp
apptainer          charmed-hpc-controller  localhost/localhost  3.6.7    unsupported  14:15:39-04:00

App        Version  Status  Scale  Charm      Channel        Rev  Exposed  Message
apptainer  1.3.4    active      1  apptainer                   0  no       
ubuntu     24.04    active      1  ubuntu     latest/stable   26  no       

Unit            Workload  Agent  Machine  Public address  Ports  Message
ubuntu/0*       active    idle   0        10.196.162.159         
  apptainer/0*  active    idle            10.196.162.159         

Machine  State    Address         Inst id        Base          AZ  Message
0        started  10.196.162.159  juju-a3584f-0  ubuntu@24.04      Running
```

Now you can run container images using Apptainer:

```shell
$ juju ssh apptainer/0 -- apptainer exec docker://ubuntu/python:3.10-22.04 python3 --version
juju ssh apptainer/0 -- apptainer exec docker://ubuntu/python:3.10-22.04 python3 --version
INFO:    Converting OCI blobs to SIF format
INFO:    Starting build...
Copying blob 128a37428dc8 done   | 
Copying blob b3ae6f4616bf done   | 
Copying blob 9ff6808be1ee done   | 
Copying config c967a28055 done   | 
Writing manifest to image destination
2025/06/16 18:21:44  info unpack layer: sha256:128a37428dc8f18a9bdaa585ec0f8ace4561b05fc95eee0102d67e2b1741d224
2025/06/16 18:21:44  info unpack layer: sha256:9ff6808be1eefee42d64f815a634a35192d0551a8afc1fb0f93dcb876acc8d0b
2025/06/16 18:21:44  info unpack layer: sha256:b3ae6f4616bfd32d63e8714d3363b1df0d734bcd55c07264cec1ee77f6f23dae
INFO:    Creating SIF file...
Python 3.10.12
Connection to 10.196.162.159 closed.
```

## 🤔 What's next?

If you want to learn more about all the things you can do with the Apptainer operator,
or have any further questions on what you can do with the operator, here are some
further resources for you to explore:

* [Charmed HPC documentation](https://canonical-charmed-hpc.readthedocs-hosted.com/latest/)
* [Open an issue](https://github.com/canonical/apptainer-operator/issues/new?title=ISSUE+TITLE&body=*Please+describe+your+issue*)

## 🛠️ Development

The project uses [just](https://github.com/casey/just) and [uv](https://github.com/astral-sh/uv) for
development, which provides some useful commands that will help you while hacking on the Apptainer operator:

```shell
just fmt            # Apply formatting standards to code.
just lint           # Check code against coding style standards.
just woke           # Run inclusive naming checks.
just typecheck      # Run static type checks.
just unit           # Run unit tests.
```

To run the Apptainer operator integration tests, you'll need to have both
[Juju](https://juju.is) and [LXD](https://ubuntu.com/lxd) installed
on your machine:

```shell
just integration    # Run integration tests.
```

If you're interested in contributing, take a look at our [contributing guidelines](./CONTRIBUTING.md).

## 🤝 Project and community

The Apptainer operator is a project of the [Ubuntu High-Performance Computing community](https://ubuntu.com/community/governance/teams/hpc).
Interested in contributing bug fixes, patches, documentation, or feedback? Want to join the 
Ubuntu HPC community? You’ve come to the right place 🤩

Here’s some links to help you get started with joining the community:

* [Ubuntu Code of Conduct](https://ubuntu.com/community/ethos/code-of-conduct)
* [Contributing guidelines](./CONTRIBUTING.md)
* [Join the conversation on Matrix](https://matrix.to/#/#hpc:ubuntu.com)
* [Get the latest news on Discourse](https://discourse.ubuntu.com/c/hpc/151)

## 📋 License

The Apptainer operator is free software, distributed under the Apache Software License, version 2.0.
See the [Apache-2.0 LICENSE](./LICENSE) file for further details.

Apptainer is both licensed under the BSD 3-Clause License and the LBNL License. 
See the upstream Apptainer [LICENSE](https://github.com/apptainer/apptainer/blob/main/LICENSE.md) file
for further licensing information about Apptainer.
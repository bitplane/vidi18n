# Development

## Runtime choice

Rootless Podman is the preferred container runtime for vidi18n. It supports the
project's goal that an ordinary user should be able to operate a node without a
privileged container daemon.

This does not mean containers themselves are a security sandbox or that every
user can run rootless Podman without system preparation. Linux hosts generally
need subordinate UID/GID ranges and suitable user-namespace networking and
storage support.

The project should use OCI images and the Compose specification rather than
Podman-only application APIs. This keeps development accessible to other
rootless OCI runtimes and avoids coupling the future federation protocol to a
deployment tool.

## Prerequisites

- Python 3.10 or newer
- FFmpeg
- Podman
- A Compose provider usable by `podman compose`
- `make` for the existing helper targets

Check the container tools with:

```bash
podman info
podman compose version
```

Podman's `compose` command delegates to an installed Compose provider. Consult
the Podman documentation if the second command reports that none is installed.

## Current prototype

The existing Compose application can be invoked with:

```bash
make node
```

It is historical prototype infrastructure, not yet the MVP described in these
documents. In particular, it has no complete transcription/translation
pipeline, and its Redis, downloader, and bind-mounted storage configuration
should not be exposed to untrusted networks.

The current Python test workflow is:

```bash
make install
make test
```

## Intended workflow

The stable development entry points are:

```bash
make install
make test
make node
make clean
```

`make node` should start the rootless Podman development deployment. Tests
should run directly in the Python virtual environment by default so that
contributors do not need to rebuild containers for every change.

To pass additional options to Compose, invoke the helper directly:

```bash
build/podman.sh --detach
```

## Container guidelines

- Run services as a non-root user inside rootless containers.
- Pin image versions; do not use mutable `latest` tags.
- Store artifacts and database files in user-owned named volumes.
- Add health checks and bounded startup dependencies.
- Apply CPU, memory, process, file-size, and job-duration limits.
- Do not mount the Podman socket into media workers.
- Do not give media workers access to credentials they do not require.
- Treat all uploaded or remotely fetched media as hostile.
- Keep local development and public-node configurations distinct.

## Documentation

Build the MkDocs site after installing development dependencies:

```bash
make docs
```

The root README states the mission and current status. Architectural decisions
belong in `docs/architecture.md`; work required for the first useful release
belongs in `docs/mvp.md`.

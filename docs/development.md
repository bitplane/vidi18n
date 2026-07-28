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

## Current progressive slice

The existing Compose application can be invoked with:

```bash
make node
```

This starts the URL-based English-to-French vertical slice. The manager queues
work in Redis Streams; separate workers resolve and chunk the video, transcribe,
translate, and package it; the browser receives replayable cues over SSE while
the video remains playable through an HTTP range proxy. It is development
infrastructure and must not be exposed to untrusted networks.

The current Python test workflow is:

```bash
make install
make test
make test-integration
```

The integration target builds an isolated Podman project, generates and serves
a local spoken-video fixture, exercises URL resolution and byte-range playback,
checks that an SSE caption arrives before the job finishes, reconnects the cue
stream, and verifies the completed WebVTT artifact. It removes its containers
and volumes when finished.

The default node uses deterministic transcription and translation adapters so
the pipeline can be exercised without model downloads. To use the first local
English-to-French adapters:

```bash
make models
make node-local
```

`make models` is the only command which downloads model data. It writes a
manifest into the `vidi18n_models` volume and verifies that both processors can
load. Recheck an existing installation without network access with:

```bash
make models-verify
```

The local CPU node keeps one `faster-whisper` `tiny.en` model and one Argos
English-to-French translator in memory per worker. Its defaults are CPU `int8`
with four transcription threads. Override the thread count with
`VIDI18N_WHISPER_CPU_THREADS`.

Run the opt-in real-model acceptance benchmark with:

```bash
make test-model-cpu
```

It uses the generated 66-second fixture and requires the first translated cue
within 20 seconds and a total real-time factor below 1.0. It also asserts that
the API reports real processor provenance, preventing deterministic adapters
from producing a false-positive result.

NVIDIA GPU transcription is an optional rootless CDI deployment:

```bash
make test-model-gpu
build/podman-compose.sh --file compose.gpu.yaml up --build
```

The host must provide a working NVIDIA driver, NVIDIA Container Toolkit CDI
configuration, CUDA 12-compatible hardware, and the `nvidia.com/gpu=all` CDI
device. GPU mode is explicit and fails rather than silently falling back to
CPU. Translation remains in the independent CPU-based Argos worker.

## Intended workflow

The stable development entry points are:

```bash
make install
make test
make node
make clean
```

`make node` starts the rootless Podman development deployment. Tests run
directly in the Python virtual environment by default so that
contributors do not need to rebuild containers for every change.

To pass additional options to Compose, invoke the helper directly:

```bash
build/podman.sh --detach
```

## Container guidelines

- Run services as a non-root user inside rootless containers.
- Pin image versions; do not use mutable `latest` tags.
- Store Redis data and artifacts in user-owned named volumes.
- Add health checks and bounded startup dependencies.
- Apply CPU, memory, process, file-size, and job-duration limits.
- Do not mount the Podman socket into media workers.
- Do not give media workers access to credentials they do not require.
- Treat all uploaded or remotely fetched media as hostile.
- Keep local development and public-node configurations distinct.

## Service development

Services communicate through versioned Redis events and artifact references.
Do not import another service's implementation to invoke its work directly.
Shared domain schemas and event envelopes belong in a small common package;
service-specific processing remains behind its stream contract.

Worker handlers must be safe to run more than once. Tests should cover duplicate
delivery, interruption before acknowledgement, retry exhaustion, and recovery
of claimed work in addition to the successful path.

Pub/Sub is appropriate for transient progress notifications. Work which must
survive a worker restart belongs in a Redis Stream and is acknowledged only
after its state and output are durable.

Workers publish short-lived readiness records only after their processors have
loaded successfully. Job responses include processor provenance and Redis-timed
latency, stage, and real-time-factor measurements. Model bootstrap time is
reported separately from warm-node job latency.

## Documentation

Build the MkDocs site after installing development dependencies:

```bash
make docs
```

The root README states the mission and current status. Architectural decisions
belong in `docs/architecture.md`; work required for the first useful release
belongs in `docs/mvp.md`.

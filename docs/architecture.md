# Architecture

## Goal

vidi18n is an open translation layer for video. A deployment may initially run
as a single node, but its useful outputs must not belong to that node. Another
implementation should be able to identify compatible media, verify an artifact,
and use or mirror it without access to the producer's database.

The architecture therefore separates media identity, translation artifacts,
job execution, discovery, and trust.

Within a node, Redis coordinates independently deployable services. Between
nodes, portable manifests and artifacts provide interoperability. Redis is not
the federation protocol, but it is a deliberate part of the node architecture.

## Conceptual flow

```text
media input
    |
    v
identify media -----> look for reusable artifacts
    |                         |
    | missing work            | found
    v                         v
extract audio             verify provenance
    |
    v
chunk -> transcribe -> translate -> review
               \          /
                v        v
              timed artifacts
                    |
                    v
          manifest + WebVTT track
                    |
                    v
             player / export
```

The MVP runs this flow on one trusted node. Later versions can replace artifact
discovery and individual job executors without changing the player-facing
result.

## Architectural boundaries

### Media identity

A URL is a locator, not an identity. The same video can move, have multiple
mirrors, or be encoded at several resolutions. Conversely, the content at a URL
can change.

The MVP should assign:

- an immutable identifier to the exact input bytes;
- a separate, versioned perceptual or media fingerprint where practical; and
- private source locators which are never included in public artifacts by
  default.

Exact hashes give safe deduplication. Cross-encode matching is useful but can
produce false matches, so it must be versioned and treated as a claim rather
than an unquestionable identity.

### Artifacts

An artifact is an immutable result such as an audio chunk, transcript segment,
translated segment, WebVTT file, or later a dubbed audio track. Artifacts are
addressed by a cryptographic hash and described by a manifest.

At minimum, provenance should record:

- artifact type and format version;
- content hash and byte length;
- media identity and time range;
- source and target languages;
- parent artifact hashes;
- producing software and model, when known;
- creation time;
- author or node signature, when supplied; and
- whether the result is machine-generated or human-reviewed.

Corrections produce new artifacts. They do not silently mutate or erase the
history used by other nodes.

The first interchange format should be boring: canonical JSON manifests,
WebVTT captions, and hash-addressed files available over HTTP. A future
transport may use torrents, content-addressed networks, or direct peers without
requiring a new translation format.

### Jobs and execution

A job describes requested work; an artifact records completed work. These are
not the same object.

Redis is the coordination backbone inside a vidi18n node. It holds active domain
state, carries work between services, and supports transient progress
notifications. Workers consume small, idempotent steps:

1. ingest;
2. audio extraction;
3. speech segmentation;
4. transcription;
5. translation;
6. caption assembly; and
7. manifest publication.

Each step receives immutable inputs and creates immutable outputs. Re-running a
step should either return the existing artifact or create an explicitly
different version. This model prepares jobs for execution by other nodes later.

The original prototype uses Redis Pub/Sub to react to changes in domain
properties. That establishes useful service boundaries, but Pub/Sub alone is
not a durable work queue: a disconnected worker can miss a message, and there
is no acknowledgement or recovery of abandoned work.

The intended division of responsibility is:

| Concern | Redis mechanism |
| --- | --- |
| Current domain and job state | Redis keys, hashes, or JSON |
| Durable work delivery | Redis Streams and consumer groups |
| Transient progress for connected clients | Redis Pub/Sub |

Domain changes should produce explicit, versioned events such as
`video.ingest.requested` or `chunk.translation.requested`. Property decorators
may provide a convenient API for producing events, but Redis key names and
Python property names must not accidentally become permanent message schemas.

Work delivery is at least once. Every consumer must therefore be idempotent.
Messages contain identifiers, hashes, time ranges, and configuration—not video,
audio, or other large payloads. A worker acknowledges a stream entry only after
its output has been stored and the corresponding state transition is durable.

Updating state and appending its event must be atomic, using a Redis transaction,
Lua script, or an outbox drained by a dispatcher. Jobs expose an explicit
lifecycle and enough information to recover work:

```text
requested -> claimed -> running -> completed
                         |  |
                         |  +-> failed
                         +----> retryable
```

The precise Redis representation is internal to a node. It must not become the
protocol used for federation between independently operated nodes.

### Service boundaries

The pipeline is divided by capability rather than by individual model or file
operation:

- **manager:** owns the public API, desired state, and job/status views;
- **ingest:** obtains or accepts media and records its identity;
- **transcribe:** extracts speech and creates timed source-language segments;
- **translate:** creates target-language segments from source segments;
- **package:** assembles WebVTT, manifests, and later playable media tracks; and
- **artifact store:** persists large immutable inputs and outputs outside Redis.

The MVP may run one instance of each worker, or combine several worker
capabilities in one development process. Their stream contracts remain
separate, allowing an operator to scale a bottleneck horizontally without
redesigning the pipeline.

### Discovery

The MVP only searches its local artifact store. Federation can later add an
HTTPS query resembling:

```text
media identity + artifact kind + language + format
```

Responses should contain signed manifests or references to them. Caption files
are small enough that ordinary HTTP federation and mirroring may be sufficient;
P2P distribution becomes more valuable for models and derived audio/video.

### Trust

There may be several valid translations of the same segment. vidi18n should not
declare one global canonical translation.

Clients and nodes can instead choose using:

- configured trusted people, communities, or nodes;
- human-review status;
- compatible language and terminology preferences;
- model and software provenance;
- local reputation or moderation policy; and
- explicit user selection.

Signatures establish provenance, not truth. Reputation, moderation, and Sybil
resistance are federation concerns and are intentionally outside the MVP.

### Privacy

Every processing request must have an explicit visibility mode:

- **local:** do not advertise the media identity or artifacts;
- **community:** share only with configured peers; or
- **public:** permit public discovery and mirroring.

Local is the safe default. Processing a private file must never imply consent
to publish its fingerprint, transcript, title, source URL, or derived media.

## MVP deployment

The first node consists of:

- an HTTP API and lightweight web application;
- Redis for domain state, durable work streams, and progress events;
- a filesystem or S3-compatible artifact store;
- independently scalable ingest, transcription, translation, and packaging
  workers;
- FFmpeg for media operations;
- configurable transcription and translation adapters; and
- a rootless OCI container deployment using Podman.

The development deployment starts one instance of each required service.
Operators can later add worker instances for a particular stream without
changing the message or artifact formats. A shared worker image may select its
capability through configuration, keeping image maintenance simple while
preserving process boundaries.

## Evolution

1. **Single node:** complete and export the subtitle workflow.
2. **Federation:** discover and mirror signed manifests over HTTPS.
3. **Community execution:** allow trusted nodes to claim bounded jobs.
4. **Peer-assisted distribution:** distribute large artifacts and models.

Federation should precede P2P computation. It provides community ownership,
independent operation, and protocol feedback with substantially less scheduling
and abuse complexity.

## Security boundaries

Media is hostile input. A public node must defend against server-side request
forgery, decompression bombs, malformed codecs, excessive duration, disk
exhaustion, and command injection. Remote ingest should use an allowlist or an
isolated fetcher with strict limits in the MVP.

Rootless containers reduce impact but are not a complete security boundary.
Workers still need resource limits, timeouts, validated paths, non-secret
environments, and a controlled outbound network policy.

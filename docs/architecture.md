# Architecture

## Goal

vidi18n is an open translation layer for video. A deployment may initially run
as a single node, but its useful outputs must not belong to that node. Another
implementation should be able to identify compatible media, verify an artifact,
and use or mirror it without access to the producer's database.

The architecture therefore separates media identity, translation artifacts,
job execution, discovery, and trust.

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

The MVP can keep jobs in a local database or queue. Workers should consume
small, idempotent steps:

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

Redis may be useful as a local queue, but Redis keys and pub/sub messages are
implementation details and must not become the network protocol.

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
- a durable relational database for jobs and metadata;
- a filesystem or S3-compatible artifact store;
- one local worker process;
- FFmpeg for media operations;
- configurable transcription and translation adapters; and
- a rootless OCI container deployment using Podman.

A queue can be added when a single worker process becomes an actual bottleneck.
The MVP should avoid splitting each step into a separately deployed service:
that would increase operational complexity without proving community reuse.

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

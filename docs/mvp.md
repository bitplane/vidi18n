# MVP plan

## The hypothesis

The MVP should answer one question:

> Will people run or use an open node to create a subtitle translation once
> and reuse it when the same video is encountered again?

It does not need to prove distributed scheduling, synthetic speech, or a token
economy. It does need to demonstrate that community-created work is portable.

## User journey

1. A user uploads a video and selects its spoken and target languages.
2. The node calculates an exact media identifier and checks local artifacts.
3. If a compatible translation exists, captions are available immediately.
4. Otherwise, the node processes audio in chunks and reports progress.
5. Captions appear in the player as translated segments become available.
6. The user can download the WebVTT track and its manifest.
7. With explicit consent, the artifact can be shared with another node.

Remote URLs can follow once upload and local-file processing are reliable.

## Scope

### Required

- A small web UI and documented HTTP API
- Uploads with configurable size and duration limits
- Exact media hashing
- Audio extraction with FFmpeg
- Chunked transcription through one adapter
- Translation through one adapter
- Timestamp-preserving WebVTT generation
- Persistent jobs with visible progress and errors
- Resumable, idempotent processing
- An exportable, versioned artifact manifest
- Local/private operation by default
- Rootless Podman deployment
- Unit tests and one reproducible end-to-end fixture

### Explicitly deferred

- Voice synthesis, cloning, and lip sync
- OCR and translation of on-screen text
- Arbitrary-site downloading
- Browser extensions
- Cross-encode perceptual matching
- Public federation
- P2P scheduling or distribution
- Reputation, payments, and compute incentives
- Mobile applications

Deferring these features protects the part that matters: producing, playing,
exporting, and reusing a translated caption track.

## Proposed implementation shape

Use a modular monolith for the MVP:

```text
vidi18n node
├── API and web UI
├── job coordinator
├── media pipeline
│   ├── FFmpeg adapter
│   ├── transcription adapter
│   └── translation adapter
├── metadata database
└── content-addressed artifact directory
```

Start with one process for the API and one worker process. Keep adapter
interfaces independent of particular AI providers so a node can use local
models, hosted APIs, or community workers later.

SQLite is sufficient for a single-node MVP if jobs are claimed transactionally.
PostgreSQL can be supported when multi-host coordination is needed. Store large
artifacts outside the database.

## Milestones

### 0. Make the skeleton trustworthy

- Replace the prototype data model with explicit job and artifact models.
- Add configuration, structured logging, and error reporting.
- Establish a rootless Podman development environment.
- Add CI for formatting, types, unit tests, and the end-to-end fixture.

Exit condition: a new contributor can start the node and run its tests from the
documented commands.

### 1. Local transcription

- Upload a short media file.
- Extract audio and segment it.
- Generate a timestamped source-language WebVTT file.
- Display progress and play the result.

Exit condition: a clean installation reliably captions the fixture and a
representative hour-long input without losing or duplicating segment boundaries.

### 2. Translation

- Translate transcript segments while preserving timing.
- Record model and language provenance.
- Produce source and target WebVTT tracks.
- Permit retries without redoing successful chunks.

Exit condition: the translated track begins appearing before the complete video
has finished processing and can be selected in the player.

### 3. Portable reuse

- Define the versioned JSON manifest.
- Export and import manifests with hash verification.
- Return an existing artifact for an identical input.
- Add explicit local/community/public visibility metadata.

Exit condition: a second clean node can import an exported result, verify it,
and play the captions without running transcription or translation.

### 4. Federation experiment

- Implement read-only discovery between manually trusted nodes.
- Mirror small public artifacts over HTTPS.
- Measure false media matches, abuse cases, and moderation requirements.

This is the first post-MVP milestone.

## Measures of success

Collect measurements that influence architecture:

- time until the first translated caption appears;
- processing time divided by media duration;
- cost or energy per media hour;
- percentage of jobs resumed successfully after interruption;
- cache hit rate for previously processed media;
- subtitle timing and translation corrections per media minute; and
- bytes required to export or mirror caption artifacts.

The most important demonstration is not model quality in isolation. It is:

> Node B can safely reuse useful work created by Node A.

## Decisions to make during implementation

The following choices should be tested rather than embedded in the network
protocol prematurely:

- local transcription model versus hosted default;
- segment duration and overlap;
- source transcript representation beneath WebVTT;
- SQLite queue versus a dedicated broker;
- signature scheme and canonical JSON rules; and
- exact semantics of public artifact withdrawal and tombstones.

# vidi18n

**Community-owned translation for video anywhere.**

vidi18n aims to make video understandable across language barriers without
requiring a single video platform, translation provider, or network operator.
It is intended to be open source, self-hostable, and eventually able to share
work across federated or peer-to-peer community nodes.

The long-term experience is simple:

> Open a video. If the community has already translated it, use that work
> immediately. If not, produce the missing translation and optionally share it
> for the next viewer.

This repository is an early prototype with a runnable progressive-caption
vertical slice, not a production release.

## Why vidi18n?

Translation supplied by a video platform only works where that platform chooses
to provide it. vidi18n treats transcripts, subtitles, translations, and
eventually dubbed audio as portable artifacts which can be created and used
independently of the site hosting the video.

The project is guided by these principles:

- **Community ownership:** no central service is required to control the
  network or its translation corpus.
- **Local first:** a person can process private media without publishing its
  identity, transcript, or translations.
- **Portable results:** artifacts use documented formats and can be exported,
  mirrored, and served by different implementations.
- **Attribution and choice:** machine output, human corrections, and competing
  translations retain their provenance rather than being collapsed into one
  unexplained answer.
- **Progressive playback:** useful results should become available while a
  video is being processed.
- **Modular execution:** Redis-coordinated workers communicate through durable,
  versioned events and can scale independently by capability.
- **Incremental decentralisation:** the first useful implementation can run on
  one machine, without making any single node or network service part of the
  permanent protocol.

## MVP

The first milestone is deliberately subtitle-only:

1. Accept an uploaded video or an explicitly authorised remote source.
2. Identify it without depending solely on its URL.
3. Extract and chunk its audio.
4. Transcribe the chunks and translate them into one requested language.
5. Publish WebVTT captions and progress as chunks complete.
6. Play the video with the progressively generated caption track.
7. Export a hashed manifest and its artifacts for reuse by another node.

Voice cloning, dubbed audio, lip synchronisation, arbitrary website support,
federation, incentives, and P2P execution are not required for the MVP.

See the
[MVP plan](https://github.com/bitplane/vidi18n/blob/master/docs/mvp.md) and
[architecture](https://github.com/bitplane/vidi18n/blob/master/docs/architecture.md)
for the proposed path.

## Running the progressive slice

Rootless Podman is the preferred runtime. The default node uses deterministic
English-to-French processing adapters, allowing the complete pipeline to run
without downloading ML models:

```bash
make node
```

`podman compose` requires a Compose provider to be installed. The current
deployment should not be exposed as a production or secure community node.

Run the isolated end-to-end check with:

```bash
make test-integration
```

Real local `faster-whisper` and Argos Translate adapters are available through
the opt-in model bootstrap described in the development guide.

See
[development](https://github.com/bitplane/vidi18n/blob/master/docs/development.md)
for prerequisites, current limitations, and the intended developer workflow.

## Project status

The first URL-based English-to-French slice now resolves a playable source,
proxies HTTP range requests, extracts ten-second audio chunks, and sends them
through independent download, transcription, translation, and packaging
workers. Redis Streams provide durable work delivery. Translated cues are
replayable over SSE while processing continues, and an incrementally updated
WebVTT track becomes the final artifact.

The default adapters produce deterministic fixture text; they prove timing,
delivery, recovery, playback, and packaging rather than model quality. Uploads,
portable manifests, identity matching, hardening, observability, worker
recovery after a consumer dies, and community-node exchange remain MVP work.

Contributions are most useful when they advance the vertical MVP path rather
than adding more distributed-system machinery before that path works.

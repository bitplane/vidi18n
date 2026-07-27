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

This repository is currently an early prototype, not a working release.

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
- **Incremental decentralisation:** the first useful implementation can run on
  one machine, without making a central database part of the permanent design.

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

See the [MVP plan](../docs/mvp.md) and
[architecture](../docs/architecture.md) for the proposed path.

## Running the prototype

The checked-in application is incomplete and its container setup is being
migrated. Rootless Podman is the preferred runtime:

```bash
podman compose up --build
```

`podman compose` requires a Compose provider to be installed. The current
Compose file describes the historical prototype and should not yet be treated
as a production or secure community-node deployment.

See [development](../docs/development.md) for prerequisites, current
limitations, and the intended developer workflow.

## Project status

The repository contains an experimental FastAPI manager, Redis events, a
`yt-dlp` metadata worker, a basic DASH player, and media-processing experiments.
The end-to-end transcription and translation path has not yet been implemented.

Contributions are most useful when they advance the vertical MVP path rather
than adding more distributed-system machinery before that path works.

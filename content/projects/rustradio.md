# RustRadio

RustRadio is a desktop internet-radio player built in Rust with a Slint user interface and GStreamer playback.

The application discovers stations through the Radio Browser API, keeps a local station cache, downloads and caches station artwork, and provides station search, country-aware discovery, favorites, and playback controls.

## Features

- Browse popular internet-radio stations
- Search stations through the Radio Browser API
- Search the local station cache for fast repeated searches
- Prefer stations from the detected or manually selected country
- Save favorite stations locally
- Download and cache station artwork
- Play radio streams with GStreamer
- Pause, resume, stop, mute, and adjust playback volume
- Read artist and title metadata from compatible streams
- Navigate between stations with previous/next controls
- Desktop UI built with Slint

## Architecture

```text
src/
├── main.rs
├── player.rs
├── radio_browser.rs
├── cache.rs
└── state.rs

ui/
└── app.slint
```

### `src/main.rs`

Connects the UI to the application logic. It manages station loading, searching, selection, favorites, country selection, artwork preparation, and player state updates.

The UI-facing station model contains the station UUID, name, country, codec, bitrate, stream URL, artwork, and favorite state.

### `src/player.rs`

Provides the audio playback layer using GStreamer.

The player creates a `playbin3` pipeline for a station's resolved stream URL and handles:

- Playback
- Pause and resume
- Stop
- Volume
- Mute
- End-of-stream messages
- GStreamer errors and warnings
- Buffering notifications
- Artist/title stream metadata

The player also supports a bundled GStreamer runtime under:

```text
runtime/gstreamer/
```

when that directory exists beside the executable.

### `src/radio_browser.rs`

Contains the HTTP client and data model used to communicate with Radio Browser.

It supports:

- Popular stations
- General station search
- Country-specific station search
- Country station lists

Station data is deserialized with Serde.

### `src/cache.rs`

Maintains a local station cache and an in-memory search index.

The cache stores up to 1,000 stations and has a 24-hour freshness period for the main station list.

The cache also stores:

```text
%LOCALAPPDATA%/Radio/stations.json
```

and station artwork under:

```text
%LOCALAPPDATA%/Radio/artwork/
```

The search index normalizes station names, countries, tags, and codecs and scores matching results so the strongest matches are returned first.

Country selection is also cached. A manually selected country takes priority over automatic country detection, while automatically detected country information is refreshed on a longer interval.

### `src/state.rs`

Stores the user's favorite stations.

Favorites are serialized to:

```text
%LOCALAPPDATA%/Radio/favorites.json
```

The state layer supports checking whether a station is a favorite, toggling favorites, and retrieving the current favorite list.

### `ui/app.slint`

Defines the desktop UI with Slint.

The UI contains the sidebar, home/favorites navigation, search field, country selector, station cards, artwork, favorite controls, play controls, and the bottom playback area.

## Data sources

Station information comes from the Radio Browser API:

```text
https://de1.api.radio-browser.info
```

Country detection uses:

```text
https://ipapi.co/country/
```

Station artwork is retrieved from the artwork URL supplied by the station data when available.

Because RustRadio contacts external services, availability and returned station data depend on those services.

## Dependencies

The project uses:

- Rust 2024 edition
- Slint 1.17.1 for the UI
- GStreamer 0.24 for audio playback
- Reqwest 0.13.4 for HTTP
- Serde and Serde JSON for data serialization
- Image 0.25.10 for JPEG, PNG, and WebP artwork decoding

See `Cargo.toml` for the authoritative dependency versions.

## Building

Clone the repository and build it with Cargo:

```bash
git clone https://github.com/Cooper-Src/RustRadio
cd RustRadio
cargo build --release
```

Run the application with:

```bash
cargo run --release
```

GStreamer must be available to the application at runtime. The player code can also use a bundled runtime at:

```text
runtime/gstreamer/
```

when one is packaged with the executable.

## Configuration and local data

RustRadio currently stores its persistent application data under:

```text
%LOCALAPPDATA%/Radio/
```

The directory can contain:

```text
stations.json
favorites.json
country.txt
country_manual.txt
artwork/
```

These files are created as needed.

## Project structure

```text
RustRadio/
├── Cargo.toml
├── build.rs
├── src/
│   ├── cache.rs
│   ├── main.rs
│   ├── player.rs
│   ├── radio_browser.rs
│   └── state.rs
├── ui/
│   └── app.slint
└── assets/
    └── icons/
        ├── chevron-left.svg
        ├── chevron-right.svg
        ├── compass.svg
        ├── globe.svg
        ├── heart.svg
        ├── home.svg
        ├── pause.svg
        ├── play.svg
        ├── radio.svg
        ├── search.svg
        ├── stop.svg
        ├── volume-low.svg
        ├── volume-mute.svg
        └── volume.svg
```

## License

A license is not specified by the current repository files. Add a license here once one has been chosen for the project.
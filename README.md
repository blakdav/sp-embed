# sp-embed

A lightweight, self-hosted dashboard embed for [Super Productivity](https://github.com/johannesjo/super-productivity). Reads your SP sync data from WebDAV and renders a clean, iframe-friendly task list for use with [Homepage](https://gethomepage.dev) or any other dashboard.

## How it works

Super Productivity syncs its data to a WebDAV server as a JSON file (`sync-data.json`). This container mounts that file read-only and serves a dark-themed HTML task list, split into three sections:

- **Today & Overdue** — tasks with a due date of today or earlier
- **Upcoming** — tasks with a future due date
- **No Due Date** — everything else

The page auto-refreshes every 60 seconds.

## Requirements

- Super Productivity running and syncing to a WebDAV server
- The WebDAV data directory accessible on the host

## Setup

### 1. Pull the image

```bash
docker pull blakdav/sp-embed:latest
```

### 2. Run the container

```bash
docker run -d \
  --name sp-embed \
  -p 8087:8080 \
  -v /path/to/webdav/data:/sp-data:ro \
  blakdav/sp-embed:latest
```

Replace `/path/to/webdav/data` with the host path where your WebDAV server stores its files (the directory containing `sync-data.json`).

### 3. Add to Homepage

In your Homepage `services.yaml`:

```yaml
- Super Productivity:
    widget:
      type: iframe
      src: http://YOUR_SERVER_IP:8087
      height: 500
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SP_DATA_PATH` | `/sp-data/sync-data.json` | Path to the SP sync data file inside the container |

## Notes

- Tasks sync on SP's configured interval (default 5 minutes). Hit **Sync Now** in SP to force an immediate sync.
- Compression must be **disabled** in SP's sync settings. In SP: Settings → Sync → Advanced → disable compression.
- Subtasks and completed tasks are not shown.

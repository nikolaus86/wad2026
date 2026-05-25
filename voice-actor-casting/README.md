# Voice Actor Casting Service

Fullstack prototype for a voice actor casting service.

## What is included

- React + Vite frontend
- Express backend
- Voice actor catalog
- Search and filters
- Actor profile modal
- Real audio demo playback from `.wav` files
- Shortlist of candidates
- Browser microphone recording for client voice references
- Casting request form
- Audio upload storage
- JSON file storage for actors and requests

## Project structure

```text
voice-actor-casting/
  src/                     React frontend
  server/
    index.js               Express backend
    data/
      actors.json          Actor database
      requests.json        Saved casting requests
    demos/                 Actor demo audio files
    uploads/               Client voice recordings
```

## Run the project

```bash
npm install
npm run dev:full
```

Frontend:

```text
http://localhost:5173
```

Backend:

```text
http://localhost:4000
```

## API

### Actors

```text
GET /api/actors
GET /api/actors/:id
```

Query filters:

```text
/api/actors?search=warm&language=English&gender=Female&tags=Warm,Narration
```

### Upload demo audio for an actor

```text
POST /api/actors/:id/demos
```

Form data:

```text
demoAudio = audio file, mp3/wav/webm
title = Demo title
tone = Demo tone
duration = 0:12
```

Example:

```bash
curl -X POST http://localhost:4000/api/actors/1/demos \
  -F "demoAudio=@./my-demo.wav" \
  -F "title=Real Commercial Demo" \
  -F "tone=Warm and confident" \
  -F "duration=0:14"
```

The uploaded file will be saved in:

```text
server/demos/
```

The actor profile in `server/data/actors.json` will be updated automatically.

### Casting requests

```text
POST /api/requests
GET /api/requests
```

Form data:

```text
clientName
project
message
actorIds = [1,2,3]
voiceNote = browser recorded audio file
```

Client recordings are saved in:

```text
server/uploads/
```

## Audio demos

The project now plays real audio files from the backend instead of generating fake sound in the browser.

Current demo files are located here:

```text
server/demos/
```

You can replace them with real human voice actor recordings. Just keep the paths in `server/data/actors.json`, or upload new demos through `POST /api/actors/:id/demos`.


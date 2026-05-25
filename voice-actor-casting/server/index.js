import cors from 'cors';
import crypto from 'crypto';
import express from 'express';
import fs from 'fs/promises';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');
const dataDir = path.join(__dirname, 'data');
const uploadsDir = path.join(__dirname, 'uploads');
const demosDir = path.join(__dirname, 'demos');
const actorsFile = path.join(dataDir, 'actors.json');
const requestsFile = path.join(dataDir, 'requests.json');
const distDir = path.join(rootDir, 'dist');
const port = process.env.PORT || 4000;

await fs.mkdir(dataDir, { recursive: true });
await fs.mkdir(uploadsDir, { recursive: true });
await fs.mkdir(demosDir, { recursive: true });

async function readJson(filePath, fallback) {
  try {
    const data = await fs.readFile(filePath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    return fallback;
  }
}

async function writeJson(filePath, data) {
  await fs.writeFile(filePath, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
}

function getActorSearchText(actor) {
  return [
    actor.name,
    actor.role,
    actor.gender,
    actor.language,
    actor.accent,
    actor.location,
    actor.rate,
    actor.availability,
    actor.ageRange,
    actor.bio,
    ...(actor.tags || []),
    ...(actor.demos || []).map((demo) => `${demo.title} ${demo.tone}`),
  ]
    .join(' ')
    .toLowerCase();
}

function parseActorIds(value) {
  if (!value) return [];

  try {
    const parsed = JSON.parse(value);
    if (Array.isArray(parsed)) return parsed.map(Number).filter(Boolean);
  } catch (error) {
    return String(value)
      .split(',')
      .map((item) => Number(item.trim()))
      .filter(Boolean);
  }

  return [];
}

function getMeta(actors) {
  return {
    total: actors.length,
    languages: [...new Set(actors.map((actor) => actor.language))].sort(),
    genders: [...new Set(actors.map((actor) => actor.gender))].sort(),
    tags: [...new Set(actors.flatMap((actor) => actor.tags || []))].sort(),
  };
}

function createAudioUpload(destination) {
  const storage = multer.diskStorage({
    destination,
    filename: (req, file, callback) => {
      const ext = path.extname(file.originalname) || '.webm';
      const safeName = `${Date.now()}-${crypto.randomUUID()}${ext}`;
      callback(null, safeName);
    },
  });

  return multer({
    storage,
    limits: {
      fileSize: 25 * 1024 * 1024,
    },
    fileFilter: (req, file, callback) => {
      const isAudio = file.mimetype.startsWith('audio/') || file.mimetype === 'video/webm' || file.originalname.endsWith('.webm') || file.originalname.endsWith('.wav') || file.originalname.endsWith('.mp3');
      if (!isAudio) return callback(new Error('Only audio files are allowed.'));
      callback(null, true);
    },
  });
}

const requestUpload = createAudioUpload(uploadsDir);
const demoUpload = createAudioUpload(demosDir);

const app = express();

app.use(cors({ origin: true }));
app.use(express.json());
app.use('/uploads', express.static(uploadsDir));
app.use('/demos', express.static(demosDir));

app.get('/api/health', (req, res) => {
  res.json({ ok: true, service: 'voice-actor-casting-api' });
});

app.get('/api/actors', async (req, res) => {
  const actors = await readJson(actorsFile, []);
  const search = String(req.query.search || '').trim().toLowerCase();
  const language = String(req.query.language || 'All');
  const gender = String(req.query.gender || 'All');
  const tags = String(req.query.tags || '')
    .split(',')
    .map((tag) => tag.trim())
    .filter(Boolean);

  const filtered = actors.filter((actor) => {
    const matchesSearch = !search || getActorSearchText(actor).includes(search);
    const matchesLanguage = language === 'All' || actor.language === language;
    const matchesGender = gender === 'All' || actor.gender === gender;
    const matchesTags = tags.length === 0 || tags.every((tag) => actor.tags.includes(tag));

    return matchesSearch && matchesLanguage && matchesGender && matchesTags;
  });

  res.json({ data: filtered, meta: getMeta(actors), count: filtered.length });
});

app.get('/api/actors/:id', async (req, res) => {
  const actors = await readJson(actorsFile, []);
  const actor = actors.find((item) => item.id === Number(req.params.id));

  if (!actor) {
    return res.status(404).json({ error: 'Actor not found.' });
  }

  res.json({ data: actor });
});

app.get('/api/requests', async (req, res) => {
  const requests = await readJson(requestsFile, []);
  res.json({ data: requests });
});

app.post('/api/actors/:id/demos', demoUpload.single('demoAudio'), async (req, res) => {
  const actors = await readJson(actorsFile, []);
  const actor = actors.find((item) => item.id === Number(req.params.id));

  if (!actor) {
    return res.status(404).json({ error: 'Actor not found.' });
  }

  if (!req.file) {
    return res.status(400).json({ error: 'Upload an audio demo file.' });
  }

  const demo = {
    title: String(req.body.title || req.file.originalname || 'Voice demo').trim(),
    tone: String(req.body.tone || 'Custom uploaded demo').trim(),
    duration: String(req.body.duration || 'audio').trim(),
    url: `/demos/${req.file.filename}`,
    kind: 'uploaded-audio-file',
    originalName: req.file.originalname,
    createdAt: new Date().toISOString(),
  };

  actor.demos = [...(actor.demos || []), demo];
  await writeJson(actorsFile, actors);

  res.status(201).json({ data: demo });
});

app.post('/api/requests', requestUpload.single('voiceNote'), async (req, res) => {
  const actors = await readJson(actorsFile, []);
  const requests = await readJson(requestsFile, []);
  const actorIds = parseActorIds(req.body.actorIds);

  if (actorIds.length === 0) {
    return res.status(400).json({ error: 'Select at least one actor.' });
  }

  const selectedActors = actors
    .filter((actor) => actorIds.includes(actor.id))
    .map((actor) => ({ id: actor.id, name: actor.name, role: actor.role, language: actor.language }));

  if (selectedActors.length === 0) {
    return res.status(400).json({ error: 'Selected actors were not found.' });
  }

  const request = {
    id: crypto.randomUUID(),
    status: 'new',
    clientName: String(req.body.clientName || '').trim(),
    project: String(req.body.project || '').trim(),
    message: String(req.body.message || '').trim(),
    actorIds,
    actors: selectedActors,
    voiceNote: req.file
      ? {
          filename: req.file.filename,
          originalName: req.file.originalname,
          mimeType: req.file.mimetype,
          size: req.file.size,
          url: `/uploads/${req.file.filename}`,
        }
      : null,
    createdAt: new Date().toISOString(),
  };

  requests.unshift(request);
  await writeJson(requestsFile, requests);

  res.status(201).json({ data: request });
});

app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    return res.status(400).json({ error: error.message });
  }

  if (error) {
    return res.status(400).json({ error: error.message || 'Request failed.' });
  }

  next();
});

try {
  await fs.access(distDir);
  app.use(express.static(distDir));
  app.use((req, res, next) => {
    if (req.method === 'GET' && !req.path.startsWith('/api')) {
      return res.sendFile(path.join(distDir, 'index.html'));
    }
    next();
  });
} catch (error) {
  // The frontend build folder does not exist during local development.
}

app.listen(port, () => {
  console.log(`Voice Actor Casting API is running on http://localhost:${port}`);
});

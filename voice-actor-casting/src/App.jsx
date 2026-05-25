import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Search,
  Filter,
  Play,
  Pause,
  Star,
  StarOff,
  X,
  Mic,
  Square,
  Send,
  Headphones,
  MapPin,
  Clock,
  Languages,
  Volume2,
  UserRound,
  CheckCircle2,
} from 'lucide-react';
import { apiUrl, getJson, postForm } from './api.js';

function DemoButton({ actor, demo, activeDemo, onPlay }) {
  const key = `${actor.id}-${demo.title}`;
  const isActive = activeDemo === key;

  return (
    <button className="demo-button" onClick={() => onPlay(key, demo)}>
      <span className="demo-icon">{isActive ? <Pause size={16} /> : <Play size={16} />}</span>
      <span className="demo-info">
        <b>{demo.title}</b>
        <small>{demo.tone} · {demo.duration}</small>
      </span>
      <span className="sound-bars" aria-hidden="true">
        {[16, 26, 18, 34, 22, 30].map((height, index) => (
          <i key={index} style={{ height }} className={isActive ? 'active' : ''} />
        ))}
      </span>
    </button>
  );
}

function ActorCard({ actor, shortlist, onShortlist, onOpen, activeDemo, onPlay }) {
  const isSelected = shortlist.some((item) => item.id === actor.id);

  return (
    <motion.article layout initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95 }} className="actor-card">
      <div className="actor-top">
        <button className="actor-main" onClick={() => onOpen(actor)}>
          <span className="avatar">{actor.initials}</span>
          <span>
            <h3>{actor.name}</h3>
            <p>{actor.role}</p>
          </span>
        </button>

        <button className={isSelected ? 'shortlist active' : 'shortlist'} onClick={() => onShortlist(actor)}>
          {isSelected ? <Star size={18} /> : <StarOff size={18} />}
        </button>
      </div>

      <div className="meta-grid">
        <span><Languages size={15} /> {actor.language}</span>
        <span><Clock size={15} /> {actor.availability}</span>
      </div>

      <div className="tag-list">
        {actor.tags.slice(0, 4).map((tag) => <span key={tag}>{tag}</span>)}
      </div>

      {actor.demos?.[0] && <DemoButton actor={actor} demo={actor.demos[0]} activeDemo={activeDemo} onPlay={onPlay} />}

      <button className="open-profile" onClick={() => onOpen(actor)}>Open full profile</button>
    </motion.article>
  );
}

function Filters({ search, setSearch, language, setLanguage, gender, setGender, selectedTags, setSelectedTags, clearFilters, languages, tags }) {
  const toggleTag = (tag) => {
    setSelectedTags((current) => current.includes(tag) ? current.filter((item) => item !== tag) : [...current, tag]);
  };

  return (
    <aside className="filters">
      <div className="filters-title">
        <h2><Filter size={18} /> Filters</h2>
        <button onClick={clearFilters}>Clear</button>
      </div>

      <label className="field-label">Search</label>
      <div className="search-box small">
        <Search size={18} />
        <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Name, tag, accent..." />
      </div>

      <label className="field-label">Language</label>
      <select value={language} onChange={(event) => setLanguage(event.target.value)}>
        <option value="All">All languages</option>
        {languages.map((item) => <option key={item} value={item}>{item}</option>)}
      </select>

      <label className="field-label">Gender</label>
      <div className="switch-row">
        {['All', 'Female', 'Male'].map((item) => (
          <button key={item} className={gender === item ? 'active' : ''} onClick={() => setGender(item)}>{item}</button>
        ))}
      </div>

      <label className="field-label">Voice tags</label>
      <div className="tag-filter">
        {tags.map((tag) => (
          <button key={tag} className={selectedTags.includes(tag) ? 'active' : ''} onClick={() => toggleTag(tag)}>{tag}</button>
        ))}
      </div>
    </aside>
  );
}

function ProfileModal({ actor, onClose, shortlist, onShortlist, activeDemo, onPlay }) {
  if (!actor) return null;

  const isSelected = shortlist.some((item) => item.id === actor.id);

  return (
    <AnimatePresence>
      <motion.div className="modal-backdrop" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={onClose}>
        <motion.div className="modal" initial={{ opacity: 0, y: 24, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 24, scale: 0.98 }} onClick={(event) => event.stopPropagation()}>
          <div className="modal-head">
            <div className="avatar big">{actor.initials}</div>
            <div>
              <h2>{actor.name}</h2>
              <p>{actor.role}</p>
              <div className="modal-pills">
                <span><MapPin size={14} /> {actor.location}</span>
                <span><UserRound size={14} /> {actor.ageRange}</span>
              </div>
            </div>
            <button className="close" onClick={onClose}><X size={20} /></button>
          </div>

          <div className="modal-body">
            <div>
              <h4>Profile</h4>
              <p className="bio">{actor.bio}</p>

              <h4>Demos</h4>
              <div className="demo-list">
                {actor.demos?.map((demo) => <DemoButton key={demo.title} actor={actor} demo={demo} activeDemo={activeDemo} onPlay={onPlay} />)}
              </div>

              <h4>Voice tags</h4>
              <div className="tag-list large">
                {actor.tags?.map((tag) => <span key={tag}>{tag}</span>)}
              </div>
            </div>

            <div className="details-box">
              <p><small>Language</small><b>{actor.language}</b></p>
              <p><small>Accent</small><b>{actor.accent}</b></p>
              <p><small>Rate</small><b>{actor.rate}</b></p>
              <p><small>Availability</small><b>{actor.availability}</b></p>
              <button className="primary-btn" onClick={() => onShortlist(actor)}>
                {isSelected ? 'Remove from shortlist' : 'Add to shortlist'}
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}

function RequestPanel({ shortlist, removeActor }) {
  const [client, setClient] = useState('');
  const [project, setProject] = useState('');
  const [message, setMessage] = useState('');
  const [recording, setRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioBlob, setAudioBlob] = useState(null);
  const [sent, setSent] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const recorderRef = useRef(null);
  const chunksRef = useRef([]);

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      recorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach((track) => track.stop());
      };

      recorder.start();
      setRecording(true);
      setError('');
    } catch (error) {
      setError('Microphone access is blocked or unavailable.');
    }
  }

  function stopRecording() {
    if (recorderRef.current) {
      recorderRef.current.stop();
      setRecording(false);
    }
  }

  async function submitRequest(event) {
    event.preventDefault();
    setError('');
    setSent('');
    setSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('clientName', client);
      formData.append('project', project);
      formData.append('message', message);
      formData.append('actorIds', JSON.stringify(shortlist.map((actor) => actor.id)));

      if (audioBlob) {
        formData.append('voiceNote', audioBlob, 'voice-reference.webm');
      }

      const response = await postForm('/api/requests', formData);
      setSent(`Request submitted. ID: ${response.data.id.slice(0, 8)}`);
    } catch (error) {
      setError(error.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <aside className="request-panel">
      <h2>Shortlist request</h2>
      <p className="muted">Choose actors and send a voice reference from the browser.</p>

      <div className="selected-list">
        {shortlist.length === 0 ? (
          <div className="empty">No actors selected yet.</div>
        ) : shortlist.map((actor) => (
          <div key={actor.id} className="selected-actor">
            <div>
              <b>{actor.name}</b>
              <small>{actor.role}</small>
            </div>
            <button onClick={() => removeActor(actor.id)}><X size={15} /></button>
          </div>
        ))}
      </div>

      <form onSubmit={submitRequest}>
        <input value={client} onChange={(event) => setClient(event.target.value)} placeholder="Client name" />
        <input value={project} onChange={(event) => setProject(event.target.value)} placeholder="Project title" />
        <textarea value={message} onChange={(event) => setMessage(event.target.value)} placeholder="Describe the required voice..." rows="4" />

        <div className="record-box">
          <div className="record-title"><Volume2 size={16} /> Voice recording</div>
          {!recording ? (
            <button type="button" className="record-btn" onClick={startRecording}><Mic size={16} /> Record</button>
          ) : (
            <button type="button" className="stop-btn" onClick={stopRecording}><Square size={16} /> Stop</button>
          )}
          {audioUrl && <audio controls src={audioUrl} />}
        </div>

        <button className="submit-btn" disabled={shortlist.length === 0 || submitting}>
          <Send size={16} /> {submitting ? 'Sending...' : 'Submit request'}
        </button>
      </form>

      {sent && <div className="success">{sent}</div>}
      {error && <div className="success error-box">{error}</div>}
    </aside>
  );
}

export default function App() {
  const [search, setSearch] = useState('');
  const [language, setLanguage] = useState('All');
  const [gender, setGender] = useState('All');
  const [selectedTags, setSelectedTags] = useState([]);
  const [shortlist, setShortlist] = useState([]);
  const [selectedActor, setSelectedActor] = useState(null);
  const [activeDemo, setActiveDemo] = useState(null);
  const [actors, setActors] = useState([]);
  const [meta, setMeta] = useState({ languages: [], tags: [], total: 0 });
  const [loading, setLoading] = useState(true);
  const [apiError, setApiError] = useState('');
  const audioRef = useRef(null);

  useEffect(() => {
    const controller = new AbortController();

    async function loadActors() {
      setLoading(true);
      setApiError('');

      try {
        const params = new URLSearchParams();
        if (search.trim()) params.set('search', search.trim());
        if (language !== 'All') params.set('language', language);
        if (gender !== 'All') params.set('gender', gender);
        if (selectedTags.length > 0) params.set('tags', selectedTags.join(','));

        const query = params.toString() ? `?${params.toString()}` : '';
        const response = await getJson(`/api/actors${query}`);

        if (!controller.signal.aborted) {
          setActors(response.data);
          setMeta(response.meta);
        }
      } catch (error) {
        if (!controller.signal.aborted) setApiError(error.message);
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }

    loadActors();
    return () => controller.abort();
  }, [search, language, gender, selectedTags]);

  async function openActor(actor) {
    setSelectedActor(actor);

    try {
      const response = await getJson(`/api/actors/${actor.id}`);
      setSelectedActor(response.data);
    } catch (error) {
      setSelectedActor(actor);
    }
  }

  function stopCurrentDemo() {
    if (!audioRef.current) return;

    if (audioRef.current.type === 'html-audio') {
      audioRef.current.audio.pause();
      audioRef.current.audio.currentTime = 0;
    }

    if (audioRef.current.type === 'oscillator') {
      audioRef.current.oscillator.stop();
      audioRef.current.context.close();
    }

    audioRef.current = null;
  }

  function playDemo(key, demo) {
    stopCurrentDemo();

    if (activeDemo === key) {
      setActiveDemo(null);
      return;
    }

    if (demo?.url) {
      const audio = new Audio(apiUrl(demo.url));
      audioRef.current = { type: 'html-audio', audio };
      setActiveDemo(key);

      audio.onended = () => {
        audioRef.current = null;
        setActiveDemo(null);
      };

      audio.onerror = () => {
        audioRef.current = null;
        setActiveDemo(null);
      };

      audio.play().catch(() => {
        audioRef.current = null;
        setActiveDemo(null);
      });
      return;
    }

    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (!AudioContext) return;

    const frequency = demo?.freq || 360;
    const context = new AudioContext();
    const oscillator = context.createOscillator();
    const gain = context.createGain();

    oscillator.type = 'sine';
    oscillator.frequency.setValueAtTime(frequency, context.currentTime);
    oscillator.frequency.exponentialRampToValueAtTime(frequency * 1.25, context.currentTime + 0.6);

    gain.gain.setValueAtTime(0.001, context.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.13, context.currentTime + 0.08);
    gain.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 1.4);

    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start();
    oscillator.stop(context.currentTime + 1.5);

    audioRef.current = { type: 'oscillator', context, oscillator };
    setActiveDemo(key);

    oscillator.onended = () => {
      context.close();
      audioRef.current = null;
      setActiveDemo(null);
    };
  }

  function toggleShortlist(actor) {
    setShortlist((current) => current.some((item) => item.id === actor.id)
      ? current.filter((item) => item.id !== actor.id)
      : [...current, actor]
    );
  }

  function clearFilters() {
    setSearch('');
    setLanguage('All');
    setGender('All');
    setSelectedTags([]);
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon"><Headphones size={22} /></div>
          <div>
            <span>VOICECAST</span>
            <b>Voice Actor Casting Service</b>
          </div>
        </div>
        <a href="#request" className="header-link">Create request</a>
      </header>

      <section className="hero">
        <div className="hero-glow one" />
        <div className="hero-glow two" />
        <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55 }} className="hero-content">
          <div className="status-pill"><CheckCircle2 size={16} /> Frontend + Express backend</div>
          <h1>Find the right voice for your project.</h1>
          <p>Browse voice actors, listen to demos, filter by tone and language, then send a shortlist with a recorded voice reference.</p>
          <div className="search-box hero-search">
            <Search size={22} />
            <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search by actor, tone, language, accent..." />
          </div>
        </motion.div>
      </section>

      <main className="layout">
        <Filters
          search={search}
          setSearch={setSearch}
          language={language}
          setLanguage={setLanguage}
          gender={gender}
          setGender={setGender}
          selectedTags={selectedTags}
          setSelectedTags={setSelectedTags}
          clearFilters={clearFilters}
          languages={meta.languages || []}
          tags={meta.tags || []}
        />

        <section className="catalog">
          <div className="catalog-head">
            <div>
              <h2>Voice actors</h2>
              <p>{loading ? 'Loading candidates...' : `${actors.length} candidates found`}</p>
            </div>
          </div>

          {apiError && <div className="success error-box">Backend error: {apiError}</div>}

          <AnimatePresence mode="popLayout">
            {loading ? (
              <motion.div className="not-found" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <Headphones size={38} />
                <h3>Loading actors...</h3>
                <p>Data is coming from the Express API.</p>
              </motion.div>
            ) : actors.length > 0 ? (
              <div className="cards-grid">
                {actors.map((actor) => (
                  <ActorCard
                    key={actor.id}
                    actor={actor}
                    shortlist={shortlist}
                    onShortlist={toggleShortlist}
                    onOpen={openActor}
                    activeDemo={activeDemo}
                    onPlay={playDemo}
                  />
                ))}
              </div>
            ) : (
              <motion.div className="not-found" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <Search size={38} />
                <h3>No actors found</h3>
                <p>Try changing search or filters.</p>
              </motion.div>
            )}
          </AnimatePresence>
        </section>

        <div id="request">
          <RequestPanel shortlist={shortlist} removeActor={(id) => setShortlist((current) => current.filter((actor) => actor.id !== id))} />
        </div>
      </main>

      <ProfileModal
        actor={selectedActor}
        onClose={() => setSelectedActor(null)}
        shortlist={shortlist}
        onShortlist={toggleShortlist}
        activeDemo={activeDemo}
        onPlay={playDemo}
      />
    </div>
  );
}

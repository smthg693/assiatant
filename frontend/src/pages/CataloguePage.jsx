import React, { useState, useEffect } from 'react';
import { Search, Filter, CheckCircle2, ChevronRight, BookOpen, Code2 } from 'lucide-react';
import { api } from '../lib/api';

export default function CataloguePage({ onSelectChallenge, token }) {
  const [challenges, setChallenges] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [difficulty, setDifficulty] = useState('all');
  const [selectedConcept, setSelectedConcept] = useState('all');

  useEffect(() => {
    async function loadChallenges() {
      setLoading(true);
      setError(null);
      try {
        const params = {};
        if (difficulty !== 'all') params.difficulty = difficulty;
        if (selectedConcept !== 'all') params.concept = selectedConcept;
        if (search.trim()) params.search = search.trim();
        const data = await api.getChallenges(params, token);
        setChallenges(data.challenges || []);
      } catch (err) {
        setError('Failed to load challenges from backend. Ensure the backend API is running on port 8000.');
      } finally {
        setLoading(false);
      }
    }
    loadChallenges();
  }, [difficulty, selectedConcept, search, token]);

  const allConcepts = ['lists', 'slicing', 'strings', 'iteration', 'math', 'recursion', 'edge-cases', 'dictionaries'];

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: '28px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '6px' }}>
          Challenge Catalogue
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          Master Python algorithms through sandboxed test suites and progressive coaching.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '12px',
          alignItems: 'center',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-color)',
          borderRadius: '8px',
          padding: '12px',
          marginBottom: '24px',
        }}
      >
        {/* Search */}
        <div style={{ position: 'relative', flex: '1 1 240px' }}>
          <Search size={16} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--text-muted)' }} />
          <input
            type="text"
            className="dojo-input"
            style={{ width: '100%', paddingLeft: '32px' }}
            placeholder="Search challenges by title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        {/* Difficulty Filter */}
        <div style={{ display: 'flex', gap: '6px' }}>
          {['all', 'easy', 'medium', 'hard'].map((d) => (
            <button
              key={d}
              className="btn-ghost"
              onClick={() => setDifficulty(d)}
              style={{
                textTransform: 'capitalize',
                fontSize: '12px',
                padding: '6px 12px',
                borderRadius: '6px',
                background: difficulty === d ? 'var(--bg-tertiary)' : 'transparent',
                color: difficulty === d ? 'var(--text-primary)' : 'var(--text-muted)',
                border: difficulty === d ? '1px solid var(--border-color)' : '1px solid transparent',
              }}
            >
              {d}
            </button>
          ))}
        </div>

        {/* Concept Dropdown */}
        <select
          className="dojo-input"
          style={{ fontSize: '12px', padding: '6px 10px' }}
          value={selectedConcept}
          onChange={(e) => setSelectedConcept(e.target.value)}
        >
          <option value="all">All Concepts</option>
          {allConcepts.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Challenge Grid */}
      {loading ? (
        <div style={{ padding: '60px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
          Loading challenges from API...
        </div>
      ) : error ? (
        <div
          style={{
            padding: '24px',
            borderRadius: '8px',
            background: 'rgba(244, 63, 94, 0.1)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            color: 'var(--accent-rose)',
            fontSize: '14px',
          }}
        >
          {error}
        </div>
      ) : challenges.length === 0 ? (
        <div style={{ padding: '60px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
          No challenges matched your filters.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '16px' }}>
          {challenges.map((c) => (
            <div
              key={c.id || c.slug}
              className="dojo-card"
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                cursor: 'pointer',
              }}
              onClick={() => onSelectChallenge(c.slug)}
            >
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 600 }}>{c.title}</h3>
                  <span className={`badge badge-${c.difficulty}`}>{c.difficulty}</span>
                </div>

                <p
                  style={{
                    fontSize: '13px',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.5,
                    marginBottom: '14px',
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                  }}
                >
                  {c.description.replace(/```[\s\S]*?```/g, '').replace(/[\*#_`]/g, '')}
                </p>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '14px' }}>
                  {c.concepts.map((concept, idx) => (
                    <span key={idx} className="badge-tag">
                      {concept}
                    </span>
                  ))}
                </div>
              </div>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  paddingTop: '12px',
                  borderTop: '1px solid var(--border-color)',
                  fontSize: '12px',
                  color: 'var(--text-muted)',
                }}
              >
                <div>
                  {c.visible_test_count} visible · {c.hidden_test_count} hidden tests
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--accent-blue)', fontWeight: 600 }}>
                  Solve <ChevronRight size={14} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

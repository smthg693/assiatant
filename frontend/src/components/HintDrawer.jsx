import React from 'react';
import { Lightbulb, Sparkles, ChevronRight, ShieldAlert, Clock } from 'lucide-react';

export default function HintDrawer({ hints, onGetHint, loading, canRequestHint }) {
  const levelNames = {
    1: 'Level 1: Conceptual Nudge',
    2: 'Level 2: Debugging Direction',
    3: 'Level 3: Specific Guidance',
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        backgroundColor: 'var(--bg-secondary)',
        borderLeft: '1px solid var(--border-color)',
        padding: '16px',
        overflowY: 'auto',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Lightbulb size={20} color="var(--accent-amber)" />
          <h3 style={{ fontSize: '16px', fontWeight: 600 }}>Progressive Hint Ladder</h3>
        </div>
        <span
          style={{
            fontSize: '11px',
            background: 'rgba(245, 158, 11, 0.15)',
            color: 'var(--accent-amber)',
            padding: '2px 8px',
            borderRadius: '9999px',
            fontWeight: 600,
          }}
        >
          {hints.length} Unlocked
        </span>
      </div>

      <div
        style={{
          background: 'rgba(59, 130, 246, 0.08)',
          border: '1px solid rgba(59, 130, 246, 0.2)',
          borderRadius: '8px',
          padding: '10px 12px',
          fontSize: '12px',
          color: 'var(--text-secondary)',
          display: 'flex',
          gap: '8px',
          marginBottom: '16px',
        }}
      >
        <Sparkles size={16} color="var(--accent-blue)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <span>
          Hints are designed to train your debugging intuition. We never reveal copy-paste solutions!
        </span>
      </div>

      {/* Hints List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1, marginBottom: '16px' }}>
        {hints.length === 0 ? (
          <div
            style={{
              padding: '28px 16px',
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '13px',
              background: 'var(--bg-card)',
              borderRadius: '8px',
              border: '1px dashed var(--border-color)',
            }}
          >
            <Lightbulb size={28} style={{ opacity: 0.3, marginBottom: '8px' }} />
            <div>No hints requested yet.</div>
            <div style={{ fontSize: '11px', marginTop: '4px' }}>
              Run your code first, then request a hint if you get stuck!
            </div>
          </div>
        ) : (
          hints.map((h, idx) => (
            <div
              key={idx}
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '12px',
                boxShadow: 'var(--shadow-sm)',
              }}
            >
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '6px',
                }}
              >
                <span
                  style={{
                    fontSize: '11px',
                    fontWeight: 700,
                    color: h.level === 1 ? 'var(--accent-emerald)' : h.level === 2 ? 'var(--accent-amber)' : 'var(--accent-purple)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.5px',
                  }}
                >
                  {levelNames[h.level] || `Hint Level ${h.level}`}
                </span>
                {h.source && (
                  <span style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'capitalize' }}>
                    {h.source}
                  </span>
                )}
              </div>
              <p style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                {h.text}
              </p>
            </div>
          ))
        )}
      </div>

      {/* Request Next Hint Action */}
      <div style={{ paddingTop: '12px', borderTop: '1px solid var(--border-color)' }}>
        <button
          className="btn-secondary"
          onClick={onGetHint}
          disabled={loading || !canRequestHint}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          {loading ? (
            'Consulting Coach...'
          ) : (
            <>
              <Lightbulb size={16} />
              Request Next Hint (Level {hints.length + 1})
            </>
          )}
        </button>
        {!canRequestHint && (
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center', marginTop: '6px' }}>
            Submit code first to unlock contextual hints
          </div>
        )}
      </div>
    </div>
  );
}

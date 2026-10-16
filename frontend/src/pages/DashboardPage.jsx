import React, { useState, useEffect } from 'react';
import { Award, AlertTriangle, CheckCircle, BarChart3, Target, ArrowRight, BookOpen, Sparkles } from 'lucide-react';
import { api } from '../lib/api';

export default function DashboardPage({ user, token, onSelectChallenge, onOpenAuth }) {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      if (!user) {
        setLoading(false);
        return;
      }
      setLoading(true);
      setError(null);
      try {
        const data = await api.getDashboard(token);
        setDashboard(data);
      } catch (err) {
        setError(err.message || 'Failed to load learner dashboard.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [user, token]);

  if (!user) {
    return (
      <div style={{ maxWidth: '600px', margin: '80px auto', textAlign: 'center', padding: '24px' }}>
        <div className="dojo-card">
          <Award size={40} color="var(--accent-blue)" style={{ marginBottom: '16px' }} />
          <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '8px' }}>
            Learner Dashboard
          </h2>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', fontSize: '14px' }}>
            Sign in or continue as a guest to track your concept mastery scores, recurring debugging mistakes, and tailored recommendations.
          </p>
          <button className="btn-primary" onClick={onOpenAuth}>
            Sign In / Guest Profile
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ padding: '80px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
        Gathering your dojo stats and mastery scores...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ maxWidth: '800px', margin: '40px auto', padding: '24px' }}>
        <div className="dojo-card" style={{ borderColor: 'var(--accent-rose)' }}>
          <h3 style={{ color: 'var(--accent-rose)', marginBottom: '8px' }}>Dashboard Error</h3>
          <p style={{ color: 'var(--text-secondary)' }}>{error}</p>
        </div>
      </div>
    );
  }

  const { progress = {}, recurring_mistakes = [], mastery = [], recommendation = {} } = dashboard || {};
  const completionPct = progress.total_challenges
    ? Math.round((progress.challenges_completed / progress.total_challenges) * 100)
    : 0;

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '36px 24px' }}>
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 800, marginBottom: '6px' }}>
          Learner Progress & Mastery
        </h1>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>
          Real-time analytics on your debugging habits, strengths, and targeted improvement areas.
        </p>
      </div>

      {/* Stats Header Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        <div className="dojo-card">
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Challenges Solved
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--accent-emerald)', marginTop: '4px' }}>
            {progress.challenges_completed || 0} <span style={{ fontSize: '16px', color: 'var(--text-muted)', fontWeight: 500 }}>/ {progress.total_challenges || 12}</span>
          </div>
          <div style={{ width: '100%', height: '6px', background: 'var(--bg-primary)', borderRadius: '3px', marginTop: '10px', overflow: 'hidden' }}>
            <div style={{ width: `${completionPct}%`, height: '100%', background: 'var(--accent-emerald)' }} />
          </div>
        </div>

        <div className="dojo-card">
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Total Submissions
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: 'var(--accent-blue)', marginTop: '4px' }}>
            {progress.total_submissions || 0}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '6px' }}>
            Attempts across all test suites
          </div>
        </div>

        <div className="dojo-card">
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
            Recurring Mistakes
          </div>
          <div style={{ fontSize: '32px', fontWeight: 800, color: recurring_mistakes.length > 0 ? 'var(--accent-amber)' : 'var(--accent-emerald)', marginTop: '4px' }}>
            {recurring_mistakes.length}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '6px' }}>
            Patterns detected in 2+ challenges
          </div>
        </div>
      </div>

      {/* AI Recommendation Banner */}
      {recommendation?.challenge_id && (
        <div
          style={{
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(139, 92, 246, 0.15))',
            border: '1px solid rgba(59, 130, 246, 0.35)',
            borderRadius: '10px',
            padding: '24px',
            marginBottom: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px',
          }}
        >
          <div style={{ maxWidth: '640px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--accent-blue)', fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px' }}>
              <Sparkles size={16} /> Recommended Challenge
            </div>
            <h3 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '6px' }}>
              {recommendation.challenge_title}
            </h3>
            <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {recommendation.reason}
            </p>
          </div>

          <button
            className="btn-primary"
            onClick={() => onSelectChallenge(recommendation.challenge_slug || recommendation.challenge_id)}
            style={{ padding: '10px 20px', fontSize: '14px' }}
          >
            Solve Challenge <ArrowRight size={16} />
          </button>
        </div>
      )}

      {/* Recurring Mistakes Section */}
      <section style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} color="var(--accent-amber)" />
          Recurring Mistake Patterns
        </h2>

        {recurring_mistakes.length === 0 ? (
          <div className="dojo-card" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)', fontSize: '14px' }}>
            <CheckCircle size={32} color="var(--accent-emerald)" style={{ marginBottom: '8px' }} />
            <div>No recurring mistake patterns detected!</div>
            <div style={{ fontSize: '12px', marginTop: '4px' }}>
              Recurring mistakes appear when a specific mistake pattern occurs across 2 or more distinct challenges.
            </div>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
            {recurring_mistakes.map((rm, i) => (
              <div
                key={i}
                className="dojo-card"
                style={{
                  background: 'rgba(245, 158, 11, 0.05)',
                  borderColor: 'rgba(245, 158, 11, 0.3)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--accent-amber)', textTransform: 'capitalize' }}>
                    {rm.category.replace(/_/g, ' ')}
                  </span>
                  <span style={{ fontSize: '11px', fontWeight: 600, background: 'rgba(245, 158, 11, 0.2)', color: 'var(--accent-amber)', padding: '2px 8px', borderRadius: '9999px' }}>
                    {rm.challenge_count} Challenges
                  </span>
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {rm.description}
                </p>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Concept Mastery Grid */}
      <section>
        <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BarChart3 size={18} color="var(--accent-blue)" />
          Concept Mastery
        </h2>

        {mastery.length === 0 ? (
          <div className="dojo-card" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)', fontSize: '14px' }}>
            Complete challenges to unlock concept mastery ratings across lists, slicing, math, strings, and recursion.
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '14px' }}>
            {mastery.map((m, idx) => {
              const pct = Math.round(m.score * 100);
              return (
                <div key={idx} className="dojo-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span style={{ fontWeight: 600, fontSize: '14px', textTransform: 'capitalize' }}>
                      {m.concept}
                    </span>
                    <span style={{ fontWeight: 700, fontSize: '14px', color: pct >= 80 ? 'var(--accent-emerald)' : pct >= 50 ? 'var(--accent-blue)' : 'var(--accent-amber)' }}>
                      {pct}%
                    </span>
                  </div>
                  <div style={{ width: '100%', height: '8px', background: 'var(--bg-primary)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${pct}%`,
                        height: '100%',
                        background: pct >= 80 ? 'var(--accent-emerald)' : pct >= 50 ? 'var(--accent-blue)' : 'var(--accent-amber)',
                      }}
                    />
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '8px' }}>
                    {m.completed_challenges} / {m.total_challenges} challenges completed
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

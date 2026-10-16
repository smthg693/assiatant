import React, { useState, useEffect } from 'react';
import { ArrowLeft, Play, RotateCcw, Lightbulb, CheckCircle2, AlertCircle, HelpCircle } from 'lucide-react';
import CodeEditor from '../components/CodeEditor';
import ResultsPanel from '../components/ResultsPanel';
import HintDrawer from '../components/HintDrawer';
import { api } from '../lib/api';

export default function WorkspacePage({ challengeSlug, onBack, user, token, onOpenAuth }) {
  const [challenge, setChallenge] = useState(null);
  const [code, setCode] = useState('');
  const [loadingChallenge, setLoadingChallenge] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGettingHint, setIsGettingHint] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [hints, setHints] = useState([]);
  const [error, setError] = useState(null);
  const [showHintsDrawer, setShowHintsDrawer] = useState(true);

  // Load Challenge
  useEffect(() => {
    async function load() {
      setLoadingChallenge(true);
      setError(null);
      try {
        const data = await api.getChallenge(challengeSlug, token);
        setChallenge(data);
        setCode(data.starter_code || '');
        setSubmissionResult(null);
        setHints([]);
      } catch (err) {
        setError('Failed to load challenge details.');
      } finally {
        setLoadingChallenge(false);
      }
    }
    load();
  }, [challengeSlug, token]);

  const handleResetCode = () => {
    if (challenge && window.confirm('Reset editor to original starter code?')) {
      setCode(challenge.starter_code || '');
    }
  };

  const handleSubmit = async () => {
    if (!user) {
      onOpenAuth();
      return;
    }
    if (!code.trim()) return;

    setIsSubmitting(true);
    setError(null);
    try {
      const res = await api.submitCode(challengeSlug, code, token);
      setSubmissionResult(res);
    } catch (err) {
      setError(err.message || 'Submission failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleGetHint = async () => {
    if (!user) {
      onOpenAuth();
      return;
    }
    if (!submissionResult?.submission_id) {
      setError('Please submit your code first to receive targeted hints.');
      return;
    }

    setIsGettingHint(true);
    try {
      const res = await api.getHint(submissionResult.submission_id, token);
      if (res?.hint) {
        setHints((prev) => [
          ...prev,
          {
            level: res.level,
            text: res.hint,
            source: res.source,
          },
        ]);
      }
    } catch (err) {
      setError(err.message || 'Could not fetch next hint.');
    } finally {
      setIsGettingHint(false);
    }
  };

  if (loadingChallenge) {
    return (
      <div style={{ padding: '60px 0', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading coding dojo environment...
      </div>
    );
  }

  if (error && !challenge) {
    return (
      <div style={{ maxWidth: '800px', margin: '40px auto', padding: '24px' }}>
        <button className="btn-ghost" onClick={onBack} style={{ marginBottom: '16px' }}>
          <ArrowLeft size={16} /> Back to Challenges
        </button>
        <div className="dojo-card" style={{ borderColor: 'var(--accent-rose)' }}>
          <h2 style={{ fontSize: '18px', color: 'var(--accent-rose)', marginBottom: '8px' }}>Challenge Error</h2>
          <p style={{ color: 'var(--text-secondary)' }}>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 61px)', overflow: 'hidden' }}>
      {/* Workspace Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 20px',
          backgroundColor: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-color)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <button className="btn-ghost" onClick={onBack} style={{ padding: '6px' }}>
            <ArrowLeft size={18} />
          </button>
          <h2 style={{ fontSize: '16px', fontWeight: 700 }}>{challenge.title}</h2>
          <span className={`badge badge-${challenge.difficulty}`}>{challenge.difficulty}</span>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button
            className="btn-ghost"
            onClick={() => setShowHintsDrawer(!showHintsDrawer)}
            style={{
              color: showHintsDrawer ? 'var(--accent-amber)' : 'var(--text-secondary)',
              background: showHintsDrawer ? 'rgba(245, 158, 11, 0.1)' : 'transparent',
            }}
          >
            <Lightbulb size={16} />
            Hints {hints.length > 0 && `(${hints.length})`}
          </button>

          <button className="btn-secondary" onClick={handleResetCode} title="Reset starter code">
            <RotateCcw size={15} /> Reset
          </button>

          <button
            className="btn-success"
            onClick={handleSubmit}
            disabled={isSubmitting}
            style={{ minWidth: '120px', justifyContent: 'center' }}
          >
            <Play size={15} />
            {isSubmitting ? 'Evaluating...' : 'Run & Submit'}
          </button>
        </div>
      </div>

      {/* Execution Error / Service Unavailable Banner with Retry */}
      {error && (
        <div
          style={{
            padding: '10px 20px',
            backgroundColor: 'rgba(244, 63, 94, 0.12)',
            borderBottom: '1px solid rgba(244, 63, 94, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '13px',
            color: 'var(--accent-rose)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
          <button
            className="btn-secondary"
            onClick={handleSubmit}
            disabled={isSubmitting}
            style={{ padding: '4px 10px', fontSize: '12px' }}
          >
            Retry Submission
          </button>
        </div>
      )}

      {/* Main Split Layout */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Left Pane: Challenge Description */}
        <div
          style={{
            width: '36%',
            minWidth: '320px',
            backgroundColor: 'var(--bg-card)',
            borderRight: '1px solid var(--border-color)',
            padding: '24px',
            overflowY: 'auto',
          }}
        >
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '16px' }}>
            {challenge.concepts.map((c, i) => (
              <span key={i} className="badge-tag">
                {c}
              </span>
            ))}
          </div>

          <div
            style={{
              fontSize: '14px',
              color: 'var(--text-primary)',
              lineHeight: 1.6,
              whiteSpace: 'pre-line',
            }}
          >
            {challenge.description}
          </div>

          {/* Visible Test Fixtures Reference */}
          {challenge.visible_tests && challenge.visible_tests.length > 0 && (
            <div style={{ marginTop: '24px' }}>
              <h4 style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                Visible Test Cases ({challenge.visible_tests.length})
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {challenge.visible_tests.map((t) => (
                  <div
                    key={t.test_number}
                    style={{
                      background: 'var(--bg-primary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: '6px',
                      padding: '8px 12px',
                      fontSize: '12px',
                      fontFamily: 'var(--font-mono)',
                    }}
                  >
                    <div style={{ color: 'var(--text-muted)', fontSize: '10px' }}>Test #{t.test_number}</div>
                    <div style={{ color: 'var(--accent-blue)', margin: '2px 0' }}>
                      {t.function_name}({t.input_args.slice(1, -1)})
                    </div>
                    <div style={{ color: 'var(--accent-emerald)' }}>
                      Expected: {t.expected_output}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Center Pane: CodeMirror Editor & Results Bottom */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* Top Half: Code Editor */}
          <div style={{ flex: '1 1 55%', padding: '12px', minHeight: '260px', overflow: 'hidden' }}>
            <CodeEditor value={code} onChange={setCode} onRun={handleSubmit} disabled={isSubmitting} />
          </div>

          {/* Bottom Half: Results Panel */}
          <div
            style={{
              flex: '1 1 45%',
              borderTop: '1px solid var(--border-color)',
              backgroundColor: 'var(--bg-secondary)',
              overflow: 'hidden',
            }}
          >
            <ResultsPanel submissionResult={submissionResult} isSubmitting={isSubmitting} />
          </div>
        </div>

        {/* Right Pane: Progressive Hint Drawer */}
        {showHintsDrawer && (
          <div style={{ width: '320px', minWidth: '280px' }}>
            <HintDrawer
              hints={hints}
              onGetHint={handleGetHint}
              loading={isGettingHint}
              canRequestHint={Boolean(submissionResult?.submission_id)}
            />
          </div>
        )}
      </div>
    </div>
  );
}

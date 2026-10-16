import React, { useState } from 'react';
import { CheckCircle2, XCircle, AlertTriangle, Clock, ShieldCheck, Bug, Eye, EyeOff } from 'lucide-react';

export default function ResultsPanel({ submissionResult, isSubmitting }) {
  const [activeTab, setActiveTab] = useState('visible'); // 'visible' | 'hidden' | 'diagnosis'

  if (isSubmitting) {
    return (
      <div
        style={{
          padding: '40px 20px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '12px',
          color: 'var(--text-secondary)',
        }}
      >
        <div
          style={{
            width: '28px',
            height: '28px',
            border: '3px solid var(--border-color)',
            borderTopColor: 'var(--accent-blue)',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }}
        />
        <style>{`@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`}</style>
        <div style={{ fontSize: '14px', fontWeight: 500 }}>Executing tests in sandbox...</div>
      </div>
    );
  }

  if (!submissionResult) {
    return (
      <div
        style={{
          padding: '40px 20px',
          textAlign: 'center',
          color: 'var(--text-muted)',
          fontSize: '13px',
        }}
      >
        Run or Submit your solution to see test evaluation results, mistake diagnosis, and feedback.
      </div>
    );
  }

  const { overall_status, total_passed, total_tests, visible_results = [], hidden_results = [], mistake_tags = [], explanation = '' } = submissionResult;
  const isPassed = overall_status === 'passed';

  const renderOutcomeBadge = (outcome) => {
    switch (outcome) {
      case 'passed':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--accent-emerald)', fontSize: '12px', fontWeight: 600 }}>
            <CheckCircle2 size={14} /> Passed
          </span>
        );
      case 'wrong_output':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--accent-rose)', fontSize: '12px', fontWeight: 600 }}>
            <XCircle size={14} /> Wrong Output
          </span>
        );
      case 'runtime_error':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--accent-amber)', fontSize: '12px', fontWeight: 600 }}>
            <AlertTriangle size={14} /> Runtime Error
          </span>
        );
      case 'timeout':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--accent-amber)', fontSize: '12px', fontWeight: 600 }}>
            <Clock size={14} /> Timeout
          </span>
        );
      default:
        return <span>{outcome}</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Overall Status Banner */}
      <div
        style={{
          padding: '12px 16px',
          backgroundColor: isPassed ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)',
          borderBottom: `1px solid ${isPassed ? 'rgba(16, 185, 129, 0.3)' : 'rgba(244, 63, 94, 0.3)'}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {isPassed ? (
            <CheckCircle2 size={20} color="var(--accent-emerald)" />
          ) : (
            <XCircle size={20} color="var(--accent-rose)" />
          )}
          <span style={{ fontWeight: 600, fontSize: '14px' }}>
            {isPassed ? 'All Tests Passed! 🎉' : 'Submission Incomplete'}
          </span>
        </div>
        <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-secondary)' }}>
          {total_passed} / {total_tests} Tests Passed
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--bg-secondary)' }}>
        <button
          className="btn-ghost"
          onClick={() => setActiveTab('visible')}
          style={{
            borderRadius: 0,
            borderBottom: activeTab === 'visible' ? '2px solid var(--accent-blue)' : '2px solid transparent',
            color: activeTab === 'visible' ? 'var(--text-primary)' : 'var(--text-muted)',
            padding: '10px 16px',
            fontSize: '13px',
          }}
        >
          <Eye size={15} /> Visible Tests ({visible_results.length})
        </button>

        <button
          className="btn-ghost"
          onClick={() => setActiveTab('hidden')}
          style={{
            borderRadius: 0,
            borderBottom: activeTab === 'hidden' ? '2px solid var(--accent-blue)' : '2px solid transparent',
            color: activeTab === 'hidden' ? 'var(--text-primary)' : 'var(--text-muted)',
            padding: '10px 16px',
            fontSize: '13px',
          }}
        >
          <EyeOff size={15} /> Hidden Tests ({hidden_results.length})
        </button>

        <button
          className="btn-ghost"
          onClick={() => setActiveTab('diagnosis')}
          style={{
            borderRadius: 0,
            borderBottom: activeTab === 'diagnosis' ? '2px solid var(--accent-blue)' : '2px solid transparent',
            color: activeTab === 'diagnosis' ? 'var(--text-primary)' : 'var(--text-muted)',
            padding: '10px 16px',
            fontSize: '13px',
          }}
        >
          <Bug size={15} /> Diagnosis {mistake_tags.length > 0 && `(${mistake_tags.length})`}
        </button>
      </div>

      {/* Tab Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        {activeTab === 'visible' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {visible_results.map((r) => (
              <div
                key={r.test_number}
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '12px',
                  fontSize: '13px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                  <span style={{ fontWeight: 600 }}>Test #{r.test_number}</span>
                  {renderOutcomeBadge(r.outcome)}
                </div>

                {r.call_expression && (
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--accent-blue)', marginBottom: '8px' }}>
                    {r.call_expression}
                  </div>
                )}

                {r.outcome === 'wrong_output' && (
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '6px' }}>
                    <div style={{ background: 'var(--bg-primary)', padding: '6px 8px', borderRadius: '4px' }}>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Expected</div>
                      <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-emerald)', marginTop: '2px' }}>
                        {r.expected}
                      </div>
                    </div>
                    <div style={{ background: 'var(--bg-primary)', padding: '6px 8px', borderRadius: '4px' }}>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Actual</div>
                      <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-rose)', marginTop: '2px' }}>
                        {r.actual || 'None'}
                      </div>
                    </div>
                  </div>
                )}

                {r.error_message && (
                  <div
                    style={{
                      marginTop: '6px',
                      background: 'rgba(244, 63, 94, 0.1)',
                      border: '1px solid rgba(244, 63, 94, 0.2)',
                      padding: '8px',
                      borderRadius: '4px',
                      color: 'var(--accent-rose)',
                      fontFamily: 'var(--font-mono)',
                      fontSize: '12px',
                    }}
                  >
                    {r.error_message}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {activeTab === 'hidden' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div
              style={{
                display: 'flex',
                gap: '8px',
                alignItems: 'center',
                background: 'rgba(59, 130, 246, 0.08)',
                border: '1px solid rgba(59, 130, 246, 0.2)',
                padding: '10px 12px',
                borderRadius: '6px',
                fontSize: '12px',
                color: 'var(--text-secondary)',
              }}
            >
              <ShieldCheck size={18} color="var(--accent-blue)" style={{ flexShrink: 0 }} />
              <span>
                Hidden test cases verify edge cases and boundary conditions. Inputs and expected values are kept private.
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '10px' }}>
              {hidden_results.map((hr) => (
                <div
                  key={hr.test_number}
                  style={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '6px',
                    padding: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                  }}
                >
                  <span style={{ fontSize: '13px', fontWeight: 600 }}>Test #{hr.test_number}</span>
                  {renderOutcomeBadge(hr.outcome)}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'diagnosis' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {explanation && (
              <div
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '6px',
                  padding: '14px',
                }}
              >
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '6px' }}>
                  AI Coach Explanation
                </div>
                <div style={{ fontSize: '14px', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                  {explanation}
                </div>
              </div>
            )}

            {mistake_tags.length > 0 && (
              <div>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Detected Mistake Patterns
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {mistake_tags.map((m, idx) => (
                    <div
                      key={idx}
                      style={{
                        background: 'rgba(245, 158, 11, 0.08)',
                        border: '1px solid rgba(245, 158, 11, 0.25)',
                        borderRadius: '6px',
                        padding: '12px',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '4px' }}>
                        <AlertTriangle size={15} color="var(--accent-amber)" />
                        <span style={{ fontWeight: 600, fontSize: '13px', color: 'var(--accent-amber)', textTransform: 'capitalize' }}>
                          {m.category.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                        {m.evidence}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

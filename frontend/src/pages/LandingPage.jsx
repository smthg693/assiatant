import React from 'react';
import { Terminal, Shield, Award, Lightbulb, Play, ArrowRight, Zap, Target } from 'lucide-react';

export default function LandingPage({ onStart, onOpenCatalogue }) {
  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '48px 24px' }}>
      {/* Hero Section */}
      <section style={{ textAlign: 'center', marginBottom: '64px' }}>
        <div
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            background: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            padding: '6px 14px',
            borderRadius: '9999px',
            fontSize: '13px',
            color: 'var(--accent-blue)',
            fontWeight: 600,
            marginBottom: '20px',
          }}
        >
          <Zap size={14} /> AI-Powered Python Debug Coach
        </div>

        <h1
          style={{
            fontSize: '44px',
            fontWeight: 800,
            lineHeight: 1.15,
            letterSpacing: '-1px',
            marginBottom: '18px',
            background: 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Learn to Debug Code.<br />Don't Just Copy the Solution.
        </h1>

        <p
          style={{
            fontSize: '18px',
            color: 'var(--text-secondary)',
            maxWidth: '680px',
            margin: '0 auto 32px auto',
            lineHeight: 1.6,
          }}
        >
          Debug Dojo guides you through diagnosing your own bugs with sandboxed execution,
          ordered conceptual hints, and personalized mistake pattern analysis.
        </p>

        <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
          <button className="btn-primary" style={{ padding: '12px 24px', fontSize: '15px' }} onClick={onStart}>
            <Play size={18} />
            Start with Mandatory Challenges
          </button>
          <button className="btn-secondary" style={{ padding: '12px 24px', fontSize: '15px' }} onClick={onOpenCatalogue}>
            Browse All Challenges
            <ArrowRight size={16} />
          </button>
        </div>
      </section>

      {/* Core Philosophy & Features */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '64px' }}>
        <div className="dojo-card">
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '8px',
              background: 'rgba(59, 130, 246, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-blue)',
              marginBottom: '16px',
            }}
          >
            <Shield size={22} />
          </div>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
            Sandboxed Evaluation
          </h3>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Code runs against 3+ visible and 5+ hidden test cases. Hidden test fixtures are strictly protected
            on the server to prevent adversarial leaks.
          </p>
        </div>

        <div className="dojo-card">
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '8px',
              background: 'rgba(245, 158, 11, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-amber)',
              marginBottom: '16px',
            }}
          >
            <Lightbulb size={22} />
          </div>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
            Progressive Hint Ladder
          </h3>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Never get spoon-fed the answer. Hints start with conceptual nudges, progress to directional debugging cues,
            and keep you in the driver’s seat.
          </p>
        </div>

        <div className="dojo-card">
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '8px',
              background: 'rgba(16, 185, 129, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--accent-emerald)',
              marginBottom: '16px',
            }}
          >
            <Target size={22} />
          </div>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>
            Mistake Pattern Learning
          </h3>
          <p style={{ fontSize: '14px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Debug Dojo classifies off-by-one, boundary comparison, empty inputs, mutation, and print-vs-return errors.
            Identifies recurring habits across challenges.
          </p>
        </div>
      </section>

      {/* Mandatory Challenges Quick Launch */}
      <section style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '32px' }}>
        <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '8px' }}>
          Mandatory Challenges
        </h2>
        <p style={{ fontSize: '14px', color: 'var(--text-secondary)', marginBottom: '20px' }}>
          Master these core Python algorithms designed to test slicing, conditions, math, and edge cases.
        </p>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
          {[
            { slug: 'last-k-total', title: 'Last K Total', desc: 'Sum the last k elements, handling bounds and empty inputs' },
            { slug: 'count-passes', title: 'Count Passes', desc: 'Count marks >= 40 at comparison boundaries' },
            { slug: 'first-n-squares', title: 'First N Squares', desc: 'List of perfect squares starting from 1 to n²' },
            { slug: 'middle-three', title: 'Middle Three', desc: 'Slice the middle 3 elements with odd-length handling' },
          ].map((item) => (
            <div
              key={item.slug}
              className="dojo-card"
              style={{ cursor: 'pointer', padding: '16px' }}
              onClick={() => onStart(item.slug)}
            >
              <div style={{ fontSize: '15px', fontWeight: 600, marginBottom: '4px', color: 'var(--accent-blue)' }}>
                {item.title}
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {item.desc}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

import React, { useState } from 'react';
import { X, Lock, Mail, UserCheck, ShieldCheck } from 'lucide-react';
import { supabase, isSupabaseConfigured } from '../lib/supabase';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [mode, setMode] = useState('signin'); // 'signin' | 'signup' | 'recovery'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      if (mode === 'recovery') {
        if (supabase) {
          const { error } = await supabase.auth.resetPasswordForEmail(email);
          if (error) throw error;
          setMessage('Password reset instructions sent to your email.');
        } else {
          setMessage('Demo Mode: Reset email dispatched for ' + email);
        }
        setLoading(false);
        return;
      }

      if (mode === 'signup') {
        if (supabase) {
          const { data, error } = await supabase.auth.signUp({ email, password });
          if (error) throw error;
          if (data?.session) {
            onAuthSuccess({
              sub: data.session.user.id,
              email: data.session.user.email,
              token: data.session.access_token,
            });
            onClose();
          } else {
            setMessage('Account created! Please check your email to confirm registration.');
          }
        } else {
          // Demo fallback
          onAuthSuccess({
            sub: 'demo-learner-' + Math.random().toString(36).substring(2, 9),
            email,
            token: 'demo-token',
          });
          onClose();
        }
        setLoading(false);
        return;
      }

      if (mode === 'signin') {
        if (supabase) {
          const { data, error } = await supabase.auth.signInWithPassword({ email, password });
          if (error) throw error;
          onAuthSuccess({
            sub: data.session.user.id,
            email: data.session.user.email,
            token: data.session.access_token,
          });
          onClose();
        } else {
          // Demo fallback
          onAuthSuccess({
            sub: 'demo-learner-' + Math.random().toString(36).substring(2, 9),
            email,
            token: 'demo-token',
          });
          onClose();
        }
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleGuestLogin = () => {
    onAuthSuccess({
      sub: 'guest-sensei-' + Math.random().toString(36).substring(2, 8),
      email: 'guest@debugdojo.dev',
      token: 'demo-token',
    });
    onClose();
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '16px',
        backdropFilter: 'blur(4px)',
      }}
      onClick={onClose}
    >
      <div
        className="dojo-card"
        style={{
          width: '100%',
          maxWidth: '420px',
          background: 'var(--bg-secondary)',
          position: 'relative',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          className="btn-ghost"
          style={{ position: 'absolute', top: '16px', right: '16px', padding: '6px' }}
          onClick={onClose}
          aria-label="Close Modal"
        >
          <X size={18} />
        </button>

        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              marginBottom: '12px',
            }}
          >
            <ShieldCheck size={24} />
          </div>
          <h2 style={{ fontSize: '20px', fontWeight: 700 }}>
            {mode === 'signin' && 'Welcome to the Dojo'}
            {mode === 'signup' && 'Create Your Belt Profile'}
            {mode === 'recovery' && 'Reset Password'}
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>
            {mode === 'signin' && 'Sign in to track mistakes, mastery, and earn hints.'}
            {mode === 'signup' && 'Register your learner account.'}
            {mode === 'recovery' && 'Enter your email to receive recovery instructions.'}
          </p>
        </div>

        {/* Mode Selector */}
        {mode !== 'recovery' && (
          <div
            style={{
              display: 'flex',
              background: 'var(--bg-primary)',
              borderRadius: '6px',
              padding: '4px',
              marginBottom: '20px',
            }}
          >
            <button
              type="button"
              onClick={() => { setMode('signin'); setError(null); setMessage(null); }}
              style={{
                flex: 1,
                padding: '6px',
                border: 'none',
                borderRadius: '4px',
                fontSize: '13px',
                fontWeight: 600,
                background: mode === 'signin' ? 'var(--bg-tertiary)' : 'transparent',
                color: mode === 'signin' ? 'var(--text-primary)' : 'var(--text-muted)',
              }}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => { setMode('signup'); setError(null); setMessage(null); }}
              style={{
                flex: 1,
                padding: '6px',
                border: 'none',
                borderRadius: '4px',
                fontSize: '13px',
                fontWeight: 600,
                background: mode === 'signup' ? 'var(--bg-tertiary)' : 'transparent',
                color: mode === 'signup' ? 'var(--text-primary)' : 'var(--text-muted)',
              }}
            >
              Sign Up
            </button>
          </div>
        )}

        {error && (
          <div
            style={{
              padding: '10px 12px',
              borderRadius: '6px',
              background: 'rgba(244, 63, 94, 0.1)',
              border: '1px solid rgba(244, 63, 94, 0.3)',
              color: 'var(--accent-rose)',
              fontSize: '13px',
              marginBottom: '16px',
            }}
          >
            {error}
          </div>
        )}

        {message && (
          <div
            style={{
              padding: '10px 12px',
              borderRadius: '6px',
              background: 'rgba(16, 185, 129, 0.1)',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              color: 'var(--accent-emerald)',
              fontSize: '13px',
              marginBottom: '16px',
            }}
          >
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '6px', color: 'var(--text-secondary)' }}>
              Email Address
            </label>
            <div style={{ position: 'relative' }}>
              <Mail size={16} style={{ position: 'absolute', left: '12px', top: '11px', color: 'var(--text-muted)' }} />
              <input
                type="email"
                required
                className="dojo-input"
                style={{ width: '100%', paddingLeft: '36px' }}
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          {mode !== 'recovery' && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                <label style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-secondary)' }}>
                  Password
                </label>
                {mode === 'signin' && (
                  <button
                    type="button"
                    onClick={() => { setMode('recovery'); setError(null); setMessage(null); }}
                    style={{ background: 'none', border: 'none', color: 'var(--accent-blue)', fontSize: '12px' }}
                  >
                    Forgot?
                  </button>
                )}
              </div>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: '12px', top: '11px', color: 'var(--text-muted)' }} />
                <input
                  type="password"
                  required
                  minLength={6}
                  className="dojo-input"
                  style={{ width: '100%', paddingLeft: '36px' }}
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            className="btn-primary"
            disabled={loading}
            style={{ width: '100%', justifyContent: 'center', marginTop: '6px', padding: '10px' }}
          >
            {loading ? 'Processing...' : mode === 'signin' ? 'Sign In' : mode === 'signup' ? 'Sign Up' : 'Send Reset Link'}
          </button>
        </form>

        {mode === 'recovery' && (
          <div style={{ textAlign: 'center', marginTop: '14px' }}>
            <button
              type="button"
              className="btn-ghost"
              onClick={() => { setMode('signin'); setError(null); setMessage(null); }}
              style={{ fontSize: '12px' }}
            >
              Back to Sign In
            </button>
          </div>
        )}

        <div style={{ position: 'relative', textAlign: 'center', margin: '20px 0' }}>
          <div style={{ position: 'absolute', top: '50%', left: 0, right: 0, height: '1px', background: 'var(--border-color)' }} />
          <span style={{ position: 'relative', background: 'var(--bg-secondary)', padding: '0 10px', fontSize: '12px', color: 'var(--text-muted)' }}>
            OR
          </span>
        </div>

        <button
          type="button"
          className="btn-secondary"
          onClick={handleGuestLogin}
          style={{ width: '100%', justifyContent: 'center' }}
        >
          <UserCheck size={16} />
          Continue as Instant Guest Learner
        </button>
      </div>
    </div>
  );
}

import React from 'react';
import { Terminal, Shield, Award, LogIn, LogOut, User } from 'lucide-react';

export default function Navbar({ activePage, setActivePage, user, onOpenAuth, onSignOut }) {
  return (
    <header
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '12px 24px',
        backgroundColor: 'var(--bg-secondary)',
        borderBottom: '1px solid var(--border-color)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}
    >
      <div
        style={{ display: 'flex', alignItems: 'center', gap: '28px', cursor: 'pointer' }}
        onClick={() => setActivePage('landing')}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div
            style={{
              width: '34px',
              height: '34px',
              borderRadius: '8px',
              background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
            }}
          >
            <Terminal size={20} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '18px', letterSpacing: '-0.5px' }}>
              Debug Dojo <span style={{ fontSize: '14px' }}>🥋</span>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '-2px' }}>
              AI Python Debug Coach
            </div>
          </div>
        </div>

        <nav style={{ display: 'flex', gap: '8px' }}>
          <button
            className={`btn-ghost ${activePage === 'catalogue' ? 'active-nav' : ''}`}
            onClick={(e) => {
              e.stopPropagation();
              setActivePage('catalogue');
            }}
            style={{
              color: activePage === 'catalogue' ? 'var(--text-primary)' : 'var(--text-secondary)',
              fontWeight: activePage === 'catalogue' ? 600 : 500,
              background: activePage === 'catalogue' ? 'var(--bg-tertiary)' : 'transparent',
            }}
          >
            Challenges
          </button>
          <button
            className={`btn-ghost ${activePage === 'dashboard' ? 'active-nav' : ''}`}
            onClick={(e) => {
              e.stopPropagation();
              setActivePage('dashboard');
            }}
            style={{
              color: activePage === 'dashboard' ? 'var(--text-primary)' : 'var(--text-secondary)',
              fontWeight: activePage === 'dashboard' ? 600 : 500,
              background: activePage === 'dashboard' ? 'var(--bg-tertiary)' : 'transparent',
            }}
          >
            <Award size={16} />
            My Dashboard
          </button>
        </nav>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        {user ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '13px',
                color: 'var(--text-secondary)',
                background: 'var(--bg-tertiary)',
                padding: '6px 12px',
                borderRadius: '9999px',
                border: '1px solid var(--border-color)',
              }}
            >
              <User size={14} color="var(--accent-emerald)" />
              <span>{user.email || 'Learner'}</span>
            </div>
            <button className="btn-ghost" onClick={onSignOut} title="Sign Out">
              <LogOut size={16} />
            </button>
          </div>
        ) : (
          <button className="btn-primary" onClick={onOpenAuth}>
            <LogIn size={16} />
            Sign In / Guest
          </button>
        )}
      </div>
    </header>
  );
}

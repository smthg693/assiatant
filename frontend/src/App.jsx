import React, { useState, useEffect } from 'react';
import './styles/theme.css';
import Navbar from './components/Navbar';
import LandingPage from './pages/LandingPage';
import CataloguePage from './pages/CataloguePage';
import WorkspacePage from './pages/WorkspacePage';
import DashboardPage from './pages/DashboardPage';
import AuthModal from './pages/AuthModal';
import { supabase } from './lib/supabase';

export default function App() {
  const [activePage, setActivePage] = useState('landing'); // 'landing' | 'catalogue' | 'workspace' | 'dashboard'
  const [selectedChallengeSlug, setSelectedChallengeSlug] = useState('last-k-total');
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('debug_dojo_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isAuthOpen, setIsAuthOpen] = useState(false);

  // Sync Supabase Auth session if configured
  useEffect(() => {
    if (supabase) {
      supabase.auth.getSession().then(({ data: { session } }) => {
        if (session) {
          const authUser = {
            sub: session.user.id,
            email: session.user.email,
            token: session.access_token,
          };
          setUser(authUser);
          localStorage.setItem('debug_dojo_user', JSON.stringify(authUser));
        }
      });

      const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
        if (session) {
          const authUser = {
            sub: session.user.id,
            email: session.user.email,
            token: session.access_token,
          };
          setUser(authUser);
          localStorage.setItem('debug_dojo_user', JSON.stringify(authUser));
        } else {
          setUser(null);
          localStorage.removeItem('debug_dojo_user');
        }
      });

      return () => subscription.unsubscribe();
    }
  }, []);

  const handleAuthSuccess = (authUser) => {
    setUser(authUser);
    localStorage.setItem('debug_dojo_user', JSON.stringify(authUser));
  };

  const handleSignOut = async () => {
    if (supabase) {
      await supabase.auth.signOut().catch(() => {});
    }
    setUser(null);
    localStorage.removeItem('debug_dojo_user');
  };

  const handleSelectChallenge = (slug) => {
    setSelectedChallengeSlug(slug);
    setActivePage('workspace');
  };

  return (
    <div className="debug-dojo-app" style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        activePage={activePage}
        setActivePage={setActivePage}
        user={user}
        onOpenAuth={() => setIsAuthOpen(true)}
        onSignOut={handleSignOut}
      />

      <main style={{ flex: 1 }}>
        {activePage === 'landing' && (
          <LandingPage
            onStart={(slug) => handleSelectChallenge(slug || 'last-k-total')}
            onOpenCatalogue={() => setActivePage('catalogue')}
          />
        )}

        {activePage === 'catalogue' && (
          <CataloguePage
            onSelectChallenge={handleSelectChallenge}
            token={user?.token}
          />
        )}

        {activePage === 'workspace' && (
          <WorkspacePage
            challengeSlug={selectedChallengeSlug}
            onBack={() => setActivePage('catalogue')}
            user={user}
            token={user?.token}
            onOpenAuth={() => setIsAuthOpen(true)}
          />
        )}

        {activePage === 'dashboard' && (
          <DashboardPage
            user={user}
            token={user?.token}
            onSelectChallenge={handleSelectChallenge}
            onOpenAuth={() => setIsAuthOpen(true)}
          />
        )}
      </main>

      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />
    </div>
  );
}

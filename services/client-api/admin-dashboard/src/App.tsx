import { useState } from 'react';
import { IntroSlides } from './components/Onboarding/IntroSlides';
import { GuidePage } from './components/Onboarding/GuidePage';
import { LoginPage } from './components/Auth/LoginPage';
import { DashboardLayout } from './components/Dashboard/DashboardLayout';
import { LoadingSpinner } from './components/common/LoadingSpinner';
import type { AppView } from './types';
import './styles/globals.css';
import './styles/animations.css';

function App() {
  const [currentView, setCurrentView] = useState<AppView>('intro');
  const [isLoading, setIsLoading] = useState(false);

  const handleTransition = (nextView: AppView) => {
    setIsLoading(true);
    setTimeout(() => {
      setCurrentView(nextView);
      setIsLoading(false);
    }, 800);
  };

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div className="app">
      {currentView === 'intro' && (
        <IntroSlides onComplete={() => handleTransition('guide')} />
      )}
      {currentView === 'guide' && (
        <GuidePage onComplete={() => handleTransition('login')} />
      )}
      {currentView === 'login' && (
        <LoginPage onLogin={() => handleTransition('dashboard')} />
      )}
      {currentView === 'dashboard' && <DashboardLayout />}
    </div>
  );
}

export default App;

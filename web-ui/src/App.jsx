import { useState } from 'react'
import Header from './components/Header'
import AuthScreen from './pages/AuthScreen'
import HomeScreen from './pages/HomeScreen'
import InterviewScreen from './pages/InterviewScreen'
import ReportScreen from './pages/ReportScreen'

function App() {
  const [currentView, setCurrentView] = useState('auth');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  const [interviewReport, setInterviewReport] = useState(null);
  const [activeMatchId, setActiveMatchId] = useState(null); 

  const handleInterviewFinish = (reportData) => {
    setInterviewReport(reportData); 
    setCurrentView('report');       
  };
  
  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentView('auth');
  };
  
  const handleGoToHistory = () => {
    if (!isAuthenticated) return;
    
    setCurrentView('home');
    
    setTimeout(() => {
      document.getElementById('past-interviews')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const renderView = () => {
    switch (currentView) {
      case 'auth':
        return <AuthScreen 
                 onLogin={() => {
                   setIsAuthenticated(true);
                   setCurrentView('home');
                 }} 
               />;
      case 'home':
        return <HomeScreen 
                 onStartInterview={(id) => {
                   setActiveMatchId(id); 
                   setCurrentView('interview');
                 }} 
               />;
      case 'interview':
        return <InterviewScreen 
                 matchId={activeMatchId} 
                 onFinish={handleInterviewFinish} 
                 onCancel={() => setCurrentView('home')} 
               />;
      case 'report':
        return <ReportScreen 
                 reportData={interviewReport} 
                 onReturnHome={() => {
                   setInterviewReport(null); 
                   setCurrentView('home');
                 }} 
               />;
      default:
        return <AuthScreen onLogin={() => setCurrentView('home')} />;
    }
  };

  return (
    <>
      <Header 
        isAuthenticated={isAuthenticated} 
        onLogout={handleLogout} 
        onLogoClick={() => isAuthenticated && setCurrentView('home')} 
        onHistoryClick={handleGoToHistory} 
      />
      <main>
        {renderView()}
      </main>
    </>
  )
}

export default App
import { useState } from 'react'
import Header from './components/Header'
import AuthScreen from './pages/AuthScreen'
import HomeScreen from './pages/HomeScreen'
import InterviewScreen from './pages/InterviewScreen'
import ReportScreen from './pages/ReportScreen'

function App() {
  const [currentView, setCurrentView] = useState('auth');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // Mülakat sonucunu (raporu) tutacağımız state
  const [interviewReport, setInterviewReport] = useState(null);

  // Mülakat bittiğinde çalışacak fonksiyon (Veriyi yakalar)
  const handleInterviewFinish = (reportData) => {
    setInterviewReport(reportData); // Gelen raporu kaydet
    setCurrentView('report');       // Rapor ekranına geç
  };
  
  // Çıkış yapma fonksiyonu
  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentView('auth');
  };
  const handleGoToHistory = () => {
    if (!isAuthenticated) return;
    
    // Önce Ana Sayfaya (home) geçiş yap
    setCurrentView('home');
    
    // DOM'un (ekranın) render olması için çok kısa bir süre bekleyip aşağı kaydır
    setTimeout(() => {
      document.getElementById('past-interviews')?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  // Hangi ekranın render edileceğini belirleyen fonksiyon
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
        return <HomeScreen onStartInterview={() => setCurrentView('interview')} />;
      case 'interview':
        // DÜZELTME 1: onFinish olayını handleInterviewFinish fonksiyonuna bağladık
        return <InterviewScreen 
                 onFinish={handleInterviewFinish} 
                 onCancel={() => setCurrentView('home')} 
               />;
      case 'report':
        // DÜZELTME 2: reportData prop'unu ekledik
        return <ReportScreen 
                 reportData={interviewReport} 
                 onReturnHome={() => {
                   setInterviewReport(null); // Temizleyip eve dön
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
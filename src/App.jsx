import { useState } from 'react'
import Header from './components/Header'
import AuthScreen from './pages/AuthScreen'
import HomeScreen from './pages/HomeScreen'
import InterviewScreen from './pages/InterviewScreen'
import ReportScreen from './pages/ReportScreen'

function App() {
  // Uygulamanın hangi ekranda olduğunu tutan state
  // Olası değerler: 'auth', 'home', 'interview', 'report'
  const [currentView, setCurrentView] = useState('auth');
  
  // Kullanıcının giriş yapıp yapmadığını tutan state
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Çıkış yapma fonksiyonu
  const handleLogout = () => {
    setIsAuthenticated(false);
    setCurrentView('auth');
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
        return <InterviewScreen 
                 onFinish={() => setCurrentView('report')} 
                 onCancel={() => setCurrentView('home')} 
               />;
      case 'report':
        return <ReportScreen onReturnHome={() => setCurrentView('home')} />;
      default:
        return <AuthScreen onLogin={() => setCurrentView('home')} />;
    }
  };

  return (
    <>
      <Header isAuthenticated={isAuthenticated} onLogout={handleLogout} onLogoClick={() => isAuthenticated && setCurrentView('home')} />
      <main>
        {renderView()}
      </main>
    </>
  )
}

export default App
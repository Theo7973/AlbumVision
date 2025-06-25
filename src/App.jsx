import { useState } from 'react';
import IntroAnimation from './components/IntroAnimation';

function App() {
  const [showMain, setShowMain] = useState(false);
  const [launched, setLaunched] = useState(false);

  const handleFinish = () => {
    setShowMain(true);
    setLaunched(true);
  };

  if (launched) {
    return (
      <div style={{ color: 'white', backgroundColor: 'black', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <h2>Launching Album Vision+ App...</h2>
      </div>
    );
  }

  return (
    <>
      {!showMain ? (
        <IntroAnimation onFinish={handleFinish} />
      ) : null}
    </>
  );
}

export default App;

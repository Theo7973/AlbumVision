import { useState } from 'react';
import IntroAnimation from './components/IntroAnimation';

function App() {
  const [showMain, setShowMain] = useState(false);

  return (
    <>
      {!showMain ? (
        <IntroAnimation onFinish={() => setShowMain(true)} />
      ) : (
        <div>
          <h1>Main App Content</h1>
        </div>
      )}
    </>
  );
}

export default App;


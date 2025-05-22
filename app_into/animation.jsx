import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useState } from 'react';
import './animation.css';

export default function IntroAnimation({ onFinish }) {
  const [showAnimation, setShowAnimation] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowAnimation(false);
      if (onFinish) onFinish(); // let parent know to switch screen
    }, 2500); // 2.5 seconds total

    return () => clearTimeout(timer);
  }, [onFinish]);

  return (
    <AnimatePresence>
      {showAnimation && (
        <motion.div
          className="intro-container"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 1 }}
        >
          <motion.img
            src="Icon.jpg"
            alt="Album Vision+ Logo"
            className="logo"
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 1 }}
          />
          <motion.h2
            className="tagline"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2, duration: 0.8 }}
          >
            Welcome to Album Vision+
          </motion.h2>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

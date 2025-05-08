import { motion } from 'framer-motion';
import './IntroAnimation.css';

export default function IntroAnimation() {
  return (
    <motion.div
      className="intro-container"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 1 }}
    >
      <motion.img
        src="/path/to/logo.png"
        alt="Album Vision+ Logo"
        className="logo"
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 1 }}
      />
    </motion.div>
  );
}
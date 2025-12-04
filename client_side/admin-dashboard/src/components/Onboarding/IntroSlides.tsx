import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, Shield, Users, BarChart3, CheckCircle } from 'lucide-react';
import { Button } from '../common/Button';

interface IntroSlidesProps {
  onComplete: () => void;
}

const slides = [
  {
    icon: Shield,
    title: 'Secure Tax Filing System',
    description: 'Manage all your tax filing operations with enterprise-grade security and encryption.',
    color: '#1e5ba8',
  },
  {
    icon: Users,
    title: 'Client Management',
    description: 'Handle multiple clients, track their requests, and manage documents efficiently.',
    color: '#2c4875',
  },
  {
    icon: BarChart3,
    title: 'Real-time Analytics',
    description: 'Monitor filing status, track submissions, and generate comprehensive reports.',
    color: '#3b7fd4',
  },
  {
    icon: CheckCircle,
    title: 'Ready to Get Started?',
    description: 'Everything you need to manage tax filings professionally and efficiently.',
    color: '#10b981',
  },
];

export const IntroSlides: React.FC<IntroSlidesProps> = ({ onComplete }) => {
  const [currentSlide, setCurrentSlide] = useState(0);

  const handleNext = () => {
    if (currentSlide < slides.length - 1) {
      setCurrentSlide(currentSlide + 1);
    } else {
      onComplete();
    }
  };

  const handleSkip = () => {
    onComplete();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-dark via-primary to-primary-light p-4">
      <div className="max-w-2xl w-full">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentSlide}
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.5 }}
            className="bg-white rounded-2xl shadow-2xl p-8 md:p-12 text-center"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
              className="inline-block mb-6"
            >
              {React.createElement(slides[currentSlide].icon, {
                size: 80,
                color: slides[currentSlide].color,
                strokeWidth: 1.5,
              })}
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-3xl md:text-4xl font-bold text-gray-800 mb-4"
            >
              {slides[currentSlide].title}
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-lg text-gray-600 mb-8"
            >
              {slides[currentSlide].description}
            </motion.p>

            <div className="flex justify-center gap-2 mb-8">
              {slides.map((_, index) => (
                <div
                  key={index}
                  className={`h-2 rounded-full transition-all duration-300 ${
                    index === currentSlide ? 'w-8 bg-primary' : 'w-2 bg-gray-300'
                  }`}
                />
              ))}
            </div>

            <div className="flex justify-between items-center">
              <button
                onClick={handleSkip}
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                Skip
              </button>
              
              <Button onClick={handleNext} className="flex items-center gap-2">
                {currentSlide === slides.length - 1 ? "Let's Go" : 'Next'}
                <ChevronRight size={20} />
              </Button>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

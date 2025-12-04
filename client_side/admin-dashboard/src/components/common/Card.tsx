import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ children, className = '', hover = false, onClick }) => {
  const hoverClass = hover ? 'hover-lift cursor-pointer' : '';
  
  return (
    <div
      className={`bg-white rounded-xl shadow-md p-6 animate-fade-in ${hoverClass} ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
};

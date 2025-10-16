// File: web_frontend/src/components/GlassPanel.tsx

import React from 'react';

interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
}

export default function GlassPanel({ children, className }: GlassPanelProps) {
  return (
    <div
      className={`
        bg-white/10          /* This is your rgba(255, 255, 255, 0.1) */
        backdrop-blur-xl     /* This is your blur(20px) - 'xl' is the closest in Tailwind */
        rounded-2xl
        border               /* This is your property */
        border-white/20      /* This is your rgba(255, 255, 255, 0.2) */
        shadow-glass         /* This is our NEW custom shadow from tailwind.config.ts */
        p-6
        ${className} 
      `}
    >
      {children}
    </div>
  );
}
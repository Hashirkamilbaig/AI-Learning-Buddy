// File: web_frontend/src/components/WelcomeScreen.tsx
'use client';
import { useState } from "react";
import GlassPanel from "./GlassPanel";

// Define the props that this component will accept
interface WelcomeScreenProps {
  onStart: (topic: string) => void; // A function that takes the topic string
}

export default function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  const [topic, setTopic] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (topic.trim()) {
      onStart(topic.trim());
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <GlassPanel className="w-full max-w-2xl">
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-2">AI Learning Buddy</h1>
          <p className="text-white/80 mb-8">
            Enter any topic you want to learn, and I'll generate a comprehensive, step-by-step curriculum for you.
          </p>
          <form onSubmit={handleSubmit}>
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Learn Quantum Physics"
              className="w-full p-4 rounded-lg bg-white/10 text-white text-lg border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              className="mt-4 w-full px-6 py-4 rounded-lg font-semibold text-white bg-blue-500/80 hover:bg-blue-500 transition-all disabled:bg-gray-500/50"
              disabled={!topic.trim()}
            >
              Generate Your Learning Plan
            </button>
          </form>
        </div>
      </GlassPanel>
    </div>
  );
}
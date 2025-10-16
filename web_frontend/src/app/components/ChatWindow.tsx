// File: web_frontend/src/components/ChatWindow.tsx
'use client';
import { useState } from "react";
import GlassPanel from "./GlassPanel";

export default function ChatWindow() {
  const [userInput, setUserInput] = useState('');
  const messages = [
    { sender: 'ai', text: 'Thinking... Searching for initial curriculum structure.' },
    { sender: 'ai', text: 'Action: curriculum_planning_tool. Input: Python for Beginners' },
    { sender: 'user', text: 'next' },
    { sender: 'ai', text: 'Great! Moving to Module 2. Researching resources...' }
  ];

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    console.log("User message:", userInput);
    setUserInput('');
  };

  return (
    <GlassPanel className="h-[500px] flex flex-col">
      <h2 className="text-xl font-bold mb-4">Agent Status & Chat</h2>
      
      <div className="flex-grow space-y-4 overflow-y-auto pr-2 text-white/90">
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`px-4 py-2 rounded-lg max-w-sm ${msg.sender === 'user' ? 'bg-blue-600' : 'bg-white/10'}`}>
              <p className="text-base leading-normal">{msg.text}</p> {/* Adjusted font size */}
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleSendMessage} className="mt-4 flex">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type 'next' or 'notes 1'..."
          className="flex-grow p-3 rounded-l-lg bg-white/10 text-white border border-white/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button type="submit" className="bg-blue-600 hover:bg-blue-500 px-5 py-3 rounded-r-lg font-semibold">
          Send
        </button>
      </form>
    </GlassPanel>
  );
}
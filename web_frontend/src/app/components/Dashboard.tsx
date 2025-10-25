// File: web_frontend/src/components/Dashboard.tsx
'use client';
import { useState, useEffect, useRef } from "react";
// Import our new types
import { Plan, Module } from "@/types";

// Import all the components we will need for different states
import WelcomeScreen from "./WelcomeScreen";
import PlanDisplay from "./PlanDisplay";
import ModuleDisplay from "./ModuleDisplay";
import ChatWindow from "./ChatWindow";

type AppStatus = 'idle' | 'loading' | 'ready';

export default function Dashboard() {
  const [status, setStatus] = useState<AppStatus>('idle');
  const [planData, setPlanData] = useState<Plan | null>(null);
  const [logMessages, setLogMessages] = useState<{ sender: 'ai' | 'user', text: string }[]>([]);
  const [activeStep, setActiveStep] = useState<number>(1);
  const chatWindowRef = useRef<HTMLDivElement>(null); // Ref for autoscrolling

  // Effect to automatically scroll the chat window down
  useEffect(() => {
    if (chatWindowRef.current) {
      chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }
  }, [logMessages]);


  // ==================================================================
  // THIS IS THE NEW, LIVE STREAMING FUNCTION
  // ==================================================================
  const handleStartGeneration = async (topic: string) => {
    setStatus('loading');
    setLogMessages([{ sender: 'ai', text: `Initializing agent for topic: "${topic}"...` }]);
    let finalJsonString = '';

    try {
      // 1. Connect to our new streaming API endpoint
      const response = await fetch('/api/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      });

      if (!response.body) {
        throw new Error("Response body is null");
      }

      // 2. Set up a reader to process the stream
      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      // 3. Loop forever to read chunks from the stream
      while (true) {
        const { done, value } = await reader.read();
        if (done) break; // Exit the loop when the stream is finished

        // Decode the chunk of data
        const chunk = decoder.decode(value);
        
        // Process Server-Sent Events (SSE) formatted data
        const lines = chunk.split('\n\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.substring(6);
            
            // Check if the data is our final JSON object
            if (data.trim().startsWith('{') && data.trim().endsWith('}')) {
              finalJsonString = data; // This is the final plan object
            } else {
              // It's a regular log message, so we add it to our state
              setLogMessages(prev => [...prev, { sender: 'ai', text: data }]);
            }
          }
        }
      }

      // 4. Once the stream is finished, parse the final JSON and update the state
      if (finalJsonString) {
        console.log("Stream finished. Parsing final JSON.");
        const parsedPlan: Plan = JSON.parse(finalJsonString);
        setPlanData(parsedPlan);
        setLogMessages(prev => [...prev, { sender: 'ai', text: 'Plan generated successfully! Here is your curriculum.' }]);
        setStatus('ready');
      } else {
        throw new Error("No final JSON plan received from the stream.");
      }

    } catch (error) {
      console.error("Error during stream processing:", error);
      setLogMessages(prev => [...prev, { sender: 'ai', text: `An error occurred: ${error}` }]);
      // Optionally reset to idle state on error:
      // setStatus('idle'); 
    }
  };

  // ----- Conditional Rendering Logic (remains the same) -----

  if (status === 'idle') {
    return <WelcomeScreen onStart={handleStartGeneration} />;
  }

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center p-8">
        <div className="w-full max-w-4xl">
           <ChatWindow messages={logMessages} isLoading={true} />
        </div>
      </div>
    );
  }

  if (status === 'ready' && planData) {
    const activeModule = planData.modules.find(m => m.stepNumber === activeStep);
    
    return (
      <div className="p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div>
            <PlanDisplay plan={planData} activeStep={activeStep} />
          </div>
          <div className="space-y-8 flex-col">
            <div>
              {activeModule && <ModuleDisplay module={activeModule} />}
            </div>
            <div ref={chatWindowRef}>
              <ChatWindow messages={logMessages} isLoading={false} />
            </div>
          </div>
        </div>
      </div>
    );
  }

  return <div>Error: Unknown application state or no plan data.</div>;
}
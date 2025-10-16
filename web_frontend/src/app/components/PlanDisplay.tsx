// File: web_frontend/src/components/PlanDisplay.tsx
import GlassPanel from "./GlassPanel";

export default function PlanDisplay() {
  const modules = [
    { step: 1, title: 'Introduction to Python Basics' },
    { step: 2, title: 'Understanding Data Types and Variables' },
    { step: 3, title: 'Working with Loops and Conditionals' },
    { step: 4, title: 'Introduction to Functions' },
    { step: 5, title: 'Final Project: Simple Calculator' },
  ];

  return (
    <GlassPanel className="h-full space-y-6">
      <div>
        <p className="text-white/80 text-sm mb-2">📍 AI-Generated Curriculum</p>
        {/* MATCHES .trail-title: font-size: 2.5rem; font-weight: bold; */}
        <h1 className="text-[2.5rem] font-bold leading-tight">Learning Plan: Python Beginners</h1>
      </div>

      {/* MATCHES description and stats styles */}
      <p className="text-white/90 leading-relaxed">
        This is a comprehensive, step-by-step curriculum designed to take you from a complete novice to a confident beginner in Python programming, focusing on core concepts and practical application.
      </p>
      
      {/* Module Timeline Section */}
      <div className="bg-white/10 p-4 rounded-xl mt-4">
        <h2 className="text-xl font-bold mb-4">Module Progress</h2>
        <div className="relative pl-4">
          <div className="absolute left-6 top-2 bottom-2 w-0.5 bg-white/20"></div>
          {modules.map((module) => (
            <div key={module.step} className="flex items-center mb-4">
              <div className="z-10 bg-blue-500 w-4 h-4 rounded-full ring-4 ring-white/10"></div>
              {/* MATCHES general text styles */}
              <p className="ml-4 text-white/90">{module.step}. {module.title}</p>
            </div>
          ))}
        </div>
      </div>
    </GlassPanel>
  );
}
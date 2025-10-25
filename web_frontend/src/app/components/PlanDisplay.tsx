// File: web_frontend/src/components/PlanDisplay.tsx
import GlassPanel from "./GlassPanel";
import { Plan } from "@/types"; // Import the Plan type

// Define the props this component expects
interface PlanDisplayProps {
  plan: Plan;
  activeStep: number;
}

export default function PlanDisplay({ plan, activeStep }: PlanDisplayProps) {
  // The component no longer has its own data. It receives it all from props.
  return (
    <GlassPanel className="h-full space-y-6">
      <div>
        <p className="text-white/80 text-sm mb-2">📍 AI-Generated Curriculum</p>
        <h1 className="text-[2.5rem] font-bold leading-tight">{plan.topic}</h1>
      </div>
      
      <p className="text-white/90 leading-relaxed">
        This is a comprehensive, step-by-step curriculum designed to take you from a complete novice to a confident beginner.
      </p>
      
      <div className="bg-white/10 p-4 rounded-xl mt-4">
        <h2 className="text-xl font-bold mb-4">Module Progress</h2>
        <div className="relative pl-4">
          <div className="absolute left-6 top-2 bottom-2 w-0.5 bg-white/20"></div>
          {/* Map over the REAL modules from the plan prop */}
          {plan.modules.map((module) => (
            <div key={module.id} className="flex items-center mb-4">
              {/* Highlight the active step */}
              <div className={`z-10 w-4 h-4 rounded-full ring-4 ring-white/10 ${activeStep === module.stepNumber ? 'bg-blue-500' : 'bg-gray-500'}`}></div>
              <p className={`ml-4 ${activeStep === module.stepNumber ? 'font-bold text-white' : 'text-white/70'}`}>
                {module.stepNumber}. {module.title}
              </p>
            </div>
          ))}
        </div>
      </div>
    </GlassPanel>
  );
}
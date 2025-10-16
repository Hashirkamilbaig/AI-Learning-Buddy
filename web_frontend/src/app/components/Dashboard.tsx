'use client';

import PlanDisplay from "./PlanDisplay";
import ModuleDisplay from "./ModuleDisplay";
import ChatWindow from "./ChatWindow";

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      {/* Main Grid Layout - 50/50 Split */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Panel - Full Curriculum Overview (50% width) */}
        <div>
          <PlanDisplay />
        </div>

        {/* Right Column - Module Details & Chat (50% width, stacked) */}
        <div className="space-y-8 flex-col">
          <div>
            <ModuleDisplay />
          </div>
          <div>
            <ChatWindow />
          </div>
        </div>

      </div>
    </div>
  );
}
// File: web_frontend/src/components/ModuleDisplay.tsx
import GlassPanel from "./GlassPanel";

export default function ModuleDisplay() {
  const currentModule = {
    title: "Module 1: Introduction to Python Basics",
    article: { title: "A Practical Introduction to Python 3", link: "#", reason: "Excellent beginner-friendly overview." },
    video: { title: "Python for Beginners - Full Course", link: "#", reason: "Comprehensive video that covers all the basics." }
  };

  return (
    <GlassPanel className="h-full">
      {/* MATCHES general title styles */}
      <h2 className="text-2xl font-bold mb-4">{currentModule.title}</h2>
      
      <div className="space-y-6"> {/* Increased spacing */}
        <div>
          {/* MATCHES stat-label styles */}
          <h3 className="font-semibold text-lg text-white/70 mb-1">▶️ Recommended Article</h3>
          {/* MATCHES stat-value styles */}
          <a href={currentModule.article.link} className="text-xl font-bold hover:underline text-white">
            {currentModule.article.title}
          </a>
          {/* MATCHES description styles */}
          <p className="text-sm text-white/80 mt-1 leading-normal">{currentModule.article.reason}</p>
        </div>
        <div>
          <h3 className="font-semibold text-lg text-white/70 mb-1">▶️ Recommended Video</h3>
          <a href={currentModule.video.link} className="text-xl font-bold hover:underline text-white">
            {currentModule.video.title}
          </a>
          <p className="text-sm text-white/80 mt-1 leading-normal">{currentModule.video.reason}</p>
        </div>
      </div>

      {/* MATCHES .buttons and .btn styles */}
      <div className="mt-8 flex space-x-4">
        <button className="px-6 py-3 rounded-lg font-semibold text-white bg-blue-500/80 hover:bg-blue-500 transition-all">
          Mark as Complete
        </button>
        <button className="px-6 py-3 rounded-lg font-semibold text-white bg-white/20 hover:bg-white/30 transition-all">
          Get Notes
        </button>
      </div>
    </GlassPanel>
  );
}
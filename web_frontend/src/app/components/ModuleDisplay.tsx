// File: web_frontend/src/components/ModuleDisplay.tsx
import GlassPanel from "./GlassPanel";
import { Module } from "@/types"; // Import the Module type
import Image from 'next/image'; // Import the Next.js Image component for optimization

interface ModuleDisplayProps {
  module: Module;
}

export default function ModuleDisplay({ module }: ModuleDisplayProps) {
  // The videos are in an object, so we get the keys (e.g., "General", "Most Viewed")
  const videoCategories = Object.keys(module.videos);

  return (
    // We add a key to the top-level GlassPanel to force React to re-render it
    // when the module changes. This is important for smooth transitions.
    <GlassPanel key={module.id} className="h-full flex flex-col space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Module {module.stepNumber}: {module.title}</h2>
      </div>

      {/* Article Section */}
      <div className="space-y-2">
        <h3 className="font-semibold text-lg text-white/70">▶️ Recommended Article</h3>
        <a 
          href={module.articleLink} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="text-xl font-bold hover:underline text-white block"
        >
          {module.articleTitle}
        </a>
        <p className="text-sm text-white/80 leading-normal">{module.articleReason}</p>
      </div>
      
      <hr className="border-white/10" />

      {/* Videos Section - This is the major change */}
      <div className="space-y-4">
        <h3 className="font-semibold text-lg text-white/70">🎓 Recommended Videos</h3>
        
        {/* We map over the video categories to display each one */}
        {videoCategories.map(category => {
          const video = module.videos[category];
          if (!video || !video.link) return null; // Don't render if a video is missing

          return (
            <div key={category} className="bg-white/10 p-4 rounded-lg flex gap-4">
              {/* Thumbnail */}
              {video.thumbnail && (
                <div className="w-32 flex-shrink-0">
                  <a href={video.link} target="_blank" rel="noopener noreferrer">
                    <Image
                      src={video.thumbnail}
                      alt={video.title}
                      width={120}
                      height={90}
                      className="rounded-md object-cover"
                    />
                  </a>
                </div>
              )}

              {/* Video Info */}
              <div className="flex-grow">
                <p className="text-xs font-semibold text-blue-300">{category}</p>
                <a 
                  href={video.link} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="font-bold hover:underline text-white block"
                >
                  {video.title}
                </a>
                <p className="text-xs text-white/80 mt-1">{video.reason}</p>
              </div>

              {/* Get Notes Button for each video */}
              <div className="flex-shrink-0 self-center">
                <button className="px-3 py-2 text-sm rounded-lg font-semibold text-white bg-white/10 hover:bg-white/20 transition-all">
                  Get Notes
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Action Buttons at the bottom */}
      <div className="mt-auto pt-6 flex justify-end">
        <button className="px-6 py-3 rounded-lg font-semibold text-white bg-blue-500/80 hover:bg-blue-500 transition-all">
          Mark as Complete & Rate Resources
        </button>
      </div>
    </GlassPanel>
  );
}
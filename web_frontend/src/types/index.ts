// File: web_frontend/src/types/index.ts

// This defines the structure of a single Resource (article or video)
export interface Resource {
  title: string;
  link: string;
  reason: string;
  thumbnail?: string; 
}

// This defines the structure of a single Module in our learning plan
export interface Module {
  id: string;
  stepNumber: number;
  title: string;
  is_complete: boolean;
  articleTitle: string;
  articleReason: string;
  articleLink: string;
  videos: {
    [key: string]: Resource; // e.g., "General", "Most Viewed", etc.
  };
}

// This defines the overall structure of the entire Learning Plan
export interface Plan {
  id: string;
  topic: string;
  modules: Module[];
}
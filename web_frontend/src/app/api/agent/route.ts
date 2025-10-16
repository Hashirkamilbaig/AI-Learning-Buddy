// File: web_frontend/src/app/api/agent/route.ts

import { NextResponse } from 'next/server';

// This function handles POST requests to the /api/agent endpoint
export async function POST(request: Request) {
  try {
    // 1. Parse the incoming request body to get the user's topic
    const body = await request.json();
    const topic = body.topic;

    // A quick check to make sure a topic was provided
    if (!topic) {
      return NextResponse.json({ error: 'Topic is required' }, { status: 400 });
    }

    console.log(`Received topic: ${topic}`);

    // --- THIS IS WHERE WE WILL CALL THE PYTHON SCRIPT IN THE NEXT STEP ---
    // For now, we'll just return a dummy success message.

    const dummyResponse = `This is a placeholder response for the topic: "${topic}". The Python script will be connected here shortly.`;

    // 2. Return a successful response
    return NextResponse.json({ result: dummyResponse });

  } catch (error) {
    console.error('Error in API route:', error);
    // Return a generic error response
    return NextResponse.json({ error: 'An internal server error occurred' }, { status: 500 });
  }
}
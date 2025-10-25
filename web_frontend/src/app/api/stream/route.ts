// File: web_frontend/src/app/api/stream/route.ts

import { spawn } from 'child_process';
import path from 'path';

// This function handles POST requests to the /api/stream endpoint
export async function POST(request: Request) {
  try {
    const body = await request.json();
    const topic = body.topic;

    if (!topic) {
      return new Response('Error: Topic is required', { status: 400 });
    }

    // Create a text encoder to format the data for streaming
    const encoder = new TextEncoder();

    // Create a ReadableStream to send data back to the client
    const stream = new ReadableStream({
      async start(controller) {
        
        // --- SPAWN THE PYTHON SCRIPT ---
        // This is the core logic that runs our agent in a separate process.

        const pythonExecutable = 'python3'; // or 'python'. Use 'python3' for broader compatibility.
        
        // IMPORTANT: The '-u' flag tells Python to run in "unbuffered" mode.
        // This is CRITICAL for real-time streaming. Without it, Python will wait
        // to send output until its internal buffer is full, defeating the purpose of streaming.
        const scriptPath = path.resolve('../agent_backend/agent_brain_optimized.py');

        const agentProcess = spawn(pythonExecutable, ['-u', scriptPath, topic]);

        console.log(`Spawned agent process for topic: "${topic}"`);

        // --- LISTEN FOR OUTPUT FROM THE PYTHON SCRIPT ---

        // 1. Listen for standard output (the logger messages and final JSON)
        agentProcess.stdout.on('data', (data) => {
          const output = data.toString();
          // We queue the data chunk to be sent to the client
          controller.enqueue(encoder.encode(`data: ${output}\n\n`));
        });

        // 2. Listen for standard error (for debugging)
        agentProcess.stderr.on('data', (data) => {
          const errorOutput = data.toString();
          console.error('Agent stderr:', errorOutput);
          // Optionally, you can send errors to the client as well
          // controller.enqueue(encoder.encode(`error: ${errorOutput}\n\n`));
        });

        // 3. Listen for when the process closes
        agentProcess.on('close', (code) => {
          if (code === 0) {
            console.log('Agent process finished successfully.');
            // Signal the end of the stream to the client
            controller.enqueue(encoder.encode('event: done\n\n'));
          } else {
            console.error(`Agent process exited with code ${code}`);
            controller.enqueue(encoder.encode(`error: Process exited with code ${code}\n\n`));
          }
          // Close the stream
          controller.close();
        });
      },
    });

    // Return the stream as the response
    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });

  } catch (error) {
    console.error('Error in stream API route:', error);
    return new Response('An internal server error occurred', { status: 500 });
  }
}
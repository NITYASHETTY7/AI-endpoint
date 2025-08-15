# AI-endpoint
To Run:

Step 1:Set the variable in your current terminal session:

    export GEMINI_API_KEY=your_actual_gemini_api_key_here

Step 2: run the app

    uvicorn src.main:app --reload
  It'll open a new browser

To get the output in terminal itself,start the app and add another terminal and run this,

Without authorization

     curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"prompt":"why sky blue?"}'

With authorization

    curl -X POST "http://127.0.0.1:8000/chat" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer your_JWT(encoder)" \
    -d '{"prompt":"why sky is blue?"}'


Deployment:
Go to FastAPI deployment documentation and choose your deployment type,
I chose Railway since it offers limited free credentials .

Here's the public url of deployment.Register a user first then authorize later login

     https://ai-endpoint-production.up.railway.app/docs

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import json
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for tighter security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to the profile data file
PROFILE_DATA_PATH = "./data/doctor_profile.json"
@app.get("/api/profile")
async def get_profile():
    """Get the doctor's profile data."""
    try:
        if not os.path.exists(PROFILE_DATA_PATH):
            raise HTTPException(status_code=404, detail="Profile data not found")
            
        with open(PROFILE_DATA_PATH, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
        return profile_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid profile data format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read profile: {str(e)}")

@app.put("/api/profile")
async def update_profile(profile: dict):
    """Update the doctor's profile data."""
    try:
        # Basic validation to ensure required fields exist
        required_fields = ["name", "title", "location", "experience", "education", "publications", "contact"]
        for field in required_fields:
            if field not in profile:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(PROFILE_DATA_PATH), exist_ok=True)
        
        # Write the updated profile to file
        with open(PROFILE_DATA_PATH, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)
            
        return profile
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

@app.post("/generate-soap")
async def generate_soap_note(file: UploadFile = File(...)):
    allowed_types = {
        "audio/wav",
        "audio/x-wav",
        "audio/x-pn-wav",
        "audio/wave", 
        "audio/vnd.wave",
        "audio/x-ms-wav",
    }

    if file.content_type not in allowed_types:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported file type: {file.content_type}"}
        )

    # Load static response from file
    response_path = "./data/response.json"
    if not os.path.exists(response_path):
        return JSONResponse(status_code=500, content={"error": "response.json file not found"})

    with open(response_path, "r", encoding="utf-8") as f:
        response_data = json.load(f)

    print("Return response data:", response_data)
    return JSONResponse(content=response_data)

if __name__ == "__main__":
    import nest_asyncio
    from pyngrok import ngrok
    import uvicorn

    ngrok.set_auth_token("2yxhLpLvFgTBfXhLydQ9P8gK77o_4y6bFTYCdfDwzudx2f25i")

    # Allow nested asyncio event loops in Colab
    nest_asyncio.apply()

    # Open an ngrok tunnel to the default uvicorn port (8000)
    # public_url = ngrok.connect(8000)
    public_url = ngrok.connect(
        addr=8000,
        domain="carefully-coherent-fawn.ngrok-free.app",  # <-- reserved in Ngrok dashboard
        # region="ap"  # Optional: choose region like us, eu, ap, etc.
    )

    print("FastAPI server running on:", public_url)

    # Run the FastAPI app
    # uvicorn.run(app, host="0.0.0.0", port=8000)

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
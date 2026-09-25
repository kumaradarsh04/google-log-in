import os

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from google.oauth2 import id_token
from google.auth.transport import requests

# load_dotenv()

app = FastAPI()
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")

app.add_middleware(CORSMiddleware, allow_origins = ["http://localhost:8000"], allow_credentials = True,allow_methods = ["*"], allow_headers = ["*"])

class GoogleLoginRequest(BaseModel):
    credential: str


@app.post("/auth/google")
def google_login(data: GoogleLoginRequest):

    try:

        # Verify the Google ID token
        idinfo = id_token.verify_oauth2_token(
            data.credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        print("==============================")
        print("GOOGLE TOKEN VERIFIED")
        print("==============================")

        print("Google ID:", idinfo["sub"])
        print("Email:", idinfo.get("email"))
        print("Name:", idinfo.get("name"))
        print("Picture:", idinfo.get("picture"))
        print("==============================")

        # Token is valid
        user = {
            "google_id": idinfo["sub"],
            "name": idinfo.get("name"),
            "email": idinfo.get("email"),
            "picture": idinfo.get("picture")
        }

        return {
            "success": True,
            "user": user
        }

    except ValueError:

        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID token"
        )

app.mount(
    "/",
    StaticFiles(directory="static", html=True),
    name="static"
)

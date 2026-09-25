import os
import psycopg
import secrets

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from google.oauth2 import id_token
from google.auth.transport import requests


app = FastAPI()


# ==========================================
# CONFIGURATION
# ==========================================

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
DATABASE_URL = os.environ["DATABSE_URL"]

# ==========================================
# TEMPORARY SESSION STORAGE
# ==========================================
#
# This is only for learning.
#
# session_id -> user
#

# ==========================================
# REQUEST MODEL
# ==========================================
class GoogleLoginRequest(BaseModel):
    credential: str


def get_db_connection():
    return psycopg.connect(DATABASE_URL)

def create_tables():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                google_id TEXT NOT NULL,
                email TEXT,
                name TEXT,
                picture TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                expires_at TIMESTAMPTZ NOT NULL
            )
        """)
        conn.commit()

create_tables()

# ==========================================
# GOOGLE LOGIN
# ==========================================
@app.post("/auth/google")
def google_login(data: GoogleLoginRequest, response: Response):
    try:

        # ----------------------------------
        # 1. Verify Google ID token
        # ----------------------------------
        idinfo = id_token.verify_oauth2_token(
            data.credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )


        # ----------------------------------
        # 2. Extract verified identity
        # ----------------------------------
        user = {
            "google_id": idinfo["sub"],
            "email": idinfo.get("email"),
            "name": idinfo.get("name"),
            "picture": idinfo.get("picture")
        }


        # print("==============================")
        # print("GOOGLE TOKEN VERIFIED")
        # print("==============================")
        # print("Google ID:", user["google_id"])
        # print("Email:", user["email"])
        # print("Name:", user["name"])
        # print("==============================")


        # ----------------------------------
        # 3. Create random session ID
        # ----------------------------------

        session_id = secrets.token_urlsafe(32)


        # ----------------------------------
        # 4. Store session on server
        # ----------------------------------

        # sessions[session_id] = user
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions
                (id, google_id, email, name, picture, expires_at)
                VALUES
                (%s, %s, %s, %s, %s, NOW() + INTERVAL '30 days')
                """, (session_id, user["google_id"], user["email"],
                    user["name"], user["picture"]
                )
            )
        conn.commit()


        # ----------------------------------
        # 5. Send session cookie
        # ----------------------------------

        response.set_cookie(
            key="__Host-session",
            value=session_id,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
            max_age=60 * 60 * 24 * 30
        )


        # ----------------------------------
        # 6. Return success
        # ----------------------------------

        return {"success": True}

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid Google ID token"
        )


# ==========================================
# CHECK CURRENT SESSION
# ==========================================
@app.get("/auth/me")
def get_current_user(request: Request):

    # Get session cookie
    session_id = request.cookies.get("__Host-session")

    # No cookie
    if not session_id:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    # Look up session
    # user = sessions.get(session_id)
    with get_db_connection() as conn:
        row = conn.execute(
            """
            SELECT google_id, email, name, picture
            FROM sessions
            WHERE id = %s
            AND expires_at > NOW()
            """,
            (session_id,)
        ).fetchone()

    if not row:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session"
        )

    # Session doesn't exist
    # if not user:
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Invalid session"
    #     )

    # Session is valid
    return {
        "success": True,
        "user": {
            "google_id": row[0],
            "email": row[1],
            "name": row[2],
            "picture": row[3]
        }
    }

# ==========================================
# LOGOUT
# ==========================================

@app.post("/auth/logout")
def logout(
    request: Request,
    response: Response
):

    session_id = request.cookies.get("__Host-session")


    # Remove server-side session
    if session_id:
        sessions.pop(session_id, None)


    # Delete browser cookie
    response.delete_cookie(
        key="__Host-session",
        path="/"
    )


    return {
        "success": True
    }


# ==========================================
# FRONTEND
# ==========================================
app.mount(
    "/",
    StaticFiles(
        directory="static",
        html=True
    ),
    name="static"
)

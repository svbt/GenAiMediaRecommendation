from fastapi import FastAPI, Query, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from jose import jwt, JWTError
from pydantic import BaseModel
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
import secrets
import hashlib

# Load environment variables
load_dotenv()

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

AMAZON_CLIENT_ID = os.getenv("AMAZON_CLIENT_ID")
AMAZON_CLIENT_SECRET = os.getenv("AMAZON_CLIENT_SECRET")
AMAZON_REDIRECT_URI = os.getenv("AMAZON_REDIRECT_URI")

# --- OAuth URLs and Scopes ---
AUTHORIZATION_BASE_URL = "https://www.amazon.com/ap/oa"
TOKEN_URL = "https://api.amazon.com/auth/o2/token"
PROFILE_URL = "https://api.amazon.com/user/profile"
SCOPES = "profile:user_id"

# --- Dummy Database (Replace with actual database in production) ---
db = {}
state_store = {}  # Temporary in-memory store for state (replace with database in production)

# --- FastAPI App Initialization ---
app = FastAPI()

# --- Pydantic Models ---
class User(BaseModel):
    id: str
    providers: list[str]

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# --- Utility Functions ---
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Amazon OAuth Flow ---
# Example Request: http://localhost:8000/auth/amazon/login
# Response Uri: https://www.amazon.com/ap/oa?response_type=code&client_id=amzn1.application-oa2-client.ef93dc8c5daf4c9bb44950472857a28d&redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fauth%2Famazon%2Fcallback&scope=profile%3Auser_id&state=lNNZNa_LzfU_qrONAYGSaqTTNVk6KflyXZU6N6EJ9GQ
# We will see a screen with "Allow" button and when press it will redirect to /callback
@app.get("/auth/amazon/login")
async def amazon_login(response: Response):
    client = WebApplicationClient(AMAZON_CLIENT_ID)
    
    # Generate a secure state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    state_hash = hashlib.sha256(state.encode()).hexdigest()
    
    # Store state in memory (replace with database in production)
    state_store[state_hash] = state
    
    # Prepare the authorization URL
    authorization_url = client.prepare_request_uri(
        AUTHORIZATION_BASE_URL,
        redirect_uri=AMAZON_REDIRECT_URI,
        scope=SCOPES,
        state=state
    )
    
    # Set state as a cookie
    response.set_cookie(key="oauth_state", value=state_hash, httponly=True, secure=False)  # Set secure=True in production
    
    return RedirectResponse(authorization_url)

# Example Requested : http://localhost:8000/auth/amazon/callback?code=ANgLXITqgtbrKxulKbxA&scope=profile%3Auser_id&state=lqUUn77Bnj6W8MI0_fCIKnfTAbrreXKqHlQtoFhBBXc
# Response: {"access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbXpuMS5hY2NvdW50LkFGU09MTU9FQjYzV1NNWFlIVlU3TkJCTFZUSEEiLCJwcm92aWRlcnMiOlsiYW1hem9uIl0sImV4cCI6MTc2MDY1NTkyN30.y7EPcjyPl1HQyjGcdfd7u0KawPLvj1AZ7QHTukUCCtY","token_type":"bearer"}
@app.get("/auth/amazon/callback", response_model=TokenResponse)
async def amazon_callback(
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None),
    response: Response = None
):
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Amazon login failed with error: {error}"
        )

    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing code or state parameter."
        )

    # Retrieve state from cookie
    state_hash = hashlib.sha256(state.encode()).hexdigest()
    if state_hash not in state_store or state_store[state_hash] != state:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid state parameter (CSRF check failed)."
        )

    # Clear state from store and cookie
    del state_store[state_hash]
    response.set_cookie(key="oauth_state", value="", expires=0)

    # Create OAuth2 session
    amazon_session = OAuth2Session(AMAZON_CLIENT_ID, redirect_uri=AMAZON_REDIRECT_URI)
    
    try:
        # Exchange code for token
        token = amazon_session.fetch_token(
            TOKEN_URL,
            client_secret=AMAZON_CLIENT_SECRET,
            code=code,
            include_client_id=True
        )
        
        # Fetch user profile
        user_profile = amazon_session.get(PROFILE_URL).json()
        user_id = user_profile.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user_id from Amazon profile."
            )
        
        # Database operations
        if user_id not in db:
            db[user_id] = User(id=user_id, providers=["amazon"])
            print(f"[{datetime.now(timezone.utc)}] (Kafka event skipped) Publishing user.login event for new user: {user_id}")
        else:
            if "amazon" not in db[user_id].providers:
                db[user_id].providers.append("amazon")
            print(f"[{datetime.now(timezone.utc)}] (Kafka event skipped) Publishing user.login event for existing user: {user_id}")

        # Create JWT token
        jwt_token = create_access_token({"sub": user_id, "providers": db[user_id].providers})
        
        return {"access_token": jwt_token, "token_type": "bearer"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during Amazon OAuth flow: {str(e)}"
        )

# Example Request : http://localhost:8000/auth/verify?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbXpuMS5hY2NvdW50LkFGU09MTU9FQjYzV1NNWFlIVlU3TkJCTFZUSEEiLCJwcm92aWRlcnMiOlsiYW1hem9uIl0sImV4cCI6MTc2MDY1NTkyN30.y7EPcjyPl1HQyjGcdfd7u0KawPLvj1AZ7QHTukUCCtY
# response: {"message":"Token is valid","payload":{"sub":"amzn1.account.AFSOLMOEB63WSMXYHVU7NBBLVTHA","providers":["amazon"],"exp":1760655927}}
@app.get("/auth/verify")
async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"message": "Token is valid", "payload": payload}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

@app.get("/")
async def root():
    return {"message": "Auth Service is running. Use /auth/amazon/login to start."}
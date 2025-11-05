
import random
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Simple in-memory store for the game state
game_state = {}

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main game page."""
    return templates.TemplateResponse(request, "index.html")

@app.post("/start", response_class=JSONResponse)
async def start_game():
    """Starts a new game by generating a new secret number."""
    secret_number = random.randint(1, 100)
    game_state["secret_number"] = secret_number
    game_state["attempts"] = 0
    return {"message": "New game started. Guess a number between 1 and 100."}

@app.post("/guess", response_class=JSONResponse)
async def make_guess(guess: int = Form(...)):
    """Handles a user's guess."""
    secret_number = game_state.get("secret_number")
    if secret_number is None:
        return {"message": "No game in progress. Please start a new game.", "game_over": True}

    game_state["attempts"] += 1
    attempts = game_state["attempts"]

    if guess < secret_number:
        return {"message": f"Higher! (Attempt {attempts})", "game_over": False}
    elif guess > secret_number:
        return {"message": f"Lower! (Attempt {attempts})", "game_over": False}
    else:
        game_state["secret_number"] = None # End the game
        return {"message": f"Correct! You guessed the number in {attempts} attempts.", "game_over": True}


from fastapi.testclient import TestClient
from app.main import app, game_state

client = TestClient(app)

def test_read_root():
    """Test that the root path returns the HTML page."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"

def test_start_game():
    """Test the /start endpoint."""
    response = client.post("/start")
    assert response.status_code == 200
    assert "secret_number" in game_state
    assert game_state["attempts"] == 0
    assert response.json() == {"message": "New game started. Guess a number between 1 and 100."}

def test_guess_logic():
    """Test the full game flow and guessing logic."""
    # Start a new game and fix the secret number for predictability
    client.post("/start")
    game_state["secret_number"] = 50

    # Test a lower guess
    response = client.post("/guess", data={"guess": "25"})
    assert response.status_code == 200
    json_response = response.json()
    assert "Higher!" in json_response["message"]
    assert json_response["game_over"] is False
    assert game_state["attempts"] == 1

    # Test a higher guess
    response = client.post("/guess", data={"guess": "75"})
    assert response.status_code == 200
    json_response = response.json()
    assert "Lower!" in json_response["message"]
    assert json_response["game_over"] is False
    assert game_state["attempts"] == 2

    # Test a correct guess
    response = client.post("/guess", data={"guess": "50"})
    assert response.status_code == 200
    json_response = response.json()
    assert "Correct!" in json_response["message"]
    assert json_response["game_over"] is True

    # Verify game is over
    assert game_state.get("secret_number") is None

    # Test guessing after game is over
    response = client.post("/guess", data={"guess": "42"})
    assert response.status_code == 200
    assert response.json()["message"] == "No game in progress. Please start a new game."

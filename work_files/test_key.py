import os
from dotenv import load_dotenv
import anthropic
from pathlib import Path

# Load from desktop-app/.env
env_path = Path(__file__).parent.parent / "desktop-app" / ".env"
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

key = os.getenv("ANTHROPIC_API_KEY")

if not key:
    print("Error: ANTHROPIC_API_KEY not found in .env")
    exit(1)

print(f"Key length: {len(key)}")
print(f"Key prefix: {key[:20]}..." if len(key) > 20 else f"Key: {key}")

client = anthropic.Anthropic(api_key=key)

try:
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say hello"}]
    )
    print(f"✓ API Key is valid!")
    print(f"Response: {response.content[0].text}")
except anthropic.AuthenticationError:
    print("✗ API Key is INVALID")
except Exception as e:
    print(f"Error: {e}")
import os
import sys
from pathlib import Path

# Make the repository's source package importable when this file is run directly.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.creator_signup import InfraiClient, SignupRequest, send_signup_verification


def main() -> None:
    recipient = os.environ.get("DEMO_EMAIL_TO")
    if not recipient:
        raise SystemExit("DEMO_EMAIL_TO is required")
    result = send_signup_verification(
        SignupRequest("Mina", recipient, "demo-token", "https://creator.example.com/assets/welcome.zip"),
        InfraiClient(),
    )
    print(f"verification email queued: {result.message_id}")
    print(f"verification link: {result.verification_url}")


if __name__ == "__main__":
    main()

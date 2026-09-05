from src.creator_signup import SignupRequest, SignupResult, build_verification_url, send_signup_verification


class FakeClient:
    def __init__(self):
        self.payload = None

    def send_email(self, payload):
        self.payload = payload
        return {"message_id": "msg_test_1"}


def test_signup_links_email_verification_to_welcome_asset():
    client = FakeClient()
    result = send_signup_verification(
        SignupRequest("Ari", "ari@example.com", "t-42", "https://cdn.example/welcome.zip"), client
    )
    assert isinstance(result, SignupResult)
    assert result.verification_url == build_verification_url("t-42")
    assert result.message_id == "msg_test_1"
    assert client.payload["to"] == "ari@example.com"
    assert result.verification_url in client.payload["html"]
    assert "https://cdn.example/welcome.zip" in client.payload["html"]

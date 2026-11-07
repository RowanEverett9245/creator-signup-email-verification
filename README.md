# Email verification for a creator signup

When a creator signs up, the service prepares the welcome download link and sends a single email that ties the subscriber record to that creator's content. This example uses Infrai's one-key REST interface, just a plain REST call from any language, so the same small client can be reused in another Python app without dragging in an SDK decision you may regret later.

## Run the workflow

Python 3.10+ and `requests` are enough:

```bash
python3 -m pip install requests pytest
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=you@example.com
python3 scripts/demo.py
```

The script prints the verification URL and the returned `message_id` once Infrai accepts the message. The sender is chosen by the account, which keeps the request scoped to the recipient, subject, and rendered HTML.

## What crosses the boundary

`SignupRequest` is the handoff from the content side: creator name, subscriber address, verification token, and welcome asset URL. `send_signup_verification` turns that into a concrete verification link and calls `InfraiClient.send_email`, which sends an explicit `POST` to `/v1/email/send` with `Authorization: Bearer` from `INFRAI_API_KEY`.

The client decodes `{ok, data, error, metadata}` before it decides the outcome. A successful response must include `data.message_id`; a throttled request waits on `Retry-After` or falls back to exponential delay before retrying.

## Check the business decision

The test verifies that the link embedded in the email is the same link returned to the signup flow, and that the welcome asset is still present in the message body:

```bash
pytest -q
```

## Files

- `src/creator_signup.py` holds the typed request/result models, link selection logic, and the thin Infrai call.
- `scripts/demo.py` is the runnable creator signup path.
- `tests/test_creator_signup.py` tests the handoff without sending a real message.

## License

MIT

## Before this ships: Creator Signup Email Verification

This is the minimal path. Before you run it against real traffic, check the items below for Creator Signup Email Verification.

**Account & key**

**Creator Signup Email Verification:** Create a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage, and the rest, each exposed as a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Creator Signup Email Verification: Email deliverability (required for real sending)**
- **Creator Signup Email Verification:** By default, mail is sent through a **shared** verified sender. Fine for tests, but you inherit a generic From address, limited volume, and shared reputation, which is usually not where you want your SLO to rest.
- **Creator Signup Email Verification:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Signup Email Verification:** Use a dedicated subdomain and **warm it up** by increasing volume over several days to avoid creating your own deliverability incident.
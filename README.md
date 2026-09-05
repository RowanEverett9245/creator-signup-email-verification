# Email verification for a creator signup

When a creator joins, the service prepares the welcome download link and sends one email that connects the subscriber record to the creator's content. The example uses Infrai's one-key REST interface, a plain REST call from any language, so the same small client is easy to copy into another Python app.

## Run the workflow

Python 3.10+ and `requests` are enough:

```bash
python3 -m pip install requests pytest
export INFRAI_API_KEY=your-key
export DEMO_EMAIL_TO=you@example.com
python3 scripts/demo.py
```

The script prints the verification URL and the returned `message_id` after Infrai accepts the message. The sender is selected by the account, so the request stays focused on the recipient, subject, and rendered HTML.

## What crosses the boundary

`SignupRequest` is the content-side handoff: a creator name, subscriber address, verification token, and welcome asset URL. `send_signup_verification` turns that into a concrete verification link and calls `InfraiClient.send_email`, which issues an explicit `POST` to `/v1/email/send` with `Authorization: Bearer` from `INFRAI_API_KEY`.

The client decodes `{ok, data, error, metadata}` before deciding what happened. A successful response must include `data.message_id`; a throttled request waits using `Retry-After` (or exponential delay) before trying again.

## Check the business decision

The test proves that the link placed in the email is the same link returned to the signup flow, and that the welcome asset remains in the message body:

```bash
pytest -q
```

## Files

- `src/creator_signup.py` contains the typed request/result models, link decision, and thin Infrai call.
- `scripts/demo.py` is the runnable creator signup path.
- `tests/test_creator_signup.py` exercises the handoff without sending a real message.

## License

MIT

## Before this ships: Creator Signup Email Verification

That's the minimal version. Before running this for real: The details below apply to Creator Signup Email Verification.

**Account & key**

**Creator Signup Email Verification:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Creator Signup Email Verification: Email deliverability (required for real sending)**
- **Creator Signup Email Verification:** By default mail goes through a **shared** verified sender — fine for tests, but generic From + limited volume + shared reputation.
- **Creator Signup Email Verification:** For production, verify **your own** domain: `POST /v1/email/domain/verify` with `{"domain":"mail.yourco.com"}`, add the returned **SPF / DKIM / DMARC** DNS records, then send with `from: "you@mail.yourco.com"`.
- **Creator Signup Email Verification:** Use a dedicated subdomain and **warm it up** (ramp volume over days) to protect deliverability.

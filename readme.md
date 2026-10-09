# Stage 1: "hi" bot

Replies "hi" to every WhatsApp message. Proves the plumbing works before we add an LLM (stage 2)
and Drive file search (stage 3).

## Setup
1. developers.facebook.com -> create an app (type: Business) -> add the **WhatsApp** product.
2. WhatsApp -> API Setup: copy the **temporary access token** and the **Phone number ID**.
   Add your own phone number as a test recipient and verify it. (Temporary tokens expire in ~24h;
   a permanent one comes from a System User later.)
3. `pip install -r requirements.txt`, `cp .env.example .env`, fill it in.
4. `uvicorn app:app --port 8000`
5. Expose it over HTTPS: `ngrok http 8000` (or `cloudflared tunnel --url http://localhost:8000`).
6. WhatsApp -> Configuration -> Webhook: callback URL `https://<your-tunnel>/webhook`,
   verify token = your `VERIFY_TOKEN`; click Verify and save, then subscribe to the **messages** field.
7. Send any message from your phone to the test number. You should get "hi" back.

## If it doesn't reply
- Check the uvicorn log for "WhatsApp error": 401 = expired token, 131030 = recipient not on the allowed list.
- No log line at all = webhook not reached: recheck the tunnel URL and that **messages** is subscribed.
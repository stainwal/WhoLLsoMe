"""Embed passages into passage_embeddings (Day 16, 12 Oct 2026). Baseline: Plan section 4.4, experiment 2.

    .venv/bin/python backend/embed.py [--limit N] [--tpm 10000] [--rpm 3]

Embeds each passage's verbatim text plus its plain version with Voyage voyage-4-lite (1024 dimensions,
input_type 'document'), stored under setup 'voyage-4-lite/text+plain'. Resumable: passages already
embedded for the setup are skipped, so an interrupted run picks up where it stopped. Paced to stay under
the account's rate limits (defaults: Voyage's limits for an account with no payment method); a 429
backs off and retries. Reads DATABASE_URL and VOYAGE_API_KEY from .env.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import load  # noqa: E402  (connect, .env)

MODEL, DIM = "voyage-4-lite", 1024
SETUP = f"{MODEL}/text+plain"
URL = "https://api.voyageai.com/v1/embeddings"


def embed_text(display_text, plain):
    return f"{display_text}\n\n{plain}"


def call(texts, key):
    body = json.dumps({"input": texts, "model": MODEL, "input_type": "document", "output_dimension": DIM}).encode()
    req = urllib.request.Request(URL, body, {"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                out = json.load(r)
            return [d["embedding"] for d in sorted(out["data"], key=lambda d: d["index"])], out["usage"]["total_tokens"]
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 7:
                wait = 20 * (attempt + 1)
                print(f"  HTTP {e.code}, waiting {wait}s", flush=True)
                time.sleep(wait)
                continue
            sys.exit(f"Voyage error {e.code}: {e.read().decode()[:300]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="embed at most N passages (a trial run)")
    ap.add_argument("--tpm", type=int, default=10_000, help="tokens per minute to stay under")
    ap.add_argument("--rpm", type=int, default=3, help="requests per minute to stay under")
    a = ap.parse_args()
    load.load_dotenv(load.ROOT / ".env")
    key = os.environ.get("VOYAGE_API_KEY")
    if not key:
        sys.exit("VOYAGE_API_KEY is not set in .env")

    with load.connect() as db:
        todo = db.execute("""select pid, display_text, plain from passages p
                             where not exists (select 1 from passage_embeddings e where e.pid = p.pid and e.setup = %s)
                             order by pid""", (SETUP,)).fetchall()
        if a.limit:
            todo = todo[:a.limit]
        print(f"{SETUP}: {len(todo):,} passages to embed", flush=True)
        budget = int(a.tpm * 0.85)          # a request's tokens, estimated at 4 characters each, kept under this
        sent, total, done, i = deque(), 0, 0, 0   # sent: (time, tokens) of requests in the last minute
        while i < len(todo):
            batch, est = [], 0
            while i < len(todo) and len(batch) < 1000:
                t = embed_text(todo[i][1], todo[i][2])
                if batch and est + len(t) // 4 > budget:
                    break
                batch.append((todo[i][0], t)); est += len(t) // 4; i += 1
            # wait until the last minute's requests leave room for this one
            while True:
                now = time.time()
                while sent and now - sent[0][0] > 61:
                    sent.popleft()
                if not sent or (len(sent) < a.rpm and sum(n for _, n in sent) + est <= a.tpm):
                    break
                time.sleep(1)
            vecs, used = call([t for _, t in batch], key)
            sent.append((time.time(), used))
            with db.cursor() as cur:
                cur.executemany("insert into passage_embeddings (pid, setup, embedding) values (%s, %s, %s::vector) "
                                "on conflict (pid, setup) do update set embedding = excluded.embedding",
                                [(pid, SETUP, str(v)) for (pid, _), v in zip(batch, vecs)])
            db.commit()
            total += used; done += len(batch)
            print(f"  {done:,}/{len(todo):,} passages, {total:,} tokens", flush=True)
    print(f"done: {done:,} passages embedded, {total:,} tokens billed against the free allowance")


if __name__ == "__main__":
    main()

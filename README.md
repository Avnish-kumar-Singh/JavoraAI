# JavaMentorAI

A Java mentoring agent: a LangGraph pipeline that routes each question to the
tool best suited to answer it — the model itself, your indexed notes (RAG), a
live web lookup, a DSA solver, a code reviewer, or the Java compiler.

Now shipped with a web UI, accounts, and persisted history.

---

## Running it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# set JWT_SECRET to a real value:
python -c "import secrets; print(secrets.token_urlsafe(48))"

ollama serve
ollama pull qwen2.5
ollama pull nomic-embed-text

python run_api.py
```

Open <http://localhost:8000>. The CLI (`python main.py`) still works.

---

## Part 1 — Response time

Six things were making responses slow. In rough order of impact:

### 1. `max_tokens` was never reaching the model

`LLMService.invoke` did this:

```python
llm = self.llm.bind(options={"num_predict": max_tokens})
```

`langchain-ollama` builds the `options` payload itself from its own fields, so
this nested key was dropped on the floor. Every generation ran to Ollama's
default limit regardless of what `ResponsePlanner` decided. `num_predict` is
now passed on the client constructor, where it is actually honoured.

### 2. Nothing streamed

The old flow blocked until the entire answer was generated. The API now has
`POST /api/chat/stream` (SSE) and the UI renders tokens as they arrive, so the
first words appear in about a second instead of after the full generation.
This is the single biggest change to *perceived* speed.

### 3. Every tool was constructed on startup

`ToolRegistry.__init__` eagerly built all six tools. That chain opened the
Chroma store, the Ollama embedding client, the DuckDuckGo service, and four
separate `ChatOllama` clients — on every process start, for a user who might
only ask one plain question. Tools are now built lazily on first use, and the
LLM client, retriever, agents and compiled graph are process-wide singletons
(`app/core/container.py`).

### 4. The planner was routing ordinary questions down slow paths

Keyword matching used plain substring checks against the whole query:

| Query | Old route | Why |
|---|---|---|
| "How do I create a **new** object in Java?" | web search | `"new"` was a web keyword |
| "How does the JVM **run** bytecode?" | Java compiler | `"run"` was a compiler keyword |
| almost anything containing "java" | RAG | `"java"` was a RAG keyword |

So a question the model knows cold was paying a network round trip, or a
vector query, or being handed to a compiler with no code in it. Matching is now
word-boundary based; web search needs a recency signal *and* a version signal;
the compiler and reviewer require code to actually be present; and RAG needs a
real domain term rather than the word "java".

### 5. ~1,400 tokens of boilerplate on every prompt

The prompt template sent a long block of numbered rules with each turn — pure
prefill latency, repeated every message. Condensed to the rules that change the
output: about 774 characters of fixed text now, down from ~3,400.

### 6. No caching

Repeat questions re-ran the whole generation. There is now a TTL + LRU cache
keyed on the normalized question plus retrieved context
(`app/core/cache.py`), applied to both the LLM and web paths.

**Also fixed along the way:** `keep_alive` is set so Ollama stops evicting the
model between questions; `num_ctx` is pinned to 4096; the model is warmed at
API startup; token budgets dropped from 1000/1800/2500 to 600/1100/1800; and
`CHROMA_PATH` in `.env` pointed at `./data/chroma` while the code hardcoded
`data/chroma_db`, so the setting had never taken effect — both now agree.

---

## Part 2 — Accounts

`POST /api/auth/register` creates an account and signs the user straight in.
`POST /api/auth/login` accepts either the username or the email address.
`GET /api/auth/me` restores a session from a stored token.

Passwords are hashed with PBKDF2-HMAC-SHA256 (240k iterations, per-user salt)
from the standard library, so there is no native build dependency. Login
returns the same error for an unknown user and a wrong password, so the
endpoint doesn't leak which usernames exist. Auth is a bearer JWT.

## Part 3 — Persisted history

Two tables: `chat_sessions` groups a conversation, `query_history` stores each
question with its answer, the tool that handled it, status and latency.

| Endpoint | Purpose |
|---|---|
| `GET /api/history` | All past questions, newest first; `?q=` full-text, `?tool=` filter, paged |
| `GET /api/history/sessions` | Chat list for the sidebar |
| `GET /api/history/sessions/{id}` | Restore a full conversation |
| `DELETE /api/history/sessions/{id}` | Delete a chat |
| `DELETE /api/history/{id}` | Delete one entry |

History is also read *back into* the model: reopening a chat and asking
"optimize that" still resolves, because the last few turns are replayed into
the prompt.

SQLite by default (`data/javamentor.db`); point `DATABASE_URL` at Postgres to
switch.

## Part 4 — UI

`frontend/index.html`, served by FastAPI at `/` so there is no CORS setup and
nothing to build. Sign-in and account creation, streaming answers, a left rail
with your chats and a search box over everything you've ever asked, and a chip
on each answer showing which tool handled it and how long it took. Responsive,
keyboard accessible, follows your system light/dark setting.

---

## Layout

```
app/
  api/            FastAPI: auth, chat (blocking + SSE), history, ORM, JWT
  core/           container.py (singletons), cache.py, enums
  agents/         planner (routing), answer (generation)
  graph/          LangGraph state + compiled graph
  nodes/          planner -> router -> tool_executor
  tools/          llm, rag, web, dsa, review, java_compiler
  rag/            chroma, embeddings, retriever, indexer
  synthesis/      prompt + context builders
frontend/         single-file UI
run_api.py        launcher
main.py           CLI
```

## Worth doing next

- The compiler tool runs untrusted Java through `subprocess` with no sandbox.
  Fine locally, unsafe the moment this is exposed to anyone else — it needs a
  container with no network and a CPU/memory cap before deployment.
- `JWT_SECRET` must be changed before deploying; tokens are signed with it.
- The response cache is per-process, so it won't be shared across workers if
  you run uvicorn with `--workers > 1`. Move it to Redis at that point.
- There are ~20 `test_*.py` scripts at the repo root that are manual scripts
  rather than assertions. Worth converting to pytest so the routing table in
  particular is protected.

---

## Pushing to GitHub

```bash
cd JavaMentorAI
git init
git add .
git commit -m "Initial commit: JavaMentorAI"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

`.env`, `data/chroma_db/`, `.venv/`, and Terraform state/vars are gitignored —
double check `git status` before the first commit if you've been running the
app locally, so nothing local leaks in.

## Local, full-stack run (Docker Compose)

Runs the API, Postgres, and Ollama together:

```bash
cp .env.example .env          # set a real JWT_SECRET and POSTGRES_PASSWORD
docker compose up --build
```

Then pull the models into the Ollama container once, and build the RAG index:

```bash
docker exec javamentor-ollama ollama pull qwen2.5
docker exec javamentor-ollama ollama pull nomic-embed-text
docker exec javamentor-api python scripts/reindex.py
```

Open <http://localhost:8000>.

## Deploying to AWS

`aws/` has a Terraform scaffold (ECS Fargate + ALB + RDS Postgres + ECR) and
`aws/AWS_DEPLOYMENT_PLAN.md` / `aws/README.md` describe it in more detail.

1. Install the AWS CLI, Docker, and Terraform, and run `aws configure`.
2. `cd aws/terraform && cp terraform.tfvars.example terraform.tfvars` and fill
   in real values — a strong `db_password`, a strong `jwt_secret`
   (`python -c "import secrets;print(secrets.token_urlsafe(48))"`), and where
   `llm_base_url` should point (Ollama needs to be reachable from ECS — a
   small EC2/Fargate Ollama service or another private endpoint).
3. `terraform init && terraform plan && terraform apply`.
4. Build and push the image to the ECR repo Terraform created, then force a
   new ECS deployment (or just run `deploy-aws.ps1` on Windows, which does
   steps 3–4 for you and generates fresh secrets into `terraform.tfvars` if
   one doesn't already exist).
5. Once the ALB is up, run the reindex step once against the running task
   (`aws ecs execute-command ... -- python scripts/reindex.py`, or bake it
   into a one-off task) so `/api/chat` has RAG content from the first request.

Terraform state is kept locally by default — for a real team setup, move it
to an S3 backend with DynamoDB locking before anyone else touches this stack.

### If you've already run this project before pulling this cleanup

Older working copies of this repo had a real Postgres password and JWT secret
committed to disk (`aws/terraform/terraform.tfvars` and a Copilot session
file). Those files are now excluded from git and were not included in this
cleaned copy, but if you'd already pushed or deployed with those values,
rotate the DB password and JWT secret before going further.

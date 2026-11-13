# Subscription teacher transport

The teacher uses installed Hermes's supported
`resolve_provider_client('openai-codex', model='gpt-6-astra')` route. It requests
no tools or reasoning-effort override and supplies only the registered JSON
envelope and fixed instruction. Normal provider-managed auth adoption/refresh
is allowed. The experiment never manually reads or copies credentials and never
changes global configuration.

`data/validation/hermes-source-pins.json` records the installed checkout commit
and SHA-256 values of the actual adapter, request-bypass, auth and bootstrap
sources. File hashes distinguish working source from the repository commit.
No credential files are included.

Hermes translates chat-shaped input to streaming Responses arguments. Our capture
merges the SDK bypass's `extra_body` fields into the shaped body, excludes headers
and retains visible text/refusal deltas plus terminal response identity/status
and numeric usage. Reasoning
token counts may be recorded. Reasoning content is excluded. Actual server model
identity is an observation, separate from the requested model name.

The route must be the default HTTPS ChatGPT Codex endpoint. Custom routes and
proxy environment settings fail closed. There is no provider/model fallback or
automatic inference retry. The no-progress limit is 120 seconds and an independent
process alarm bounds duration to 600 seconds. Cancellation cannot prove remote
work has stopped. There is no enforced output-token cap on this transport.

A failed initial transport attempt exposed Hermes's supported bootstrap re-exec.
Bootstrap now completes before output creation. The failed request is retained,
and a replacement smoke uses a fresh directory. A smoke is transport evidence,
not a scientific trial. Subscription usage does not imply API-dollar charges or
provider equivalence.

For reproduction, activate an existing compatible Hermes Python environment,
make its source importable, then run from this experiment directory:

```sh
python -m unittest test_oauth_teacher.py
python oauth_teacher.py --prompt-fixture FIXTURE.json --outdir NEW_OUTPUT
```

The CLI is a one-shot call. Use a transport-only fixture until registration is
published. Offline mocks need Hermes dependencies but do not resolve credentials.
Recorded mock command: `python -m unittest test_oauth_teacher.py`. The original
operator environment used the existing Hermes venv. No installation was needed.

Official documentation establishes the broader authentication and event concepts:
[Codex authentication](https://developers.openai.com/codex/auth/) and
[streaming Responses](https://developers.openai.com/api/docs/guides/streaming-responses).
The installed source and captured wire records establish this experiment's
specific Hermes behavior. These API event docs do not establish subscription
endpoint equivalence or billing.

The second transport-only smoke completed successfully. Its terminal response
reported model `gpt-6-astra`, status `completed`, 89 input tokens and 146 output
tokens, with zero cached and reasoning tokens. Sanitized request, shaped wire,
visible response and terminal metadata are retained in `data/auth-smoke-02/`.
The first attempt made no inference call. This establishes the observed local
authentication route and response format, not scientific task performance.

Failed streams retain the observed visible deltas. Error records expose only the
exception class and a numeric HTTP status when available, with elapsed seconds.
They exclude exception text. The `terminal-events.json` filename also contains
these allowed visible events.

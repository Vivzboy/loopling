---
name: ai-media
description: >
  Generate AI IMAGES and AI VIDEO via PiAPI (one key, many models). OPTIONAL + PAID — needs a
  PiAPI key and costs real money per generation. Trigger when the bot needs to create (not
  fetch) an image or short video. Read the cost-control hard rule before generating.
---

# ai-media — AI image + video generation (PiAPI)

**Optional, key-gated, and PAID.** [PiAPI](https://piapi.ai) is a unified API that wraps many
generation models behind one key — image models (GPT-image, Flux) and video models (e.g.
Seedance). One `PIAPI_KEY` covers both.

## Setup (the key pattern)
On setup, **ask the user for their PiAPI key** (<https://piapi.ai>) and store it in
`~/.claude/secrets.local` as `PIAPI_KEY`. The bot reads it from there.

## ⚠️ Cost-control hard rule (read this)
Generation costs real money (images ~cents, **video ~$2–3/clip**). Therefore:
- **Never generate without the user's go-ahead** if it's non-trivial spend (always for video).
- **Never auto-retry / resubmit / run parallel attempts.** If a job fails, report it and wait —
  every submission is billed whether it succeeds or not.
- For anything expensive, show the prompt first, get approval, then submit one job.

## Image generation
```bash
curl -s -X POST https://api.piapi.ai/v1/images/generations \
  -H "Authorization: Bearer $PIAPI_KEY" -H "Content-Type: application/json" \
  -d '{"model":"gpt-image-1","prompt":"<prompt>","size":"1024x1024"}'
```
- `gpt-image-1` for quality / instruction-following; `Qubico/flux1-schnell` for cheap/fast (~$0.002/img).
- To lock a subject's identity across images, use an image-edit/reference flow (pass a reference image).

## Video generation (async task API)
```bash
# Submit
curl -s -X POST https://api.piapi.ai/api/v1/task \
  -H "X-API-Key: $PIAPI_KEY" -H "Content-Type: application/json" \
  -d '{"model":"<video-model>","task_type":"...","input":{"prompt":"<prompt>", "image_urls":["<ref?>"]}}'
# Poll
curl -s https://api.piapi.ai/api/v1/task/<task_id> -H "X-API-Key: $PIAPI_KEY"
```
- Video jobs are **async + slow** (5–15 min). Submit, then poll the task id until done.
- **Reference image URLs must be reachable from PiAPI's processing servers** (some are in China):
  jsDelivr (`cdn.jsdelivr.net/gh/...`) and Pexels CDN work; GitHub raw / catbox / Telegram URLs
  are often blocked. Host refs somewhere broadly reachable.

## Cheaper / free alternatives first
Before paying to generate: can a **stock** photo/video (`stock-images`) or a **DuckDuckGo
Images** real photo (`web-search`) do the job? Generate only when you actually need something
that doesn't exist.

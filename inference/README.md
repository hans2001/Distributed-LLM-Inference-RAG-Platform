# Inference Service

This project uses the official `vllm/vllm-openai` image to provide an OpenAI-compatible API.
The service is configured in `docker-compose.yml` and exposes port 8001.

Health check is performed by requesting `/v1/models`.

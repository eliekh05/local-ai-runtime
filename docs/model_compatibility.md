# Model Compatibility

## Auto-detected architectures

The detector reads GGUF metadata and maps architectures to chat templates:

| Architecture | Default Template | Example Models |
|-------------|-----------------|----------------|
| llama | llama3 | Llama 3.x, CodeLlama |
| mistral / mixtral | mistral | Mistral 7B, Mixtral 8x7B |
| phi / phi3 | chatml | Phi-3, Phi-3.5 |
| qwen / qwen2 | chatml | Qwen2, Qwen2.5 |
| gemma / gemma2 | chatml | Gemma 2 |
| command-r | chatml | Command R |
| deepseek | chatml | DeepSeek |
| falcon | chatml | Falcon |
| yi | chatml | Yi |
| codellama | llama3 | CodeLlama |

## How to test a model

1. Drop `.gguf` file in `models/`
2. Run `GET /models/detect` — auto-detects architecture, template, context length
3. Run `GET /config/backends` — verify your backend is available
4. `PUT /config` with `backend_type` and `model_file`
5. Send a test message via `POST /chat`

## Notes

- GGUF format required for local backends (llama-cpp, ollama)
- API backends (OpenAI, Anthropic, Gemini) accept any model they support — no GGUF needed
- Chat template `auto` picks the best template from model metadata automatically
- Context length auto-detected from GGUF header when available

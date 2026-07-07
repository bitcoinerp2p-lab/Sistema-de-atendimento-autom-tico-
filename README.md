# ORION OS V6 — Fase 1 (MVP Estrutural)

Sistema SaaS multiagente para operar a venda do produto INSUGLIN via WhatsApp,
com agentes de IA em papel estritamente analítico/consultivo — nunca
financeiro, nunca de voz — e supervisão humana obrigatória em qualquer ação
de negócio.

Este repositório contém a **Fase 1** conforme o plano em
`~/.claude/plans/elegant-cuddling-floyd.md`: um ambiente rodável localmente
via Docker Compose, com o ORION OS Core Engine (FastAPI), Postgres, Redis,
Qdrant, n8n e Evolution API.

## Decisões de arquitetura (conflitos resolvidos com o Thiago)

| Item | Decisão |
|---|---|
| PHANTOM | Motor de insights restrito — nunca fala com o lead, só gera recomendações para um operador humano. |
| VORTEX | Puramente analítico — nunca executa nada em plataformas de tráfego pago (ainda não implementado nesta fase). |
| Funil oficial | O conteúdo Leadzy/MSA Turbo é a base inicial do Funil Oficial Ativo (upload dinâmico). |
| OpenClaw | Abstraído atrás de `AgentRuntimePort` (`backend/app/core/agent_runtime.py`). A Fase 1 usa `AnthropicAgentRuntime`, chamando a API da Anthropic diretamente. Trocar de adapter quando o OpenClaw estiver disponível. |

## Subindo localmente

```bash
cd infra
cp .env.example .env
# edite .env e preencha ao menos ANTHROPIC_API_KEY

docker compose up -d --build
```

Depois de subir, rode as migrations dentro do container do core-engine:

```bash
docker compose exec core-engine alembic upgrade head
```

Importe o workflow de exemplo do n8n (`infra/n8n/workflows/whatsapp_ingress.json`)
pela UI do n8n em `http://localhost:5678` (Workflows → Import from File).

## Verificação

1. **Sobe sem erro**: `docker compose up -d` deve subir postgres, redis,
   qdrant, n8n, evolution-api e core-engine.
2. **Webhook do WhatsApp**:
   ```bash
   curl -X POST http://localhost:8000/webhook/evolution/whatsapp/ingress \
     -H "Content-Type: application/json" \
     -d '{"event":"messages.upsert","instance":"orion_test","data":{"key":{"remoteJid":"5511999999999@s.whatsapp.net","fromMe":false,"id":"MSG1"},"messageType":"conversation","message":{"conversation":"Olá, quero saber mais"},"messageTimestamp":1788374700}}'
   ```
   Deve retornar `{"status": "accepted", ...}` e criar um registro em `leads`
   e `events`.
3. **Upload do Funil Oficial Ativo**:
   ```bash
   curl -X POST http://localhost:8000/api/v6/core/funnel/upload-document \
     -F "file=@caminho/para/funil_leadzy.md"
   ```
   Deve retornar `chunks_generated > 0` e `status: INDEXED_SUCCESSFULLY`.
4. **Testes automatizados** (dentro do container ou de um venv local):
   ```bash
   cd backend
   pip install -r requirements.txt
   pytest
   ```
   Cobre o algoritmo de reputação (penalidades, recuperação, estados
   Green/Yellow/Amber/Red), o parsing dos contratos de evento (`EventIn`,
   `FunnelUploadMetadata`, `AbandonmentAlertIn`), o classificador de objeções
   e o parsing da saída estruturada do PHANTOM.

   > Nota: estes testes foram escritos mas **não foram executados nesta
   > sessão** — a instalação de dependências localmente foi evitada por
   > restrição de espaço em disco na máquina (~2% livre). Rode `pytest`
   > antes de confiar no código em produção.

## O que falta para produção (fora do escopo da Fase 1)

- Frontend React/TypeScript (Painel ORION) — Fase 2/3.
- Os outros 13 agentes constitucionais (só PHANTOM insight-only e o
  Mapeamento de Objeções existem nesta fase).
- Enforcement automático do sistema de reputação em runtime (hoje são
  funções puras, sem hook de bloqueio real).
- VoIP/Asterisk/Twilio, transcrição de áudio (Whisper), OCR de comprovantes.
- Deploy real na VPS Hostinger, TLS/Traefik, backups para S3, failover.
- Troca do `AnthropicAgentRuntime` por um adapter real do OpenClaw, quando
  (e se) esse runtime existir e você tiver acesso a ele.
- Pareamento de um número de WhatsApp real na Evolution API (hoje o serviço
  sobe, mas sem instância pareada).
- Embeddings reais: `backend/app/services/embeddings.py` usa um placeholder
  determinístico via hash — não é semanticamente significativo. Trocar por
  um modelo de embedding de verdade antes de usar com leads reais.

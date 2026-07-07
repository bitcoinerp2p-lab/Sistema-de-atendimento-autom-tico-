"""Interface de execução de agentes (`AgentRuntimePort`) e adapter concreto.

Todos os documentos de especificação assumem "OpenClaw" como motor de
execução de agentes (runtime gRPC/REST para LLMs). Não há evidência de que
esse seja um produto publicamente existente, então esta camada abstrai a
execução atrás de uma porta (`AgentRuntimePort`): a Fase 1 implementa
`AnthropicAgentRuntime`, que chama a API da Anthropic diretamente. Quando o
OpenClaw estiver disponível de fato, basta escrever um novo adapter que
implemente a mesma porta — nenhum código de agente precisa mudar.

O formato de `AgentInferenceResult` espelha deliberadamente o contrato
protobuf `AgentInferenceResponse` descrito na Especificação V2 Complementar
(secao 7.1), para que uma futura migração para OpenClaw via gRPC seja só
uma troca de adapter.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from anthropic import AsyncAnthropic

from app.core.config import get_settings

settings = get_settings()


@dataclass
class AgentInferenceResult:
    generated_text_output: str
    tool_call_requested: bool = False
    tool_name: str | None = None
    tool_arguments_json: str | None = None
    token_usage_count: int = 0


class AgentRuntimePort(ABC):
    """Porta que qualquer motor de execução de agentes deve implementar."""

    @abstractmethod
    async def run(
        self,
        *,
        agent_identifier: str,
        system_prompt: str,
        context_chunks: list[str],
        user_message: str,
        temperature: float = 1.0,
    ) -> AgentInferenceResult:
        raise NotImplementedError


class AnthropicAgentRuntime(AgentRuntimePort):
    """Implementação Fase 1: chama a API da Anthropic diretamente.

    Isolamento de segurança minimo desta fase (a sandbox completa de
    processo/egress descrita na Especificação V1 secao 2.2 fica para uma
    fase posterior, quando o OpenClaw ou equivalente estiver em produção):
    o prompt de sistema e o input do usuário são sempre enviados em blocos
    separados, nunca concatenados livremente, para reduzir o risco de
    injeção de prompt indireta vinda de mensagens de leads.
    """

    def __init__(self) -> None:
        if not settings.anthropic_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY não configurada — defina no .env antes de "
                "usar o AnthropicAgentRuntime."
            )
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def run(
        self,
        *,
        agent_identifier: str,
        system_prompt: str,
        context_chunks: list[str],
        user_message: str,
        temperature: float = 1.0,
    ) -> AgentInferenceResult:
        context_block = "\n\n".join(
            f"<context_chunk index=\"{i}\">\n{chunk}\n</context_chunk>"
            for i, chunk in enumerate(context_chunks)
        )
        user_block = (
            f"{context_block}\n\n<user_input>\n{user_message}\n</user_input>"
            if context_block
            else f"<user_input>\n{user_message}\n</user_input>"
        )

        response = await self._client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1024,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_block}],
        )

        text = "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        )
        usage = response.usage
        token_usage_count = (usage.input_tokens or 0) + (usage.output_tokens or 0)

        return AgentInferenceResult(
            generated_text_output=text,
            token_usage_count=token_usage_count,
        )


class FakeAgentRuntime(AgentRuntimePort):
    """Runtime determinístico para testes — não faz nenhuma chamada externa."""

    def __init__(self, canned_response: str = "resposta de teste") -> None:
        self._canned_response = canned_response

    async def run(
        self,
        *,
        agent_identifier: str,
        system_prompt: str,
        context_chunks: list[str],
        user_message: str,
        temperature: float = 1.0,
    ) -> AgentInferenceResult:
        return AgentInferenceResult(
            generated_text_output=self._canned_response,
            token_usage_count=0,
        )

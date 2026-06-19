# AI Banking Sales Agent — Agente de IA Omnicanal para Vendas PJ

> **Contexto:** Projeto desenvolvido em 2024–2025 durante atuação em fintech de serviços bancários. O agente realizava prospecção ativa de empresas (CNPJs) via WhatsApp e voz, conduzindo triagem automatizada e entregando leads qualificados para a equipe comercial fechar as vendas na plataforma bancária.

---

## O Problema Real

Uma corretora de soluções bancárias PJ precisava escalar prospecção ativa sem escalar headcount. Os desafios:

- **Base fria e grande:** mailing de CNPJs filtrados por CNAE (Receita Federal), sem histórico de relacionamento
- **Baixo engajamento inicial:** taxa de resposta no WhatsApp ativo em torno de 22–31%
- **Gargalo humano:** consultores gastavam tempo em triagem em vez de fechar negócios
- **Múltiplos produtos:** conta PJ, crédito capital de giro, maquininha, antecipação de recebíveis, seguros

## A Solução: Funil Omnicanal com Agente de IA

Um agente treinado via **ChatGPT Custom** operando em dois canais simultâneos:

1. **WhatsApp ativo** (disparo em massa via Twilio) - triagem conversacional - handoff humano
2. **URA de voz** (plataforma Callix) - qualificação por botão - handoff humano

O humano só entrava quando o lead estava qualificado e pronto para cadastrar a venda.

---

## Métricas do Funil (Dados Reais)

| Mês | Canal | Base/dia | Taxa Atendimento | Taxa Lead | Contas Abertas |
|---|---|---|---|---|---|
| Set/2025 | URA | ~46k | ~8.2% | ~24.7% | ~11.2/dia |
| Out/2025 | URA | ~16k | ~30.9% | ~30.5% | ~220/mês |
| Nov/2025 | URA | ~29.7k | ~22.6% | ~34.2% | ~280/mês |
| Jul/2025 | Discadora | ~3.1k | ~8.2% | ~4.7% | ~8/dia |

## Modelo de Negócio (agente de IA)

Receita Mensal = X% x (total de tokens consumidos no mês)

Alinhamento de incentivo: mais conversas = mais valor entregue = mais receita.

## Estrutura do Projeto

- docs/architecture.md — arquitetura detalhada do sistema
- docs/flow_scripts.md — scripts completos de conversação
- src/webhook_handler.py — webhook Twilio + OpenAI em Flask
- src/agent_prompts.py — system prompts configuráveis
- data/funnel_metrics.csv — KPIs mensais Jul–Nov 2025
- data/contact_template.csv — template de mailing para disparo
- notebooks/funnel_analysis.ipynb — análise do funil e ROI

## Quick Start

1. Cole o system prompt de src/agent_prompts.py no ChatGPT Custom
2. Configure o webhook Twilio apontando para src/webhook_handler.py
3. Preencha data/contact_template.csv e importe no Twilio Campaigns

## Autor

**Kenio Freitas** — Business Analytics | Data Analytics | BI | Lean Six Sigma | 
LinkedIn: linkedin.com/in/kenio-freitas | keniomf@gmail.com

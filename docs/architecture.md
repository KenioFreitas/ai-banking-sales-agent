# Arquitetura Técnica — AI Banking Sales Agent

## Visão Geral

O sistema opera como um funil de vendas automatizado com três camadas:

1. **Captação** — disparo em massa via WhatsApp (Twilio) e voz (Callix)
2. **Qualificação** — agente de IA (ChatGPT Custom) conduz triagem conversacional
3. **Conversão** — handoff para consultor humano que cadastra a venda na plataforma bancária

---

## Componentes

### 1. Base de Prospects

Origem: base pública de CNPJs da Receita Federal, filtrada por critérios de segmentação.

**Critérios de filtragem:**
- CNAE principal (código de atividade econômica)
- Porte da empresa (MEI, ME, EPP)
- Tempo de abertura >= 6 meses
- Estado (UF) de atuação

**Formato do mailing** (data/contact_template.csv):
```
Nome | Telefone | Razão Social | CNPJ | DATA
```

---

### 2. Canal WhatsApp (Twilio)

**Fluxo técnico:**
```
Mailing CSV
    │
    ▼
Twilio Campaigns (disparo em massa WhatsApp Business API)
    │
    ▼
Webhook HTTP POST → seu servidor
    │
    ▼
OpenAI Chat Completions API (system prompt + histórico da conversa)
    │
    ▼
Resposta → Twilio API → WhatsApp do cliente
```

### 3. Canal URA / Voz (Callix)

Blocos utilizados no fluxo Callix:

| Bloco | Função |
|---|---|
| Identificar cliente | Busca dados do contato pelo número de telefone |
| Decidir baseado em variável | Roteamento condicional |
| Fazer pergunta | Coleta input por voz (DTMF) ou texto |
| Enviar mensagem | Dispara mensagem de texto ou voz |
| Qualificar atendimento | Registra qualificação (interesse, desinteresse) |
| Transferir para fila | Transfere para agente humano disponível |
| Fim | Encerra o fluxo |

### 4. Agente de IA (ChatGPT Custom)

- Plataforma: OpenAI GPT Builder (ChatGPT Custom ou API direta)
- Modelo: GPT-4o
- System prompt: ver src/agent_prompts.py

**Responsabilidades:**
- Identificar empresa pelo CNPJ
- Direcionar para trilha de produto correta
- Executar sequência de microcompromissos
- Gerenciar objeções
- Detectar sinal de qualificação → acionar handoff

### 5. Handoff Humano

1. Agente encerra a trilha automatizada
2. Envia dados coletados para planilha/CRM
3. Notifica consultor
4. Consultor assume a conversa já qualificada
5. Cadastra abertura de conta na plataforma bancária

---

## Stack Tecnológica

| Componente | Ferramenta | Alternativas |
|---|---|---|
| WhatsApp API | Twilio | MessageBird, Zenvia, Blip |
| Voz/URA | Callix | Zenvia Voice, Talkdesk |
| Agente de IA | ChatGPT Custom / OpenAI API | Anthropic Claude, Gemini |
| Webhook | Flask (Python) | FastAPI, Node.js Express |
| Histórico de sessões | Redis / DynamoDB | PostgreSQL, Firestore |
| CRM / leads | Google Sheets | HubSpot, Pipedrive |
| Analytics | Python + pandas | Power BI, Looker Studio |

---

## Considerações de Custo

- OpenAI API (GPT-4o): ~$0.005 por conversa
- Twilio WhatsApp: ~$0.06 por conversa iniciada
- 1.000 conversas/dia ≈ $65/dia ≈ $1.950/mês
- Modelo de receita: cobrar margem sobre o custo total (OpenAI + Twilio)

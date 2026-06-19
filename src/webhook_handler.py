"""
Webhook Handler — Twilio WhatsApp -> OpenAI -> Twilio
Integração entre Twilio (WhatsApp inbound) e OpenAI Chat Completions.

Requisitos:
    pip install flask twilio openai python-dotenv

Configuração (.env):
    TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
    TWILIO_AUTH_TOKEN=xxxxxxxxxxxx
    TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
    OPENAI_API_KEY=sk-xxxxxxxxxxxx

Executar:
    python src/webhook_handler.py

Configure a URL no Twilio Console:
    Messaging > WhatsApp Sandbox > When a message comes in
    URL: https://seu-dominio.com/webhook (POST)
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Sessões em memória (use Redis/DB em produção)
sessions: dict = {}


def get_or_create_session(phone: str) -> dict:
    if phone not in sessions:
        from agent_prompts import build_system_prompt
        sessions[phone] = {
            "phone": phone,
            "messages": [{"role": "system", "content": build_system_prompt("geral")}],
            "qualificacao": {},
            "status": "em_andamento",
            "timestamp_inicio": datetime.utcnow().isoformat(),
        }
    return sessions[phone]


def check_for_signals(response_text: str, session: dict) -> str:
    if "[HANDOFF_TRIGGER]" in response_text:
        session["status"] = "handoff"
        trigger_handoff(session)
        idx = response_text.index("[HANDOFF_TRIGGER]")
        return response_text[:idx].strip()
    if "[LEAD_NEGATIVO]" in response_text:
        session["status"] = "desinteresse"
        idx = response_text.index("[LEAD_NEGATIVO]")
        return response_text[:idx].strip()
    return response_text


def trigger_handoff(session: dict):
    lead = {
        "phone": session["phone"],
        "qualificacao": session["qualificacao"],
        "timestamp": datetime.utcnow().isoformat(),
        "status": "handoff_pendente",
    }
    with open("leads_handoff.jsonl", "a") as f:
        f.write(json.dumps(lead) + "\n")
    logger.info(f"Lead registrado: {lead}")
    # TODO: substituir por chamada ao CRM
    # import requests
    # requests.post(os.getenv("HANDOFF_WEBHOOK_URL"), json=lead)


def get_ai_response(session: dict, user_message: str) -> str:
    session["messages"].append({"role": "user", "content": user_message})
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=session["messages"],
            max_tokens=200,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erro OpenAI: {e}")
        reply = "Desculpe, tive um problema técnico. Um consultor vai entrar em contato em breve!"
        session["status"] = "erro_fallback_humano"
    session["messages"].append({"role": "assistant", "content": reply})
    return reply


@app.route("/webhook", methods=["POST"])
def webhook():
    from_number = request.form.get("From", "")
    message_body = request.form.get("Body", "").strip()
    if not from_number or not message_body:
        return Response("Bad Request", status=400)

    session = get_or_create_session(from_number)
    if session["status"] in ["handoff", "desinteresse"]:
        return Response("", status=200)

    if len(session["messages"]) == 1:
        from agent_prompts import PROMPT_ABERTURA, CONFIG
        reply = PROMPT_ABERTURA.format(empresa=CONFIG["nome_empresa"])
        session["messages"].append({"role": "assistant", "content": reply})
    else:
        raw_reply = get_ai_response(session, message_body)
        reply = check_for_signals(raw_reply, session)

    twiml = MessagingResponse()
    twiml.message(reply)
    return Response(str(twiml), mimetype="text/xml")


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok", "sessions_ativas": len(sessions)}, 200


@app.route("/leads", methods=["GET"])
def list_leads():
    leads = [s for s in sessions.values() if s["status"] == "handoff"]
    return {"total": len(leads), "leads": leads}, 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)

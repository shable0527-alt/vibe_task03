"""FastAPI 后端服务：提供 AI 客服对话 API + 静态页面服务。"""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import Config
from rag_engine import RAGEngine
from vectorstore import ChromaStore
from utils.logger import get_logger

logger = get_logger(__name__)

# In-memory session store for conversation history
_sessions: dict[str, list[dict]] = {}
_rag_engine: RAGEngine | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _rag_engine
    store = ChromaStore()
    _rag_engine = RAGEngine(store=store)
    stats = store.get_stats()
    logger.info(f"Server started. Knowledge base: {stats['total_documents']} documents")
    yield
    _rag_engine = None
    _sessions.clear()


app = FastAPI(title="证券AI客服", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic models ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


class StatsResponse(BaseModel):
    total_documents: int
    collection_name: str
    active_sessions: int


# ── API Endpoints ────────────────────────────────────────────────

@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Handle a chat message and return AI response."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="消息不能为空")

    # Get or create session
    session_id = req.session_id or str(uuid.uuid4())
    history = _sessions.setdefault(session_id, [])

    # Get RAG response
    reply = _rag_engine.chat(query=req.message, history=history)

    # Update history
    history.append({"role": "user", "content": req.message})
    history.append({"role": "assistant", "content": reply})

    # Keep history bounded
    if len(history) > 40:
        _sessions[session_id] = history[-20:]

    return ChatResponse(reply=reply, session_id=session_id)


@app.post("/api/session/reset")
async def reset_session(session_id: str | None = None):
    """Reset a conversation session."""
    if session_id and session_id in _sessions:
        del _sessions[session_id]
    return {"status": "ok"}


@app.get("/api/stats", response_model=StatsResponse)
async def stats():
    """Get knowledge base statistics."""
    store_stats = _rag_engine._store.get_stats()
    return StatsResponse(
        total_documents=store_stats["total_documents"],
        collection_name=store_stats["collection_name"],
        active_sessions=len(_sessions),
    )


# ── Web UI ───────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return _CHAT_HTML


_CHAT_HTML = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>理博基金 - 智能客服</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; background: #f5f6fa; height: 100vh; display: flex; flex-direction: column; }

  .header { background: linear-gradient(135deg, #1a3a5c, #2c5f8a); color: #fff; padding: 14px 24px; display: flex; align-items: center; gap: 14px; box-shadow: 0 2px 12px rgba(0,0,0,.12); }
  .header .logo { font-size: 20px; font-weight: 700; letter-spacing: 2px; }
  .header .logo span { font-size: 12px; font-weight: 400; opacity: .7; letter-spacing: 1px; margin-left: 8px; }
  .header .actions { margin-left: auto; display: flex; gap: 12px; align-items: center; }
  .header .stats { font-size: 12px; opacity: .7; }
  .reset-btn { background: rgba(255,255,255,.15); border: 1px solid rgba(255,255,255,.25); color: #fff; border-radius: 6px; padding: 5px 12px; font-size: 12px; cursor: pointer; transition: all .2s; }
  .reset-btn:hover { background: rgba(255,255,255,.25); }

  .chat-container { flex: 1; overflow-y: auto; padding: 20px 16px; display: flex; flex-direction: column; gap: 16px; max-width: 820px; width: 100%; margin: 0 auto; }

  .msg { display: flex; gap: 10px; max-width: 88%; animation: fadeIn .3s ease; }
  .msg.user { align-self: flex-end; flex-direction: row-reverse; }
  .msg.assistant { align-self: flex-start; }

  .avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 14px; flex-shrink: 0; font-weight: 600; }
  .msg.user .avatar { background: #2c5f8a; color: #fff; }
  .msg.assistant .avatar { background: linear-gradient(135deg, #e8f0fe, #d4e4f7); color: #1a3a5c; border: 1px solid #c8d8e8; }

  .bubble { padding: 12px 16px; border-radius: 16px; font-size: 14px; line-height: 1.8; white-space: pre-wrap; word-break: break-word; }
  .msg.user .bubble { background: #2c5f8a; color: #fff; border-bottom-right-radius: 4px; }
  .msg.assistant .bubble { background: #fff; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 1px 6px rgba(0,0,0,.06); }

  .typing .bubble::after { content: '\\25CF\\25CF\\25CF'; animation: blink 1.2s infinite; letter-spacing: 3px; color: #999; }
  @keyframes blink { 0%,100%{opacity:.2} 50%{opacity:1} }
  @keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:none} }

  .input-area { background: #fff; border-top: 1px solid #e4e8ee; padding: 14px 16px; }
  .input-wrap { max-width: 820px; margin: 0 auto; display: flex; gap: 10px; align-items: flex-end; }
  .input-wrap textarea { flex: 1; border: 1.5px solid #dde3ea; border-radius: 12px; padding: 10px 16px; font-size: 14px; resize: none; outline: none; max-height: 120px; line-height: 1.5; font-family: inherit; transition: border .2s; }
  .input-wrap textarea:focus { border-color: #2c5f8a; box-shadow: 0 0 0 3px rgba(44,95,138,.1); }

  .send-btn { width: 42px; height: 42px; border-radius: 50%; border: none; background: #2c5f8a; color: #fff; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all .2s; flex-shrink: 0; }
  .send-btn:hover { background: #1a3a5c; transform: scale(1.05); }
  .send-btn:disabled { background: #c8d0d8; cursor: not-allowed; transform: none; }

  .welcome { text-align: center; padding: 50px 20px; color: #666; }
  .welcome .brand { font-size: 28px; font-weight: 700; color: #1a3a5c; margin-bottom: 4px; letter-spacing: 3px; }
  .welcome .slogan { font-size: 13px; color: #999; letter-spacing: 2px; margin-bottom: 16px; }
  .welcome .intro { font-size: 15px; color: #555; margin-bottom: 24px; line-height: 1.6; }
  .suggestions { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; max-width: 600px; margin: 0 auto; }
  .suggestions button { background: #fff; border: 1.5px solid #dde3ea; border-radius: 22px; padding: 9px 18px; font-size: 13px; cursor: pointer; transition: all .2s; color: #444; }
  .suggestions button:hover { border-color: #2c5f8a; color: #2c5f8a; background: #f0f5fa; box-shadow: 0 2px 8px rgba(44,95,138,.08); }

  .footer { text-align: center; padding: 6px; font-size: 11px; color: #bbb; background: #fff; border-top: 1px solid #f0f0f0; }
</style>
</head>
<body>

<div class="header">
  <div class="logo">理博基金<span>LESS IS MORE</span></div>
  <div class="actions">
    <span class="stats" id="stats"></span>
    <button class="reset-btn" onclick="resetChat()">新对话</button>
  </div>
</div>

<div class="chat-container" id="chat">
  <div class="welcome">
    <div class="brand">理博小助手</div>
    <div class="slogan">辞简理博 / LESS IS MORE</div>
    <div class="intro">您好！我是理博基金的智能客服助手，可以为您解答关于公司、策略、产品、投资流程等方面的问题。</div>
    <div class="suggestions">
      <button onclick="ask(this.textContent)">理博基金是一家什么样的公司？</button>
      <button onclick="ask(this.textContent)">你们有哪些投资策略？</button>
      <button onclick="ask(this.textContent)">2025年度各策略收益如何？</button>
      <button onclick="ask(this.textContent)">理博万象7号产品介绍一下</button>
      <button onclick="ask(this.textContent)">如何购买你们的基金产品？</button>
      <button onclick="ask(this.textContent)">资金安全性如何保障？</button>
    </div>
  </div>
</div>

<div class="input-area">
  <div class="input-wrap">
    <textarea id="input" rows="1" placeholder="请输入您想了解的问题..." onkeydown="handleKey(event)"></textarea>
    <button class="send-btn" id="sendBtn" onclick="send()">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
    </button>
  </div>
</div>

<div class="footer">杭州理博私募基金管理有限公司 | 基金业协会备案编码：P1072890</div>

<script>
const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('input');
const sendBtn = document.getElementById('sendBtn');
let sessionId = null;
let sending = false;

inputEl.addEventListener('input', () => {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
});

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
}

function ask(text) { inputEl.value = text; send(); }

async function resetChat() {
  if (sessionId) {
    fetch('/api/session/reset', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({session_id: sessionId}) }).catch(()=>{});
  }
  sessionId = null;
  chatEl.innerHTML = `
    <div class="welcome">
      <div class="brand">理博小助手</div>
      <div class="slogan">辞简理博 / LESS IS MORE</div>
      <div class="intro">您好！我是理博基金的智能客服助手，可以为您解答关于公司、策略、产品、投资流程等方面的问题。</div>
      <div class="suggestions">
        <button onclick="ask(this.textContent)">理博基金是一家什么样的公司？</button>
        <button onclick="ask(this.textContent)">你们有哪些投资策略？</button>
        <button onclick="ask(this.textContent)">2025年度各策略收益如何？</button>
        <button onclick="ask(this.textContent)">理博万象7号产品介绍一下</button>
        <button onclick="ask(this.textContent)">如何购买你们的基金产品？</button>
        <button onclick="ask(this.textContent)">资金安全性如何保障？</button>
      </div>
    </div>`;
}

async function send() {
  const msg = inputEl.value.trim();
  if (!msg || sending) return;
  sending = true;
  sendBtn.disabled = true;

  const welcome = chatEl.querySelector('.welcome');
  if (welcome) welcome.remove();

  addMsg('user', msg);
  inputEl.value = '';
  inputEl.style.height = 'auto';

  const typingEl = addMsg('assistant', '', true);

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, session_id: sessionId })
    });
    const data = await res.json();
    sessionId = data.session_id;
    typingEl.remove();
    addMsg('assistant', data.reply);
  } catch (e) {
    typingEl.remove();
    addMsg('assistant', '网络出现了一点问题，请稍后再试。如需帮助，请联系 investor@liboinv.com');
  }
  sending = false;
  sendBtn.disabled = false;
  inputEl.focus();
}

function addMsg(role, text, typing = false) {
  const div = document.createElement('div');
  div.className = `msg ${role}` + (typing ? ' typing' : '');
  const avatarText = role === 'user' ? 'You' : 'LB';
  div.innerHTML = `<div class="avatar">${avatarText}</div><div class="bubble">${typing ? '' : escHtml(text)}</div>`;
  chatEl.appendChild(div);
  chatEl.scrollTop = chatEl.scrollHeight;
  return div;
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>');
}

fetch('/api/stats').then(r=>r.json()).then(d=>{
  document.getElementById('stats').textContent = `知识库 ${d.total_documents} 条`;
}).catch(()=>{});
</script>
</body>
</html>
"""

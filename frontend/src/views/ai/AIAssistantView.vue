<template>
  <div class="fade-in-up">
    <div class="page-header">
      <div>
        <h1 class="page-title"><i class="bi bi-robot me-2 text-primary"></i>AI Assistant</h1>
        <p class="page-subtitle">Ask questions about your church data in plain language</p>
      </div>
    </div>

    <!-- Feature cards -->
    <div class="row g-3 mb-4" v-if="messages.length === 0">
      <div class="col-md-4" v-for="f in features" :key="f.title">
        <div class="cos-card ai-feature-card" @click="sendSuggestion(f.prompt)" style="cursor:pointer">
          <div class="ai-feature-icon">{{ f.emoji }}</div>
          <h6 class="fw-bold mb-1">{{ f.title }}</h6>
          <p class="text-muted small mb-0">{{ f.description }}</p>
          <div class="text-primary small mt-2 fw-semibold">
            <i class="bi bi-arrow-right me-1"></i>{{ f.prompt.slice(0,60) }}…
          </div>
        </div>
      </div>
    </div>

    <!-- Chat window -->
    <div class="cos-card p-0" style="height:520px;display:flex;flex-direction:column">
      <!-- Messages -->
      <div class="chat-messages" ref="chatContainer">
        <div v-if="messages.length === 0" class="cos-empty" style="padding:3rem">
          <i class="bi bi-robot" style="font-size:3rem;opacity:.2;display:block;margin-bottom:1rem"></i>
          <p class="fw-semibold">How can I help you today?</p>
          <p class="text-muted small">Ask me anything about your members, finances, attendance, or get insights and recommendations.</p>
        </div>

        <div v-for="msg in messages" :key="msg.id" class="message-row" :class="msg.role">
          <div class="message-bubble" :class="msg.role">
            <div v-if="msg.role === 'assistant'" class="message-avatar ai">
              <i class="bi bi-robot"></i>
            </div>
            <div v-else class="message-avatar user">
              <i class="bi bi-person-fill"></i>
            </div>
            <div class="message-content">
              <div class="message-text" v-html="formatMessage(msg.content)"></div>
              <div class="message-time">{{ msg.time }}</div>
            </div>
          </div>
        </div>

        <div v-if="thinking" class="message-row assistant">
          <div class="message-bubble assistant">
            <div class="message-avatar ai"><i class="bi bi-robot"></i></div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Input -->
      <div class="chat-input-area">
        <div class="chat-input-row">
          <textarea
            v-model="inputText"
            class="form-control chat-input"
            placeholder="Ask about your members, finances, events... (Enter to send, Shift+Enter for new line)"
            rows="2"
            @keydown.enter.exact.prevent="sendMessage"
            @keydown.enter.shift.exact="() => {}"
            :disabled="thinking || !aiEnabled"
          ></textarea>
          <button class="btn btn-primary chat-send-btn" @click="sendMessage" :disabled="thinking || !inputText.trim() || !aiEnabled">
            <i class="bi bi-send-fill" v-if="!thinking"></i>
            <span class="spinner-border spinner-border-sm" v-else></span>
          </button>
        </div>
        <div v-if="!aiEnabled" class="text-center text-muted small mt-2">
          <i class="bi bi-info-circle me-1"></i>
          AI features are disabled. Enable them in
          <RouterLink to="/settings" class="text-primary">Settings → Integrations</RouterLink>.
        </div>
        <div class="chat-actions" v-if="messages.length > 0">
          <button class="btn btn-xs btn-outline-secondary" @click="clearChat">
            <i class="bi bi-trash me-1"></i>Clear chat
          </button>
          <button class="btn btn-xs btn-outline-primary" @click="exportChat">
            <i class="bi bi-download me-1"></i>Export
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue'
import dayjs from 'dayjs'
import api from '@/api'
import { useSettingsStore } from '@/stores/settings'
import { financeApi, membersApi } from '@/api'

const settingsStore = useSettingsStore()
const aiEnabled = computed(() => settingsStore.settings.enable_ai_features)

const messages = ref([])
const inputText = ref('')
const thinking = ref(false)
const chatContainer = ref(null)
let msgId = 0

const features = [
  {
    emoji: '💰', title: 'Financial Insights',
    description: 'Analyse income trends, top givers, and financial health',
    prompt: 'Give me a financial summary for this month including tithes, offerings, and expenses',
  },
  {
    emoji: '👥', title: 'Member Analytics',
    description: 'Membership growth, retention, and engagement insights',
    prompt: 'How is our membership growing? How many new members joined this year?',
  },
  {
    emoji: '📊', title: 'Giving Forecast',
    description: 'Predict expected income based on historical trends',
    prompt: 'Based on our giving history, what income should we expect next month?',
  },
  {
    emoji: '🔔', title: 'Pastoral Alerts',
    description: 'Members needing follow-up or showing disengagement',
    prompt: 'Which members have been absent for more than 2 weeks and need follow-up?',
  },
  {
    emoji: '📋', title: 'Budget Advice',
    description: 'Review spending patterns and budget recommendations',
    prompt: 'Review our budget vs actual spending and highlight any concerns',
  },
  {
    emoji: '🎤', title: 'Sermon Summary',
    description: 'Summarise and extract insights from recent sermons',
    prompt: 'Summarise the key themes from our sermons this month',
  },
]

async function buildContext() {
  // Gather real data to give the AI context
  const context = { church_name: settingsStore.settings.church_name, date: dayjs().format('MMMM D, YYYY') }
  try {
    const [finRes, memRes] = await Promise.all([
      financeApi.summary({ period: 'this_month' }),
      membersApi.list({ page_size: 1 }),
    ])
    context.finance = finRes.data
    context.member_count = memRes.data.count
  } catch {}
  return context
}

function formatMessage(text) {
  // Convert markdown-like formatting to HTML
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
    .replace(/^• (.*)/gm, '<li>$1</li>')
    .replace(/^- (.*)/gm, '<li>$1</li>')
}

async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || thinking.value) return

  inputText.value = ''
  messages.value.push({ id: ++msgId, role: 'user', content: text, time: dayjs().format('h:mm A') })
  await scrollToBottom()

  thinking.value = true
  try {
    const context = await buildContext()
    const systemPrompt = `You are a pastoral and church management AI assistant for ${context.church_name}. 
Today is ${context.date}.
Current data: Active members: ${context.member_count || 'unknown'}.
Finance this month: Income ${context.finance?.this_month || 'unknown'}, Total tithes: ${context.finance?.total_tithes || 'unknown'}.
Be warm, professional, and concise. Use bullet points for lists. Provide actionable insights.`

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 1000,
        system: systemPrompt,
        messages: [
          ...messages.value
            .filter(m => m.role !== 'assistant' || m.id < msgId)
            .slice(-10)
            .map(m => ({ role: m.role, content: m.content })),
          { role: 'user', content: text }
        ],
      })
    })
    const data = await response.json()
    const reply = data.content?.[0]?.text || 'I could not generate a response. Please check your API configuration in Settings.'
    messages.value.push({ id: ++msgId, role: 'assistant', content: reply, time: dayjs().format('h:mm A') })
  } catch (e) {
    messages.value.push({
      id: ++msgId, role: 'assistant',
      content: 'I encountered an error. Please ensure the Anthropic API key is configured in Settings → Integrations → AI Features.',
      time: dayjs().format('h:mm A')
    })
  } finally {
    thinking.value = false
    await scrollToBottom()
  }
}

async function sendSuggestion(prompt) {
  inputText.value = prompt
  await sendMessage()
}

function clearChat() {
  if (confirm('Clear the conversation?')) messages.value = []
}

function exportChat() {
  const text = messages.value.map(m => `[${m.role.toUpperCase()}] ${m.time}\n${m.content}`).join('\n\n---\n\n')
  const blob = new Blob([text], { type: 'text/plain' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = `ai_chat_${dayjs().format('YYYYMMDD_HHmm')}.txt`
  a.click()
}

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.ai-feature-card { transition: all .2s; }
.ai-feature-card:hover { box-shadow: var(--cos-shadow-lg); transform: translateY(-2px); border-color: var(--cos-primary) !important; }
.ai-feature-icon { font-size: 2rem; margin-bottom: 8px; }

.chat-messages {
  flex: 1; overflow-y: auto; padding: 1.5rem;
  display: flex; flex-direction: column; gap: 16px;
}

.message-row { display: flex; }
.message-row.assistant { justify-content: flex-start; }
.message-row.user { justify-content: flex-end; }

.message-bubble { display: flex; gap: 10px; max-width: 80%; }
.message-bubble.user { flex-direction: row-reverse; }

.message-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; flex-shrink: 0;
}
.message-avatar.ai { background: var(--cos-primary); color: white; }
.message-avatar.user { background: var(--cos-accent); color: white; }

.message-content { display: flex; flex-direction: column; gap: 4px; }
.message-text {
  padding: 10px 14px; border-radius: 12px;
  font-size: 13.5px; line-height: 1.65;
}
.message-row.assistant .message-text { background: var(--cos-bg); border: 1px solid var(--cos-border); border-radius: 0 12px 12px 12px; }
.message-row.user .message-text { background: var(--cos-primary); color: white; border-radius: 12px 0 12px 12px; }
.message-time { font-size: 10px; color: var(--cos-text-muted); padding: 0 4px; }
.message-row.user .message-time { text-align: right; }

.typing-indicator { display: flex; gap: 4px; padding: 12px 16px; background: var(--cos-bg); border-radius: 12px; border: 1px solid var(--cos-border); }
.typing-indicator span { width: 7px; height: 7px; border-radius: 50%; background: var(--cos-text-muted); animation: bounce 1.2s infinite; }
.typing-indicator span:nth-child(2) { animation-delay: .2s; }
.typing-indicator span:nth-child(3) { animation-delay: .4s; }
@keyframes bounce { 0%,60%,100% { transform: translateY(0); } 30% { transform: translateY(-6px); } }

.chat-input-area { padding: 1rem 1.5rem; border-top: 1px solid var(--cos-border); background: var(--cos-card-bg); }
.chat-input-row { display: flex; gap: 10px; align-items: flex-end; }
.chat-input { resize: none; flex: 1; border-radius: 12px; font-size: 13.5px; }
.chat-send-btn { width: 42px; height: 42px; border-radius: 12px; padding: 0; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.chat-actions { display: flex; gap: 8px; margin-top: 8px; }
.btn-xs { padding: 3px 10px; font-size: 11px; }
</style>

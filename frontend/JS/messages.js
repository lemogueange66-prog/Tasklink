/* Chat: conversation list (message.html) and a live thread (message.html?to=ID).
   New messages arrive by asking the server every few seconds while the page is open. */
const $ = (id) => document.getElementById(id);
const to = new URLSearchParams(location.search).get("to");
const POLL_MS = 3000;

const dayKey = (s) => new Date(String(s).replace(" ", "T") + "Z").toDateString();
const clock = (s) => { const d = new Date(String(s).replace(" ", "T") + "Z"); return isNaN(d) ? "" : d.toLocaleTimeString(lang === "fr" ? "fr-FR" : "en-GB", { hour: "2-digit", minute: "2-digit" }); };
const dayLabel = (s) => { const d = new Date(String(s).replace(" ", "T") + "Z"); return isNaN(d) ? "" : d.toLocaleDateString(lang === "fr" ? "fr-FR" : "en-GB", { weekday: "long", day: "numeric", month: "long" }); };
const shortWhen = (s) => {
  const d = new Date(String(s).replace(" ", "T") + "Z");
  if (isNaN(d)) return "";
  return d.toDateString() === new Date().toDateString() ? clock(s)
    : d.toLocaleDateString(lang === "fr" ? "fr-FR" : "en-GB", { day: "numeric", month: "short" });
};

/* Same-site links (like a meeting point) become clickable; everything else stays plain text. */
function linkify(text) {
  return esc(text).replace(/https?:\/\/[^\s<]+/g, (u) => {
    try {
      const url = new URL(u.replace(/&amp;/g, "&"));
      if (url.origin === location.origin) {
        const label = url.pathname.endsWith("/route.html") ? t("Meet · 3D map") + " →" : url.pathname + url.search;
        return `<a href="${esc(url.pathname + url.search)}">${esc(label)}</a>`;
      }
    } catch (e) {}
    return u;
  });
}

/* ---------------- conversation list ---------------- */
async function showList() {
  $("listView").hidden = false;
  const list = $("list");
  try {
    const items = await api("/api/chat/conversations");
    list.innerHTML = items.map((c) => `<a class="card convo ${c.unread ? "unread" : ""}" href="message.html?to=${esc(c.user.id)}">
        ${avatarHtml(c.user.full_name, c.user.profile_photo)}
        <div class="who"><b>${esc(c.user.full_name)}</b><span class="last">${c.mine ? esc(t("You:")) + " " : ""}${esc(c.last.split("\n")[0])}</span></div>
        <span class="when">${esc(shortWhen(c.created))}</span>
        ${c.unread ? `<span class="dot">${esc(c.unread)}</span>` : ""}</a>`).join("")
      || `<div class="empty-state">No conversations yet. Open a profile and tap Message.</div>`;
  } catch (err) { list.innerHTML = `<p class="msg">${esc(t(err.message))}</p>`; }
}

$("findForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    const { id } = await api("/api/chat/find", "POST", { email: e.target.email.value });
    location.href = "message.html?to=" + id;
  } catch (err) { showError($("findMsg"), err); }
});

/* ---------------- one conversation ---------------- */
let lastId = 0, lastDay = "", timer = null, busy = false;
const log = $("log");

function addMessages(msgs) {
  const nearBottom = log.scrollHeight - log.scrollTop - log.clientHeight < 120;
  let html = "";
  for (const m of msgs) {
    const day = dayKey(m.created);
    if (day !== lastDay) { lastDay = day; html += `<div class="day-sep">${esc(dayLabel(m.created))}</div>`; }
    html += `<div class="msg-b ${m.mine ? "mine" : ""}">${linkify(m.content)}<time>${esc(clock(m.created))}</time></div>`;
    lastId = Math.max(lastId, m.id);
  }
  if (!html) return;
  log.querySelector(".empty-state")?.remove();
  log.insertAdjacentHTML("beforeend", html);
  if (nearBottom || msgs.some((m) => m.mine)) log.scrollTop = log.scrollHeight;
}

async function poll(first) {
  if (busy) return;
  busy = true;
  try {
    const data = await api(`/api/chat/${encodeURIComponent(to)}?after=${lastId}`);
    if (first) {
      $("peerName").textContent = data.user.full_name;
      $("peerCity").textContent = t(data.user.city);
      renderAvatar($("peerAvatar"), data.user);
      $("peerAvatar").className = "avatar avatar-sm";
      $("peerAvatar").style.background = colorFor(data.user.full_name);
      $("peerAvatar").href = "provider.html?id=" + encodeURIComponent(data.user.id);
      if (!data.messages.length) log.innerHTML = `<div class="empty-state" style="margin:auto">${esc(t("Say hello 👋"))}</div>`;
    }
    addMessages(data.messages);
    if (window.refreshUnread && (first || data.messages.some((m) => !m.mine))) window.refreshUnread();   // update the red dot
    if (first) log.scrollTop = log.scrollHeight;
    $("msg").textContent = "";
  } catch (err) {
    if (first) { $("msg").textContent = t(err.message); stop(); }
  }
  busy = false;
}
function start() { stop(); timer = setInterval(() => { if (!document.hidden) poll(false); }, POLL_MS); }
function stop() { clearInterval(timer); }
document.addEventListener("visibilitychange", () => { if (!document.hidden && to) poll(false); });

function showThread() {
  $("threadView").hidden = false;
  $("meetLink").href = "route.html?with=" + encodeURIComponent(to);
  const box = $("composer").content;
  const grow = () => { box.style.height = "auto"; box.style.height = Math.min(box.scrollHeight, 120) + "px"; };
  box.addEventListener("input", grow);
  box.addEventListener("keydown", (e) => {                 // Enter sends, Shift+Enter = new line
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); $("composer").requestSubmit(); }
  });
  $("composer").addEventListener("submit", async (e) => {
    e.preventDefault();
    const content = box.value.trim();
    if (!content) return;
    $("sendBtn").disabled = true;
    try {
      await api("/api/chat/" + encodeURIComponent(to), "POST", { content });
      box.value = ""; grow();
      await poll(false);
      $("msg").textContent = "";
    } catch (err) { showError($("msg"), err); }
    $("sendBtn").disabled = false;
    box.focus();
  });
  poll(true).then(start);
}

if (to && /^\d+$/.test(to)) showThread(); else showList();

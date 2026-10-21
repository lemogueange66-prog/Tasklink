const list = document.getElementById("list");
const to = new URLSearchParams(location.search).get("to");
if (to) document.querySelector("[name=to_email]").parentElement.hidden = true;

async function load() {
  const items = await api("/api/messages");
  list.innerHTML = items.map((m) => `<div class="card"><b>${esc(m.sender)}</b> → ${esc(m.receiver)}
    <p>${esc(m.content)}</p><small>${esc(m.created)}</small></div>`).join("")
    || "<p>No messages yet.</p>";
}

document.getElementById("send").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("msg");
  try {
    const data = formData(e.target);
    if (to) data.to_id = Number(to);
    await api("/api/messages", "POST", data);
    e.target.reset();
    msg.textContent = "";
    load();
  } catch (err) {
    msg.textContent = err.message;
  }
});
load();
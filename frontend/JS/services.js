const list = document.getElementById("list");

async function load() {
  const q = encodeURIComponent(document.getElementById("q").value);
  const c = encodeURIComponent(document.getElementById("category").value);
  const items = await api(`/api/services?q=${q}&category=${c}`);
  list.innerHTML = items.map((s) => `<div class="card"><b>${esc(s.title)}</b> ${s.kind === "training" ? `<span class="badge">Training</span>` : ""}<br>
    ${esc(s.provider)} · ${esc(t(s.category))} · ${esc(t(s.city))}${s.rating ? ` · ★ ${esc(s.rating)}` : ""}<br>
    From ${esc(s.price)} FCFA<p>${esc(s.description)}</p>
    <a class="link" href="provider.html?id=${esc(s.user_id)}">View profile and call</a></div>`).join("")
    || "<p>No services found. Add the first one below.</p>";
}

document.getElementById("q").value = new URLSearchParams(location.search).get("q") || "";
document.getElementById("search").onclick = load;
document.getElementById("add").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api("/api/services", "POST", formData(e.target));
  e.target.reset();
  load();
});
load();
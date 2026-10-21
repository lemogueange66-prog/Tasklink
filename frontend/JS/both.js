const list = document.getElementById("list");
const mine = document.getElementById("mine");
const STATUS = { open: "Open", in_progress: "In progress", done: "Done" };

async function load() {
  const q = encodeURIComponent(document.getElementById("q").value);
  const items = await api(`/api/missions?q=${q}`);
  const svc = await api(`/api/services?q=${q}&category=`);
  document.getElementById("svc").innerHTML = svc.map((s) => `<div class="card"><b>${esc(s.title)}</b> ${s.kind === "training" ? `<span class="badge">Training</span>` : ""}<br>
    ${esc(s.provider)} · ${esc(t(s.category))} · ${esc(t(s.city))}${s.rating ? ` · ★ ${esc(s.rating)}` : ""}<br>
    From ${esc(s.price)} FCFA<br><a class="link" href="provider.html?id=${esc(s.user_id)}">View profile and call</a></div>`).join("")
    || "<p>No services found.</p>";
  list.innerHTML = items.map((m) => `<div class="card"><b>${esc(m.title)}</b><br>
    ${esc(m.author)} · ${esc(t(m.city))}<br>Budget: ${esc(m.budget)} FCFA
    <p>${esc(m.description)}</p>
    <button class="orange" data-apply="${m.id}" ${m.applied ? "disabled" : ""}>${m.applied ? "Applied" : "Apply"}</button></div>`).join("")
    || "<p>No open missions yet. Post the first one below.</p>";
  loadMine();
}

async function loadMine() {
  const items = await api("/api/my-missions");
  mine.innerHTML = items.map((m) => `<div class="card"><b>${esc(m.title)}</b> · ${esc(t(STATUS[m.status]))}
    ${m.status === "open" ? m.applicants.map((a) => `<p><a class="link" href="provider.html?id=${a.id}">${esc(a.full_name)}</a>
      <button data-accept="${m.id}" data-user="${a.id}">Accept</button></p>`).join("") : ""}
    ${m.status === "in_progress" ? `<p>${esc(m.worker)}</p><button data-done="${m.id}">Mark as done</button>` : ""}
    ${m.status === "done" && !m.reviewed ? `<button data-review="${m.id}">Rate the worker</button>` : ""}</div>`).join("")
    || "<p>You have not posted any mission yet.</p>";
}

document.addEventListener("click", async (e) => {
  const d = e.target.dataset;
  try {
    if (d.apply) await api(`/api/missions/${d.apply}/apply`, "POST");
    else if (d.accept) await api(`/api/missions/${d.accept}/accept`, "POST", { user_id: Number(d.user) });
    else if (d.done) await api(`/api/missions/${d.done}/complete`, "POST");
    else if (d.review) {
      const rating = Number(prompt(t("Rating from 1 to 5")));
      if (!rating) return;
      await api(`/api/missions/${d.review}/review`, "POST", { rating, comment: prompt(t("Comment (optional)")) || "" });
    } else return;
    load();
  } catch (err) { alert(t(err.message)); }
});

document.getElementById("search").onclick = load;
document.getElementById("add").addEventListener("submit", async (e) => {
  e.preventDefault();
  await api("/api/missions", "POST", formData(e.target));
  e.target.reset();
  load();
});
load();
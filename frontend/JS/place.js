/* "My meeting place": pick a spot on the 3D map (search, tap, or GPS) and choose whether to share it */
const $ = (id) => document.getElementById(id);
let map, marker, picked = null, tilted = true;

const setPick = (lat, lng, { fly = false, label } = {}) => {
  picked = { lat, lng };
  if (!marker) {
    marker = TLMAP.pin(map, "meet", "📍", [lng, lat], true);
    marker.on("dragend", async () => { const p = marker.getLngLat(); await setPick(p.lat, p.lng, { label: true }); });
  } else marker.setLngLat([lng, lat]);
  if (fly) map.flyTo({ center: [lng, lat], zoom: 16.5, pitch: tilted ? 60 : 0, speed: 1.2 });
  if (label) TLMAP.reverse(lat, lng).then((name) => { if (name && !$("form").label.dataset.touched) $("form").label.value = name; });
};

async function init() {
  const me = await api("/api/me");
  const start = me.lat != null ? [me.lng, me.lat] : TLMAP.CENTERS[me.city] || TLMAP.CENTERS.Other;
  try {
    map = await TLMAP.createMap($("map"), { center: start, zoom: me.lat != null ? 16 : 13 });
  } catch (e) { $("mapStatus").textContent = t(e.message); return; }
  $("mapStatus").hidden = true;

  const f = $("form");
  if (me.lat != null) {
    setPick(me.lat, me.lng);
    f.label.value = me.location_label || "";
    f.share.checked = !!me.share_location;
    $("remove").hidden = false;
  }
  f.label.addEventListener("input", () => { f.label.dataset.touched = "1"; });
  map.on("click", (e) => { setPick(e.lngLat.lat, e.lngLat.lng, { label: true }); });
}

$("tilt").onclick = () => {
  tilted = !tilted;
  $("tilt").classList.toggle("on", tilted);
  if (map) map.easeTo({ pitch: tilted ? 60 : 0, bearing: tilted ? -17 : 0, duration: 700 });
};

$("gps").onclick = () => {
  if (!navigator.geolocation) return showError($("msg"), new Error("Could not get your position"));
  navigator.geolocation.getCurrentPosition(
    (p) => { if (map) { setPick(p.coords.latitude, p.coords.longitude, { fly: true, label: true }); $("msg").textContent = ""; } },
    () => showError($("msg"), new Error("Could not get your position")),
    { enableHighAccuracy: true, timeout: 12000 });
};

$("searchForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const q = $("q").value.trim(), box = $("results");
  if (!q) return;
  box.hidden = false;
  box.innerHTML = `<li class="meta" style="padding:10px 14px">${esc(t("Loading…"))}</li>`;
  try {
    const found = await TLMAP.search(q);
    box.innerHTML = found.length
      ? found.map((r, i) => `<li><button type="button" data-i="${i}">${esc(r.name)}</button></li>`).join("")
      : `<li class="meta" style="padding:10px 14px">${esc(t("No place found"))}</li>`;
    box.onclick = (ev) => {
      const b = ev.target.closest("[data-i]");
      if (!b || !map) return;
      const r = found[b.dataset.i];
      $("form").label.value = r.name.split(",").slice(0, 3).join(",").trim();
      $("form").label.dataset.touched = "1";
      setPick(r.lat, r.lng, { fly: true });
      box.hidden = true;
    };
  } catch (err) { box.innerHTML = `<li class="msg" style="padding:10px 14px">${esc(t(err.message))}</li>`; }
});

$("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = $("msg"), btn = $("save");
  msg.textContent = "";
  if (!picked) return showError(msg, new Error("Choose a place on the map"));
  btn.disabled = true;
  try {
    await api("/api/me/location", "PUT", { ...picked, label: e.target.label.value, share: e.target.share.checked });
    $("remove").hidden = false;
    showOk(msg, "Place saved");
  } catch (err) { showError(msg, err); }
  btn.disabled = false;
});

$("remove").onclick = async () => {
  try {
    await api("/api/me/location", "PUT", { clear: true });
    if (marker) { marker.remove(); marker = null; }
    picked = null; $("form").reset(); $("remove").hidden = true;
    showOk($("msg"), "Place removed");
  } catch (err) { showError($("msg"), err); }
};

init().catch((err) => showError($("msg"), err));

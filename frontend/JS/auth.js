/* Login and registration forms */
document.getElementById("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const msg = document.getElementById("msg"), btn = e.target.querySelector("button[type=submit]");
  msg.textContent = "";
  btn.disabled = true;
  try {
    await api(e.target.dataset.url, "POST", formData(e.target));
    location.href = e.target.dataset.next;
  } catch (err) {
    showError(msg, err);
    btn.disabled = false;
  }
});

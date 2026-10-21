document.getElementById("form").addEventListener("submit", async (e) => {
  e.preventDefault();
  try {
    await api(e.target.dataset.url, "POST", formData(e.target));
    location.href = e.target.dataset.next;
  } catch (err) {
    document.getElementById("msg").textContent = err.message;
  }
});
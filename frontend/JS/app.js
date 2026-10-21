async function api(url, method = "GET", body) {
  const res = await fetch(url, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401 && document.body.hasAttribute("data-nav")) location.href = "login.html";
  if (!res.ok) throw new Error(data.error || "Something went wrong");
  return data;
}

const esc = (s) => String(s ?? "").replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const formData = (form) => Object.fromEntries(new FormData(form));

const mediaHtml = (items, mine = false) => items.map((i) => `<div class="card">${i.kind === "video"
  ? `<video controls playsinline src="/uploads/${esc(i.filename)}"></video>`
  : `<img src="/uploads/${esc(i.filename)}" alt="${esc(i.caption || "Portfolio image")}">`}
  <p>${esc(i.caption)}</p><small>${esc((i.created || "").slice(0, 10))}</small>${mine ? `<button class="orange" data-del="${i.id}">Delete</button>` : ""}</div>`).join("") || "<p>Nothing here yet.</p>";

if (document.body.hasAttribute("data-nav")) {
  document.body.insertAdjacentHTML("beforeend", `<nav>
    <a href="home.html">Home</a><a href="services.html">Explore</a>
    <a href="messages.html">Messages</a><a href="profile.html">Profile</a></nav>`);
}

/* ---- Languages: French first, English second ---- */
let lang = "fr";
try { lang = localStorage.getItem("lang") || "fr"; } catch (e) {}
document.documentElement.lang = lang;

const FR = {
  "Log in": "Se connecter", "Email": "E-mail", "Password": "Mot de passe",
  "New here?": "Nouveau ici ?", "Create an account": "Créer un compte",
  "Join TaskLink and turn your skills into opportunities.": "Rejoins TaskLink et transforme tes compétences en opportunités.",
  "Full name": "Nom complet", "Phone number": "Numéro de téléphone", "City": "Ville", "Other": "Autre",
  "Create my account": "Créer mon compte", "Already have an account?": "Déjà un compte ?",
  "Connecting skills to opportunities.": "Connecte les compétences aux opportunités.",
  "Get started": "Commencer", "I already have an account": "J'ai déjà un compte",
  "Hello": "Bonjour", "What do you want to do?": "Que veux-tu faire ?",
  "Find a service": "Trouver un service", "Offer a service": "Proposer un service", "Both": "Les deux", "Do both": "Faire les deux", "Training": "Formation", "Finance": "Finance et investissement", "Content": "Création de contenu", "Coaching": "Coaching", "Services and trainings": "Services et formations", "Ex: logo, how to save money...": "Ex : logo, comment économiser mon argent...",
  "Home": "Accueil", "Explore": "Explorer", "Profile": "Profil",
  "Ex: logo, sewing...": "Ex : logo, couture...", "All categories": "Toutes les catégories", "Search": "Rechercher",
  "Service name": "Nom du service", "Category": "Catégorie", "Starting price (FCFA)": "Prix de départ (FCFA)",
  "Add service": "Ajouter le service", "No services found. Add the first one below.": "Aucun service trouvé. Ajoute le premier ci-dessous.",
  "View profile and call": "Voir le profil et appeler",
  "IT": "Informatique", "Education": "Éducation", "Sewing": "Couture", "Beauty": "Beauté", "Repair": "Réparation",
  "Find a mission": "Trouver une mission", "Search missions": "Rechercher des missions", "Post a mission": "Publier une mission",
  "Title": "Titre", "Post mission": "Publier la mission",
  "No open missions yet. Post the first one below.": "Aucune mission ouverte pour le moment. Publie la première ci-dessous.",
  "My missions": "Mes missions", "You have not posted any mission yet.": "Tu n'as pas encore publié de mission.",
  "Open": "Ouverte", "In progress": "En cours", "Done": "Terminée",
  "Apply": "Postuler", "Applied": "Candidature envoyée", "Accept": "Accepter",
  "Mark as done": "Marquer comme terminée", "Rate the worker": "Noter le prestataire",
  "Rating from 1 to 5": "Note de 1 à 5", "Comment (optional)": "Commentaire (facultatif)",
  "Send to (email)": "Envoyer à (e-mail)", "Send message": "Envoyer le message", "No messages yet.": "Aucun message pour le moment.",
  "My profile": "Mon profil", "About me": "À propos de moi", "My skills (comma separated)": "Mes compétences (séparées par des virgules)",
  "Save": "Enregistrer", "Saved": "Enregistré", "Log out": "Se déconnecter", "My portfolio": "Mon portfolio",
  "Photo or video of your work": "Photo ou vidéo de ton travail", "Short description": "Courte description",
  "Upload": "Envoyer", "Uploaded": "Envoyé", "Upload failed": "Échec de l'envoi", "Nothing here yet.": "Rien ici pour le moment.",
  "Introduce yourself in a few words...": "Présente-toi en quelques mots...", "Design, Video editing": "Design, Montage vidéo",
  "Ex: Logo for a bakery": "Ex : Logo pour une boulangerie",
  "Reviews": "Avis", "Delete": "Supprimer", "Delete this post?": "Supprimer cette publication ?", "Services and missions": "Services et missions", "No services found.": "Aucun service trouvé.", "No reviews yet": "Pas encore d'avis", "Report this profile": "Signaler ce profil",
  "Why are you reporting this profile?": "Pourquoi signales-tu ce profil ?",
  "Thank you. We will review this profile.": "Merci. Nous allons examiner ce profil.",
  "File too large (max 30 MB)": "Fichier trop volumineux (30 Mo max)",
  "Please log in": "Connecte-toi d'abord", "This email is already in use": "Cet e-mail est déjà utilisé",
  "Wrong email or password": "E-mail ou mot de passe incorrect",
  "Too many attempts. Try again in 10 minutes.": "Trop de tentatives. Réessaie dans 10 minutes.",
  "Use a JPG, PNG, WEBP, MP4, WEBM or MOV file": "Utilise un fichier JPG, PNG, WEBP, MP4, WEBM ou MOV",
  "Not allowed": "Action non autorisée", "You cannot apply to this mission": "Tu ne peux pas postuler à cette mission",
  "No user found": "Utilisateur introuvable", "User not found": "Utilisateur introuvable",
  "Something went wrong": "Une erreur est survenue",
};
const PATTERNS = [
  [/^Hello, (.+)$/, "Bonjour, $1"], [/^From (.+) FCFA$/, "À partir de $1 FCFA"],
  [/^Budget: (.+) FCFA$/, "Budget : $1 FCFA"], [/^Call (.+)$/, "Appeler $1"],
];
const t = (s) => {
  if (lang !== "fr" || !s) return s;
  const k = s.trim();
  if (FR[k]) return s.replace(k, FR[k]);
  for (const [re, to] of PATTERNS) if (re.test(k)) return s.replace(k, k.replace(re, to));
  return s;
};
const tNode = (n) => { const v = t(n.nodeValue); if (v !== n.nodeValue) n.nodeValue = v; };
function translate(root) {
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  for (let n = w.nextNode(); n; n = w.nextNode()) tNode(n);
  root.querySelectorAll("[placeholder]").forEach((el) => { el.placeholder = t(el.placeholder); });
}
document.body.insertAdjacentHTML("beforeend",
  `<button id="lang" aria-label="Language" style="position:absolute;top:10px;right:10px;width:auto;margin:0;padding:6px 12px;z-index:10;background:#2563eb">${lang === "fr" ? "EN" : "FR"}</button>`);
document.getElementById("lang").onclick = () => {
  try { localStorage.setItem("lang", lang === "fr" ? "en" : "fr"); } catch (e) {}
  location.reload();
};
if (lang === "fr") {
  new MutationObserver((ms) => ms.forEach((m) => m.addedNodes.forEach((n) => {
    if (n.nodeType === 3) tNode(n); else if (n.nodeType === 1) translate(n);
  }))).observe(document.body, { childList: true, subtree: true });
  translate(document.body);
}
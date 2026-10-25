# TaskLink

TaskLink is a local-services and missions web app built with Flask, SQLite, HTML, CSS and JavaScript.

## Run on Windows
1. Install Python 3.10 or newer (python.org or Miniconda).
2. Extract the ZIP to a normal folder (not inside the ZIP preview).
3. Double-click `start.bat`. The first launch installs Flask if it is missing and creates the database.
   (Or, in a terminal: `cd backend` then `python app.py`.)
4. Open **http://127.0.0.1:5000** in your browser.

The pages must be opened through that address. Opening `frontend/index.html` as a plain file does not work, because the app needs the Flask server.

## Run on Linux / macOS
```bash
./start.sh
```
Then open http://127.0.0.1:5000.

## Main features
- Email-based registration and login, password hashing, seven-day sessions, and login-attempt limiting (5 wrong tries per 10 minutes).
- Services and training listings with category filter and smart search in French or English.
- Missions, applications, acceptance, completion and reviews.
- **Reviews on any profile**: rating (1-5 stars) + a written comment about the person's skill, average and star breakdown, edit or delete your own review. Reviews that come from a completed mission carry a "Verified mission" badge.
- **Chat**: conversation list with unread counters, live conversation (new messages appear within ~3 seconds), red dot on the Messages tab.
- **3D meeting map** (OpenStreetMap): see the route between you and another person on a tilted 3D map with extruded buildings, walk / bike / car directions, "Meet halfway" or tap the map to choose a meeting point, send the meeting point in the chat, and a 3D fly-through of the route.
- Profiles with profile picture, skills, portfolio uploads, reports and messages.
- French (default) / English interface toggle.

## Notes
- The app is for local development and demonstration. Do not deploy it publicly without a stable `SECRET_KEY`, HTTPS, a production server, backups and a security review.
- The SQLite database lives in `backend/tasklink.db` (created on first start; older databases are upgraded automatically). Uploaded media lives in `backend/uploads/`. Back up both.
- Sessions stay valid across restarts: a secret key is generated once into `backend/.secret_key`. Set the `SECRET_KEY` environment variable to use your own. Keep that file private.
- Uploaded files are only served to logged-in users, and their content is checked (not only the file extension).

### Profile pictures
Users can upload or replace a profile picture from **Profile → Edit profile**. Supported formats are JPG, PNG and WEBP, with a 5 MB maximum. The picture is stored in `backend/uploads/` under a random name and shown on the profile, on provider profiles, and on service and mission cards.

### Reviews
Open any provider profile: the review form is under **Reviews**. One review per person per provider; sending again edits it. You cannot review yourself. Old databases are upgraded automatically (existing mission reviews are kept).

### Chat
**Messages** lists your conversations; tap one to chat (Enter sends, Shift+Enter adds a line). You can also start a chat by e-mail, or with **Message** on a profile. The page asks the server for new messages every 3 seconds while it is open (no extra software needed).

### 3D meeting map
- **Profile → My meeting place** (or `place.html`): search a place or address, tap the map, drag the pin, or use your current position. Tick *Share* to let people you have chatted with see it. Your place is never visible to anyone else, and only to people you exchanged messages with.
- **Meet · 3D map** (button on a profile and in a chat) opens `route.html`: your place and theirs, the route, distance and time, step-by-step directions. Your phone's GPS position can replace your saved place for that visit (it is not sent to the server).
- The map uses free services built on OpenStreetMap data and needs internet in the browser: map tiles and 3D buildings from OpenFreeMap, the MapLibre GL library from the jsDelivr CDN (unpkg as backup), place search from Nominatim (Cameroon only) and routes from the OSRM servers at routing.openstreetmap.de. These public servers are for light use; for a busy public site, host your own tiles/routing or use a paid provider and change the addresses at the top of `frontend/js/map.js`.

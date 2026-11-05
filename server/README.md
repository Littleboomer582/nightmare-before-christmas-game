# Dead End Depot game server

Your own server for online co-op. The game normally uses free public servers. This gives you a private
one that only carries Dead End Depot games, so you're not at the mercy of a public server being down
or blocked.

It is a small MQTT broker over WebSocket (the same language the game already speaks to the public
servers). It relays only the game's messages, keeps nothing, and caps message sizes and player counts.

## Put it on Render (free)

1. Sign in at [render.com](https://render.com) with your GitHub account.
2. Click **New** → **Blueprint** and pick the `nightmare-before-christmas-game` repository. Choose the
   branch that has this `server` folder and the `render.yaml` file in it.
3. Render reads `render.yaml` and shows one service, `dead-end-depot`, on the **Free** plan. Click
   **Apply** (or **Deploy Blueprint**).
4. Wait for the deploy to finish, then open the service. Its address is at the top, like
   `https://dead-end-depot.onrender.com` (Render may add a few letters to the name).
5. Open that address in a browser. You should see `{"ok":true,"game":"deadenddepot",...}`.
6. Put the address in `zombies.html`: `const NET_OWN_SERVER = 'https://your-address.onrender.com';`
   and rebuild the Android app.

No Blueprint? **New** → **Web Service** works too: pick the repository and branch, then set
**Root Directory** `server`, **Build Command** `npm install`, **Start Command** `node server.js`,
**Instance Type** Free, and under Advanced, **Health Check Path** `/health`.

## How the game uses it

- **Hosting** tries your server first, then the public servers if yours can't be reached. Room codes
  from your server end in its own digit (6), and joiners go straight to it.
- **Free servers fall asleep** after a while with no visitors. The game wakes yours with a web visit
  and waits for it (up to about a minute the first time), saying "Waking up your game server" while
  it does. Opening the Online Co-op screen already starts waking it, so it's often ready by the time
  you press Host. During a game, the game visits it every few minutes so it doesn't nod off.
- Online Co-op's server check lists **Your server** with the others.

## Run it yourself

    cd server
    npm install
    PORT=10000 node server.js

Then use `http://localhost:10000` (or your computer's address) as `NET_OWN_SERVER`.

| Setting | What it does | Default |
|---|---|---|
| `PORT` | The port to listen on (Render sets this for you) | 10000 |
| `MAX_CLIENTS` | Most players connected at once | 200 |

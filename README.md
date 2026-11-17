# Browser Games

Single-file HTML games. Open any of them directly in a browser, no build step needed.

| File | Game |
|------|------|
| `index.html` | This Is Halloween: Jack's Nightmare |
| `rpg.html` | Nightmare Before Christmas RPG |
| `zombies.html` | **Dead End Depot**, a first-person, round-based zombies survival game |

## Dead End Depot

A fan tribute to classic round-based zombie survival, set in a bus depot at the edge of nowhere.
Weapons are real-world firearms; perks, upgraded weapon names, wonder weapons, buildables and art are original and generated procedurally in code (Three.js r128 from cdnjs).

**Goal:** survive as many rounds as you can.

**Performance:** the static world is merged into a few hundred batched meshes, zombies are built from pre-merged parts (small details switch off beyond 14 m), particles, smoke, bullet holes and tracers each draw in one call, shadows refresh every other frame, and the lamp budget depends on the graphics level. Graphics has three levels: High (soft contact shadows, anti-aliasing, flashlight shadows), Medium (the default on computers) and Low (the default on phones). Dynamic Resolution (on by default) renders fewer pixels when frames run slow and recovers when there's headroom.

**Sounds:** gunshots, reloads, zombie groans and attacks, footsteps, impacts, boards, hammering and explosions are real CC0 recordings from OpenGameArt.org (credits in `sounds/CREDITS.md`), with random takes and slight pitch variation. `tools/prepare_sounds.py` rebuilds `sounds/` from the original packs. Any file listed in `sounds/sounds.json` replaces the synthesized sound of the same name (names are listed above `loadSamples()` in `zombies.html`); interface sounds, music and the sci-fi weapons are still synthesized. The Android build bundles the folder automatically.

**Character quotes:** your survivor talks: about 160 original lines for the start of each map, new rounds, multi-kills, headshots, crawlers, getting hurt, being surrounded, running dry, every wall gun, mystery box pulls, perks, power, the Punch Press, doors, buildables and power-ups. They show as subtitles with your survivor name and are spoken by the device's own speech engine (the browser's, or Android's text-to-speech in the app). Lines never repeat back-to-back, important ones wait their turn instead of talking over each other, and chatter leaves a few seconds of quiet. Add or change lines in `QUOTE_LINES` in `zombies.html`.

**Recorded voice lines:** the quotes can be read by a real person. `voice/SCRIPT.md` lists every line to record, grouped by situation with the most-heard first, each with its file name. Recordings go in `voice/`; the game plays a recording whenever one exists for a line and uses the speech engine for the rest, and in a situation with some recordings it picks only the recorded lines so voices don't mix. Lines that name a gun or a round number stay with the speech engine. The radios and the farmhouse whisper can be recorded too. `tools/voice.js` (needs ffmpeg) does the work:

- `node tools/voice.js script` regenerates `voice/SCRIPT.md` after lines change. File names come from each line's first words, so adding or reordering lines doesn't break recordings.
- `node tools/voice.js split <recording> <section>` cuts one long take of a script section (lines read top to bottom, two seconds of silence between them) into a file per line. `--order=1,2,2,3` handles a re-read line: the later take wins.
- `node tools/voice.js clean <recording> <file name>` cleans up one single-line recording.
- `node tools/voice.js index` rewrites `voice/voice.json`, the list the game loads (split and clean do this for you).
- `node tools/voice.js lines` prints every recordable line with its file name, for matching recordings that came in without names.

Own lines are welcome too: add the text to the situation's list in `QUOTE_LINES`, then `clean` the recording under the file name `lines` gives it. The script marks recorded lines with ✅.

Every recording is cleaned the same way: rumble and hiss reduced, silence trimmed from both ends, loudness evened out, saved as a small mono MP3. The Android build copies `voice/` into the app.

**Realism:** screen-space ambient occlusion, rain-slick wet patches that reflect the lamps, large-scale surface variation, galvanised chain-link fences, and realistic zombies that stagger when hit, fall away from the shot, lose arms and become crawlers when their legs go. Guns climb and kick under recoil, sway as you turn, leave bullet holes and smoke; you'll see a red arc pointing at whatever hit you. Zombie groans and footsteps are positioned in 3D, gunfire echoes indoors, and your footsteps change with the surface.

**Zombies:** human proportions and sculpted faces (deep sockets with cloudy, bloodshot eyes, a nose and ears, cracked lips, a jaw that hangs open on ragged yellow teeth, blood down the chin, stubble, bites and scalp wounds), hair or hats, bony hands. Skin and clothes are painted when a match loads, each with a normal map (pores, veins, wrinkles, seams, folds) and, for skin, a roughness map so wounds and blood look wet. Every map dresses its dead for the place: bus drivers in uniform and caps, road crews in hi-vis vests, office workers in shirts and ties, nurses in scrubs on Route 9; flannel, overalls and undershirts at Ashgrove Farmhouse; rain slickers and knit sweaters on the pier; miners in coveralls with reflective tape and hard hats in Cold Hollow. Clothes are torn to the skin, soaked in old and fresh blood and grimy at the hem. On Low a zombie costs no more to draw than before.

**Menus:** a title screen over live shots of the map, then a main menu with Solo, Online Co-op, Operator, Leaderboards, Options, Field Manual and Credits. Everything works with the mouse or the keyboard (arrow keys, Enter, Esc).
- **Solo** sets up the match: map, difficulty (Casual, Normal, Hardened) and starting round (1, 5, 10, 15 or 20, with extra starting points). Maps:
  - **Route 9**: the full map, with the depot, bus lot, foggy road and the bus.
  - **Depot Survival**: the depot and bus lot only, with the gate chained shut.
  - **Blackwater Pier**: a foggy fishing harbour. Zombies climb out of the water onto a boardwalk with a bait shop, warehouse, chowder shack and a long T-shaped fishing pier; the power switch is by the lighthouse.
  - **Cold Hollow Mine**: a snowed-in mining camp ringed by cliffs, with log cabins, a bunkhouse, a mess tent, a bonfire and falling snow; the Punch Press waits at the end of a dead-end mine tunnel.
  - **Ashgrove Farmhouse**: classic survival in a ruined stone farmhouse in the marsh. Start in the kitchen, clear the rubble into the parlor (fireplace and the mystery box) and open the barn door. Zombies only get in through the boarded windows of rooms you've opened. No power, perks or buildables: just the wall guns and the box.
  - **Penny Mile Supercenter**: a 24-hour superstore (an original brand) off the interstate. A foggy parking lot with abandoned cars and carts, two smashed entrances, checkout lanes and customer service, tall shelf aisles (toys, housewares, hardware and sports on one side; snacks, canned goods, cereal and baking on the other), a wall of glitching TVs in electronics, glowing drink coolers, the pharmacy, an employees-only stockroom with pallet racking, the power breaker, the Punch Press and an open loading dock, and a fenced garden center with string lights. Zombies come in from the lot, the dock and the garden gate, and find their way through the aisles. All seven buildables; store staff in red polos, shoppers, a manager, a pharmacist and stockers among the dead.
- A loading screen shows the map, mode and a survival tip; press any key to begin, and the location is typed out as the match starts.
- **Options** (saved in your browser): survivor name, mouse sensitivity, invert look, field of view, master volume, menu music (the original, a song of your own, or off; **Choose Menu Song** picks any audio file on your device, which stays on the device and is never part of the game files), character quotes (voice and subtitles, subtitles only, or off), graphics quality and an FPS counter.
- **Pause** (Esc) has Resume, Options, Field Manual, Restart Match and End Game.
- **Game over** shows a scoreboard (score, kills, headshots, downs, accuracy) and saves the run to the local **Leaderboards** (top 10).

- **Barricades:** zombies tear boards off the four depot windows. Hold **F** at a window to rebuild it (+10 points per board).
- **Points:** earn them for hits, kills (more for headshots and knife kills) and repairs. Spend them on:
  - **Wall weapons:** chalk outlines on the walls. Inside: M14 (500), Double-Barrel (500), MP5 (1000), AK-74u (1200). On the depot's lot-side wall: Remington 870 (1500) and M16 (1200, three-round burst). Buy again for ammo.
  - **Mystery box (950):** Galil, FAL, MTAR, Skorpion EVO, M1216, RPD, LSAT, Python, Barrett M82A1, DSR 50, the wall guns, and the wonder weapons: the **Ray Pistol** (an original atomic-age ray gun that fires exploding energy bolts; careful, the splash hurts you up close until it is punched up) and the rarer Arc Thrower.
  - **Debris (750):** clears the south door into the bus lot.
  - **Lot gate (1000):** opens the bus lot onto the road.
  - **Power switch** (by the generator in the lot): powers the perk machines and the Punch Press.
  - **Perks** (hold up to four): Ironhide Ale (more health), Quickhands Cola (fast reload), Doubleshot Draught (faster fire and double damage), Second Wind Soda (one self-revive), Fleetfoot Fizz (run faster, sprint longer), Third Holster Tonic (carry a third gun), Steady Hand Stout (half the spread and recoil, harder headshots), Spark Cider (reloading shocks zombies around you; the emptier the mag, the bigger the shock) and Blastproof Bitters (your own grenades and Ray Pistol splash can't hurt you; grenades hit harder). Route 9 has all nine (six in Depot Survival), and Blackwater Pier and Cold Hollow Mine have all nine too.
  - **The Punch Press (5000):** punches up your current weapon into its stronger version.
- **The road and the bus:** past the lot gate a foggy road runs west and east. A bus shuttles along it, waiting 25 seconds at each stop: walk in through its side door to ride. It turns around at each end of the line, runs over anything in the road, and the horde follows you wherever you go.
  - **Pine Hollow Gas & Motel** (west): pumps under a canopy, a store with the Galil on its wall (1700), and a neon-lit motel row.
  - **Transit Depot** (middle): the depot and bus lot.
  - **Kessler Lumber Mill** (east): an open saw shed with the FAL on its back wall (1600), a workbench, log piles and a logging truck.
- **Buildables:** parts are scattered around the map (shuffled every game). Collect all the parts of an item, then hold **F** at a workbench to build it. Take it from any bench. Route 9 has the first four plus the Nail Gun, Blackwater Pier adds the Spike Strip, Cold Hollow Mine the Boombox Lure, Depot Survival keeps the first three, and Penny Mile Supercenter has all seven:
  - **Riot Shield** (3 parts): blocks 8 hits from the front.
  - **Sentry Turret** (3 parts): press **T** to place it; it fires at zombies for 90 seconds.
  - **Shock Trap** (3 parts): press **T** to place it; it electrocutes up to 25 zombies over 60 seconds.
  - **Gale Cannon** (4 parts): a scrap-built wind cannon carried as an extra weapon (key **3**). Hold fire to drag zombies in front of you into the fan. It heats up while firing and cools when you stop; let it hit 100% and it breaks.
  - **Nail Gun** (3 parts: nail gun, air compressor, air hose): a fully automatic pneumatic nailer carried as an extra weapon. Nails go through up to three zombies and pin each one for a moment. Take a fresh one from a bench once it's empty; the Punch Press turns it into the Railspike.
  - **Boombox Lure** (3 parts: boombox, propane tank, duct tape): press **T** to set it down. It plays a loud beat for 12 seconds and every zombie within about 24 m goes for it instead of you, then the propane goes up and takes them with it. (Online, it draws the host's zombies when the host places it.)
  - **Spike Strip** (3 parts: rake heads, rubber mat, zip ties): press **T** to lay it across your path. Zombies that walk over it get torn up and slowed; it lasts 90 seconds or 40 hits.
  - Worn-out or broken items can be taken again from a bench after 30 seconds.
- **Power-ups** drop from zombies: Max Ammo, Insta-Kill, Double Points, Kaboom (kills everything on screen) and Carpenter (repairs every window).

**On phones and tablets:** touch controls switch on automatically (or force them on or off under Options → Touch Controls). Play in landscape; the game goes fullscreen when it can.
- Left thumb: a floating joystick appears wherever you touch. Push it all the way forward to sprint.
- Right thumb: drag anywhere on the right half to look. Drag from the FIRE button to aim while shooting.
- Buttons: FIRE, AIM (toggle), JUMP, RELOAD, USE (tap, or hold to rebuild and build), KNIFE, NADE, SWAP, PLACE (when carrying a turret or trap) and pause.
- A gentle aim assist eases your view onto a nearby zombie while you fire or aim.
- In the menus, tap a setting's row to step forward through its choices, or the **‹** in front of the value to step back. On a phone held sideways the list and its info card sit side by side and each scrolls on its own.
- Phones start on the Low graphics setting.

**Controls:** WASD move · Shift sprint · Space jump · Mouse aim · LMB fire · RMB aim down sights · R reload ·
F/E interact · V knife · G grenade · T place turret/trap · Q/1/2/3/wheel switch weapon · Esc pause.

**Reloads:** every gun reloads its own way, animated in first person with your support hand doing the work: rifles and SMGs drop the magazine, seat a fresh one and rack the charging handle; snipers swap the magazine and work the bolt; machine guns swap the box; the pistol drops its magazine out of the grip and racks the slide; the revolver swings its cylinder out, dumps the brass and takes a speedloader; pump and auto shotguns are fed shell by shell and racked; the double-barrel breaks open; the Ray Pistol's glowing cell is lifted out and a fresh one charges up; the Arc Thrower swaps its battery. Magazine guns keep the recorded reload sound; the rest have sounds timed to the motion. Quickhands Cola speeds the whole animation up.

**Operator:** design your survivor from the main menu: jacket colour and pattern (plain, woodland camo, digital camo, tiger stripe, hi-vis stripes, plaid), pants, skin tone, headgear (beanie, cap, helmet, hood, headband), face (bandana, gas mask, goggles, skull mask, war paint), gloves, backpack and name colour, with a 3D preview you can drag to turn and a Randomize button. Your sleeves and gloves show in first person, and online your teammates see the whole operator with your name in your colour.

**Secrets:** every map hides three small objects; find them all and an original song starts (four songs, each in its own style, played live by the game's own synthesizer: drums, bass, distorted guitar and a lead). Each map also has a radio with a piece of the story, the farmhouse has a clock you shouldn't wind, and there are two menu cheats (Big Head Mode and Confetti Mode). Objects you're close to give off a faint chime. The Field Manual keeps track of what you've found and gives a hint for each secret you haven't.

## Online co-op

Up to four players on any mix of phones (the Android app) and browsers. One player picks **Online Co-op → Host a Game** and reads out the 5-character room code; the others type it under **Join Game**. Players can also join a match that has already started.

- **How it connects:** free public servers out of the box, or your own.
  - **Your own server (optional):** `server/` is a small game server made for free hosting on Render (`render.yaml` sets it up; steps in `server/README.md`). Put its address in `NET_OWN_SERVER` in `zombies.html` and hosts use it first, waking it if it fell asleep, with the public servers as a fallback. Its room codes end in 6.
  - **Android app and normal browsers:** players exchange small messages through free public MQTT brokers over secure WebSockets (HiveMQ, EMQX, Eclipse Mosquitto's test server, shiftr.io and the Eclipse IoT sandbox on port 443). The host tries them all at once and takes the first to answer; the room code's last digit (1–5) tells joiners which. Both sides only make outgoing connections, so it works on mobile data and home Wi-Fi without port forwarding. If nothing answers, the message names each server and what went wrong. The brokers are public: anyone who knows a room code could see that room's messages, which only carry game data and player names.
  - **The claude.ai page:** pages on claude.ai can't reach outside servers, so there the game uses claude.ai's own live rooms instead (codes ending in 0). Everyone needs access to the page (Share, then invite them). Players on the page and players in the app can't be in the same game.
- **Who runs what:** the host's game runs the zombies, rounds, doors, power, boards, power-ups and the bus, and sends a snapshot about 8 times a second. Everyone runs their own player, guns, perks, mystery box and buildables, and sends their hits to the host, which decides kills and credits the points to whoever made them.
- **Shared:** doors, power, window boards, power-ups (they apply to everyone) and the round. **Your own:** points, guns, perks and buildables.
- **Downs:** at zero health you go down instead of dying. A teammate holds F (or USE) next to you for 3 seconds to revive you; after 30 seconds you bleed out and come back at the start of the next round. If everyone is down at once, the game is over. Second Wind Soda still revives you on the spot.
- **Zombies** chase whichever standing player is nearest, and rounds have 50% more zombies for each extra player.
- The host's game must stay open and on screen: if the host leaves, the game ends for everyone.

## Android app

`android/dist/DeadEndDepot.apk` is the game packaged as an Android app (Android 7.0 or newer). It runs full screen in landscape, works completely offline (three.js and the fonts are bundled inside), keeps your settings and leaderboard, and uses the touch controls. The Back button pauses during play, steps back through menus, and exits from the title screen.

**Installing:** copy the APK to your phone (or download it from GitHub on the phone) and open it. Android asks you to allow installs from that app (your browser or Files) the first time; Play Protect may warn that the app is from an unknown developer, choose to install anyway.

**Rebuilding:** `android/build.sh [versionCode] [versionName]` rebuilds it from `zombies.html`. It doesn't need the Android SDK: it compiles `android/app/src` with the JDK against Android's API stubs, converts it with `dx`, writes the binary manifest and resource table itself (`android/tools/apk.py`), and signs with Google's `apksig` (`android/tools/Sign.java`), all fetched from Maven Central and npm. The signing key lives in `android/keystore/` (not committed); Android only installs an update over an existing install when it is signed with the same key.

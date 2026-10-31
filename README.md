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

**Realism:** screen-space ambient occlusion, rain-slick wet patches that reflect the lamps, large-scale surface variation, sculpted zombies (gaunt faces, ribcage torsos, fingers, ragged clothes) that stagger when hit, fall away from the shot, lose arms and become crawlers when their legs go. Guns climb and kick under recoil, sway as you turn, leave bullet holes and smoke; you'll see a red arc pointing at whatever hit you. Zombie groans and footsteps are positioned in 3D, gunfire echoes indoors, and your footsteps change with the surface.

**Menus:** a title screen over live shots of the map, then a main menu with Solo, Leaderboards, Options, Field Manual and Credits. Everything works with the mouse or the keyboard (arrow keys, Enter, Esc).
- **Solo** sets up the match: map, difficulty (Casual, Normal, Hardened) and starting round (1, 5, 10, 15 or 20, with extra starting points). Maps:
  - **Route 9**: the full map, with the depot, bus lot, foggy road and the bus.
  - **Depot Survival**: the depot and bus lot only, with the gate chained shut.
  - **Blackwater Pier**: a foggy fishing harbour. Zombies climb out of the water onto a boardwalk with a bait shop, warehouse, chowder shack and a long T-shaped fishing pier; the power switch is by the lighthouse.
  - **Cold Hollow Mine**: a snowed-in mining camp ringed by cliffs, with log cabins, a bunkhouse, a mess tent, a bonfire and falling snow; the Forge waits at the end of a dead-end mine tunnel.
- A loading screen shows the map, mode and a survival tip; press any key to begin, and the location is typed out as the match starts.
- **Options** (saved in your browser): survivor name, mouse sensitivity, invert look, field of view, master volume, menu music, graphics quality and an FPS counter.
- **Pause** (Esc) has Resume, Options, Field Manual, Restart Match and End Game.
- **Game over** shows a scoreboard (score, kills, headshots, downs, accuracy) and saves the run to the local **Leaderboards** (top 10).

- **Barricades:** zombies tear boards off the four depot windows. Hold **F** at a window to rebuild it (+10 points per board).
- **Points:** earn them for hits, kills (more for headshots and knife kills) and repairs. Spend them on:
  - **Wall weapons:** chalk outlines on the walls. Inside: M14 (500), Double-Barrel (500), MP5 (1000), AK-74u (1200). On the depot's lot-side wall: Remington 870 (1500) and M16 (1200, three-round burst). Buy again for ammo.
  - **Mystery box (950):** Galil, FAL, MTAR, Skorpion EVO, M1216, RPD, LSAT, Python, Barrett M82A1, DSR 50, the wall guns, and the wonder weapons: the **Ray Pistol** (an original atomic-age ray gun that fires exploding energy bolts; careful, the splash hurts you up close until it is forged) and the rarer Arc Thrower.
  - **Debris (750):** clears the south door into the bus lot.
  - **Lot gate (1000):** opens the bus lot onto the road.
  - **Power switch** (by the generator in the lot): powers the perk machines and the Forge.
  - **Perks:** Ironhide Ale (more health), Quickhands Cola (fast reload), Doubleshot Draught (faster fire and double damage), Second Wind Soda (one self-revive).
  - **The Forge (5000):** upgrades your current weapon to its stronger version.
- **The road and the bus:** past the lot gate a foggy road runs west and east. A bus shuttles along it, waiting 25 seconds at each stop: walk in through its side door to ride. It turns around at each end of the line, runs over anything in the road, and the horde follows you wherever you go.
  - **Pine Hollow Gas & Motel** (west): pumps under a canopy, a store with the Galil on its wall (1700), and a neon-lit motel row.
  - **Transit Depot** (middle): the depot and bus lot.
  - **Kessler Lumber Mill** (east): an open saw shed with the FAL on its back wall (1600), a workbench, log piles and a logging truck.
- **Buildables:** thirteen parts are scattered across the depot, the bus lot, the gas station and the mill (shuffled every game). Collect all the parts of an item, then hold **F** at a workbench (depot, bus lot or mill) to build it. Take it from any bench:
  - **Riot Shield** (3 parts): blocks 8 hits from the front.
  - **Sentry Turret** (3 parts): press **T** to place it; it fires at zombies for 90 seconds.
  - **Shock Trap** (3 parts): press **T** to place it; it electrocutes up to 25 zombies over 60 seconds.
  - **Gale Cannon** (4 parts): a scrap-built wind cannon carried as an extra weapon (key **3**). Hold fire to drag zombies in front of you into the fan. It heats up while firing and cools when you stop; let it hit 100% and it breaks.
  - Worn-out or broken items can be taken again from a bench after 30 seconds.
- **Power-ups** drop from zombies: Max Ammo, Insta-Kill, Double Points, Kaboom (kills everything on screen) and Carpenter (repairs every window).

**On phones and tablets:** touch controls switch on automatically (or force them on or off under Options → Touch Controls). Play in landscape; the game goes fullscreen when it can.
- Left thumb: a floating joystick appears wherever you touch. Push it all the way forward to sprint.
- Right thumb: drag anywhere on the right half to look. Drag from the FIRE button to aim while shooting.
- Buttons: FIRE, AIM (toggle), JUMP, RELOAD, USE (tap, or hold to rebuild and build), KNIFE, NADE, SWAP, PLACE (when carrying a turret or trap) and pause.
- A gentle aim assist eases your view onto a nearby zombie while you fire or aim.
- Phones start on the Low graphics setting.

**Controls:** WASD move · Shift sprint · Space jump · Mouse aim · LMB fire · RMB aim down sights · R reload ·
F/E interact · V knife · G grenade · T place turret/trap · Q/1/2/3/wheel switch weapon · Esc pause.

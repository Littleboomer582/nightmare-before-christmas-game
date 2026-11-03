# Games

Single-file browser games — open any `.html` file in a desktop browser.

| File | Game |
|---|---|
| `index.html` | This Is Halloween: Jack's Nightmare |
| `rpg.html` | Nightmare Before Christmas RPG |
| `the-quiet.html` | **The Quiet: Patient 0-12** — first-person survival horror |

## The Quiet: Patient 0-12

You wake in the sealed sub-level of St. Ambrose Memorial. A mystery virus, **H-12**, has turned
the patients into the "quiet ones": they stop talking, stop sleeping, then get back up.
You have no gun, but there are melee weapons to find. Climb out through three areas, find the 7 documents that reveal what H-12
really is (and why you're still alive), and escape before dawn. The ending depends on how much
of the truth you uncover.

**Areas**
1. **Sub-Level B: Isolation Ward.** Find the Director's keycard to open the exit. Taking it sets off the alarm.
2. **Sub-Level C: Maintenance Tunnels.** Throw three breakers to power the service lift. Each one is loud.
3. **Ground Floor: Main Lobby.** Find Dr. Rowe, then reach the ambulance bay before the building is sterilized.

**Cutscenes:** waking up on the gurney, leaving the ward, a lift ride with something on the roof,
the Dr. Rowe reveal, the escape at dawn, and death. If a zombie kills you, you're pulled to the floor:
it bends over you and bites while the others close in, and your heartbeat fades out. Press Space to skip any of them.
If you die, you can retry from the start of the current area.

**Controls:** WASD move · mouse look · Shift sprint · C crouch/hide · Space hold breath · click swing weapon · F flashlight · E read/use/pick up · Esc pause · Space skip cutscene

- Bars for health, **infection** (bites raise it; your immune system slowly clears it, and above 75% it drains your health), flashlight battery and stamina
- **Melee weapons** are hidden in every area: lead pipe, crowbar, pipe wrench and fire axe. Hits stagger zombies and knock them back, and enough hits kill them.
  You carry one weapon at a time. Picking up another drops the one you're holding. Each has its own damage, speed and durability, and breaks when it wears out.
  Every swing costs stamina and makes noise, so running away is often still the better choice.
- **Crouch and hide.** Press C to crouch: you move slowly and silently and are harder to spot. Crawl under gurneys, workbenches and desks to hide.
  Zombies that lose you go to where they last saw you and search, sniffing around. If they saw you crawl in, they drag you out.
  Your breathing can give you away, so hold Space to hold your breath. Hold it too long and you gasp out loud.
- Sometimes a shadow figure with red eyes stands at the far end of a hall. It's never there when you get close.
- Zombies hunt by sight, flashlight and running footsteps. Break line of sight to lose them, and sprint to outrun the fast ones.

**What makes it feel real**
- Zombies have human anatomy: knees, elbows, fingers and a hanging jaw. Skin is mottled and veined, faces have sunken eyes and a bloody mouth, and clothes are torn and blood-soaked.
- They move in different ways: shambling, limping, sprinting and crawling. Crawlers can see you under furniture. Some of the corpses on the floor get up when you walk past.
- Moans are made by shaping a throat-like tone into vowel sounds, so they sound human. You'll also hear distant sobbing and knocking.
- Your flashlight casts real shadows, lags and trembles like a hand holding it, and lights up dust in the beam.

Uses Three.js (r128). All textures and audio are generated in code. Headphones recommended.

## Android app

`dist/the-quiet.apk` is a ready-to-install Android build: offline, fullscreen and landscape, for Android 7.0 and newer.
Copy it to your phone, open it, and allow "install unknown apps" when asked.

On touch screens:
- Left thumb: joystick. Push it past the ring to run.
- Right thumb: drag to look.
- Buttons: Swing, Use, Crouch, Hold breath, Light. Android's Back button pauses the game.

The same touch controls also work if you open `the-quiet.html` in a mobile browser.

To rebuild the APK (needs a JDK, curl and zip; the Android build tools download automatically on first run):

```bash
./android/build-apk.sh
```

The script signs the APK with `android/debug.keystore`, creating it if it's missing. The keystore is not committed to git, so keep a copy if you want later builds to install over an earlier one.

---
human-contributors: Jonny Kram
ai-contributors: [Claude]
date: 2026-05-11
---

# Project notes

## Display condition (May 2026)

The Inky pHAT panel is significantly damaged. Root cause: stored for approximately 4 years with a static image on it, powered off.

**Symptoms observed:**
- Two dead/unreliable bands: left edge (~columns 0-14px) and a middle band (~columns 109-120px)
- Black pigment barely responds -- very faint rendering, fine text almost invisible
- Red pigment splotchy, bleeds heavily, cannot render fine detail
- White migration still works correctly
- Inverted rendering (white text on black background) is more legible than normal

**Why this happens:**

E-ink displays use charged pigment particles in microcapsules. Black particles are negatively charged; white are positively charged. In a 3-colour panel, red adds a third charge system. After years of static display, the surface coatings on the black particles oxidise and the particles agglomerate. They lose electrophoretic mobility and stop responding to the electric field. White particles are more stable and still migrate correctly, which is why shading to white works but darkening doesn't.

**Could it have been prevented?**

Partially. Clearing the display to white before extended storage would have reset particle positions rather than leaving them stranded at extremes. GooDisplay's guidelines recommend storing in a white state and refreshing at least every 24 hours. That said, 4 years of storage would have caused some pigment degradation regardless.

**Recovery attempts:**

572 full flush cycles run before these notes were written. Marginal improvement only. Recovery of this level of degradation is unlikely -- the particle charge itself appears irreversibly lost.

**State at handoff:**

- Display flushed to white before power-off (2026-05-11)
- Pi Zero running, SSH accessible at `pi0.local` (user: `jdkram`)
- Flask server deployed to `/home/jdkram/rpi-zero-display/`, running as `rpi-display` systemd service
- Server endpoints: `/date`, `/task`, `/calendar`, `/test`, `/test/sizes`, `/test/solid/<white|black|red>`, `/health`
- `make deploy` from this directory syncs and restarts the service

**If picking this up again:**

Consider replacing the panel. Pimoroni sells replacement Inky pHAT panels. The server code is fully functional -- a new panel would work immediately with no code changes.

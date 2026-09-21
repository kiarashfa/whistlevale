# Briarwatch dragon

Art direction and public credit: **nickfromlater**, with Codex assistance.
The drab seated dragon was reconstructed with [TencentARC Pixal3D](https://huggingface.co/TencentARC/Pixal3D) from a generated anatomical reference, then cleaned, fitted, rigged and animated in Blender. It replaces the earlier procedural dragon. Pixal3D's model card identifies its license as MIT; no model weights or provider code are bundled. Generation revisions and asset hashes are recorded in `provenance.json`.

`briarwatch-dragon.blend` is the packed, editable source, saved with Blender 5.1.1. It includes the generated surface and original 4096px coat, an articulated mandible with authored mouth lining and teeth, 38 deform bones, nine animator controls, and four two-joint planted-leg IK constraints. The feet fit the actual keep roof. Body, ribs, three neck segments, jaw, wings and the curled tail have separate controls. Broad surfaces were simplified while preserving facial and sole vertices.

**Quiet watch** and **Perched fire ritual** are editable 20-second actions. The ritual has an intake, a continuously moving braced exhale, and a recovery. There is no flight. The native room samples both actions at 12 Hz and interpolates poses; the ritual starts 20 seconds after entry and repeats every 120 seconds. Ignition begins seven seconds into the ritual. Pause and reduced motion use the existing room controls.

Model space faces +X with Blender Z up; export converts `(x,y,z)` to `(x,z,-y)`. The saved rig owns its authored perch transform. The browser consumes the same pose for color, shadow and map passes. One 2048px delivery coat is shared across the three draw palettes. The existing limits remain: fewer than 16,000 indexed vertices, 60,000 expanded triangle vertices, and 24 bones per draw. `export-report.json` records measured counts and hashes.

Export from the saved source, without rebuilding or regenerating geometry:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background \
  models/briarwatch-dragon/briarwatch-dragon.blend --python-exit-code 1 \
  --python models/briarwatch-dragon/export.py
```

Edit the rig/actions directly in Blender, or adjust `animation-direction.json` and write a separate animation candidate:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background \
  models/briarwatch-dragon/briarwatch-dragon.blend --python-exit-code 1 \
  --python models/briarwatch-dragon/animate.py -- \
  --output evidence/briarwatch-dragon/animation-candidate.blend
```

The animation script preserves geometry and writes to the requested candidate path. Inspect that candidate before replacing the source. The former procedural builders were retired so they cannot overwrite this generated asset. Neither ordinary editing nor export requires Hugging Face credentials, GPU jobs, or new generation.

Read-only studio review:

```sh
/Applications/Blender.app/Contents/MacOS/Blender --background \
  models/briarwatch-dragon/briarwatch-dragon.blend --python-exit-code 1 \
  --python models/briarwatch-dragon/review.py
```

The fire retains its turbulent jet, cooling edges, smoke, embers and scoped light. Particle positions use the muzzle pose at emission, so moving the head does not drag old fire. This is an authored effect, not a fluid simulation. No generated recordings are bundled.

Run `npm run test:briarwatch` for actual weighted-surface roof contact, clearance, pose continuity, seated motion, the two-minute cadence, render-pass immutability and reduced motion. Studio images do not establish native performance; inspect the room and encoded recordings as well. Resized-browser checks are not physical-phone tests.

See [verification.md](verification.md) for measured checks, capture receipts and delivery limits.

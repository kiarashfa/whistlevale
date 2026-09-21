# Verification — 2026-09-21

The source and exported runtime are identified by the SHA-256 hashes in `export-report.json`. This record describes local checks, not user acceptance or a published release.

## Geometry and animation

| Measurement | Previous procedural source | Generated and rigged source |
| --- | ---: | ---: |
| Indexed vertices | 9,844 | 15,622 |
| Expanded triangle vertices | 54,462 | 41,604 |
| Deform bones | 28 | 38 |
| Draw palettes | 2 | 3 |
| Runtime script bytes | 1,861,717 | 5,145,424 |

The existing 16,000 indexed / 60,000 expanded vertex and 24-bone-per-draw limits remain unchanged. The new runtime includes its shared 2048px coat and denser editable animation samples; this increases download size.

Actual exported soles were checked against the keep's roof triangles every 0.25 seconds across the 120-second cycle. Clearance was 0.008999–0.009006 room units and maximum sole drift was 0.000001708. Every weighted surface vertex was checked every 0.5 seconds across both actions; the pose was evaluated at 60 Hz across the full cycle. Both action seams and the loop seam passed. Four simulated minutes produced exactly two ignitions. Folded-wing weights, actual lip opening, joint-edge stretching, historical fire emission, reduced motion and render-pass immutability passed.

The packed Blender rig also passed a planted-leg control test: raising the chest moved the elbows while foot drift remained below 0.0000003. Exporting the saved public `.blend` reproduced the recorded runtime hash. The documented animation command completed successfully and wrote a separate ignored candidate.

## Project checks

- `npm test` — passed, including the public build.
- `npm run test:geometry:full` — passed: 501 meshes, 12,148,698 vertices, 145,784,376 Float32 attributes bitwise identical between reference and optimized geometry builders.
- `npm run check:contributions -- --json` — passed: 11 works, three workshop pieces, nine trains.
- `git diff --check` — passed.

Detailed logs and the measured contribution report are in ignored `evidence/briarwatch-dragon/pixal/final-*` files. No persistence schema or credit identity changed.

## Native views and recordings

Inspected the final source in the native WebGL renderer at desktop size and in 390px and 320px browser frames. Checked the house map, drab rest/intake pose, planted feet, open jaw, wing roots, curved tail, the fire performance, locomotive smoke and masonry/roof filtering. Standard app Views and Atmosphere controls and the native night view were also checked. The original local-time mood preference was restored. These are resized-browser checks, not physical-phone checks.

Recorded a complete 20-second ritual and a 15-second room reel from the same source. Both are H.264, 1920×1080, 30 fps, silent, with 600 and 450 frames respectively. Capture receipts bind the source and video hashes. Inspected decoded phase/shot frames and verified both files play through in Chrome. The castle shot was widened after an encoded review exposed clipped horns, then recaptured and checked again.

The reel and five PNGs covering the room, village, train, castle and dragon were sent by Taildrop to the requested iPhone on September 21. All six transfers reported success and the command exited zero. This confirms transfer, not playback or live performance on the phone.

A local Chrome sample on Apple M4 Pro at 2294×1134, 4× MSAA and 3072px shadows reported about 120 fps, 8.3 ms median / 10.2 ms p95 frame interval, and approximately 3 ms median GPU time while the close view ran. The diagnostics retain the latest 900 frame intervals; this is a single desktop observation, not a before/after speed claim or a live-phone guarantee.

The original room was merged separately in PR #43 at `983cc98dcef963a076d604c5551ca62c3bae52c0`. The dragon revision was held locally while requested. The follow-up branch `codex/briarwatch-perched-dragon` starts from that current `main` commit and carries the final source, without the superseded flight/procedural iterations.

The full `npm test`, `npm run test:geometry:full` and measured contribution audit were rerun successfully in the fresh main-based PR checkout. All 26 code, asset and QA files match the reviewed local revision byte-for-byte; only this verification record differs. The full geometry comparison remains 501 meshes / 12,148,698 vertices / 145,784,376 Float32 attributes; the contribution audit reports `ok: true`, 11 works, three workshop pieces and nine trains.

## Revised room reel

The final 15-second reel uses wide room and castle shots, then town, train and a distant fire finale, with no dragon close-up. A capture-camera depth correction (`near=2`, `far=500`, vertical FOV `.74`, 1920×1080) removes the banner/backing and rug-overlay flicker seen with the earlier `near=.1`, `far=700` projection. This is a recording-adapter correction, not a change to the live application's camera.

The corrected MP4 has 450 native rendered frames at 30 fps, H.264/yuv420p and no audio. Its SHA-256 is `cadacbed54ca66e424cafaa7eff8ca2471d0ac31e7c6aee700b12eb5a629dc9c`. Decoded frames and full Chrome playback were checked. Taildrop reported successful delivery; phone playback remains unverified. Media and capture intermediates remain in ignored evidence, outside source and public builds.

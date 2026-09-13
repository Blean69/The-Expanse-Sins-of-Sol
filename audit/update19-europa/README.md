# Europa's Bane game art derivative

Source: user-supplied `expanse-extracted/OPA-pirate-ships/meshes/Europa_Bane_Exterior_A.gltf` and accompanying bin/material exports. The original files are read-only. This is the Europa's Bane from the Telltale prequel game; no claim that this exact asset appeared in a TV episode or book.

The ship keeps its original hull geometry and UV0. Source engine-cone groups identify aft as source +Z, corroborated by actual geometry renders. The conversion rotates 180 degrees around Y, centers the source bounds, and uses 1.875 game units/metre, matching the current Tachi (42m ->78.75 game units). The source hull spans178.851m, therefore335.346 game units.

Six proven independent base/barrel PDC turrets replace static source guns. Each source replacement is677 triangles. Their supports are measured against the actual hull. The six full-yaw, outward-facing elevation windows passed 1-degree ray samples with a +/-3-degree aim envelope. This is geometric sampling against the static hull, not an engine targeting test or proof of continuous all-pose clearance. Neighbor turret motion and game target acquisition remain untested.

Four engine origins are measured from the actual source engine cones. Two forward torpedo launchers and the shared boarding launcher are derivative placements at measured bow surfaces; exact screen tube correspondence is not claimed. No railgun was invented.

Unreal material graphs do not directly transfer to Sins. The derivative retains original UVs and base-color/normal textures, bakes exposed color/paint parameters as a documented approximation, and uses conservative roughness/metallic response. Shader-dependent decal cards are excluded rather than importing opaque cards. The original RGB-mask layered paint behavior is not reproduced. Source material and texture hashes are recorded separately.

Run geometry, then compilation, then materials. Compilation uses installed MeshBuilder in an isolated Wine prefix. Official MeshBuilder facing-grid trailers are retained; only tangent bytes are repaired from authored frames. Material compilation uses BC7 color/ORM/mask and BC5_SNORM normals with mipmaps. Actual geometry previews are software renders, not game captures.

No installation, faction/gameplay edits, remote push, or runtime claims are part of this worker's output. Integrator uses `integration-spec.json` for private game files, mounts, spatial extents, effects origins and hashes.

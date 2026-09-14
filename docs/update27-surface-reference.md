# 0.27 drive and surface reference pass

The user explicitly requested replacing black printer-like drive stubs with detailed Epstein assemblies taken from existing models, especially the Laconian frigate and Hephaestus. The revised compiled side/stern views have been inspected: the bells are exposed and their short collars connect to the hulls. Sampled muzzle clearance and artifact dependency checks pass.

Design reference: the supplied Paul Kiesling Scirocco renders/material sheets. His [project description](https://paulwk13.artstation.com/projects/Qn3oN8) explains that he used show and production-model references and baked thermal-panel, curvature and ambient-occlusion detail. This supports small thermal tiles and layered surface relief instead of relying on a uniformly painted STL.

The show's designers describe conventional rocket cones and heat-resistant surface tiles in their [North Front interview](https://magazine.artstation.com/2016/02/scenes-concept-art-expanse/). These guide the new surface treatment and exposed drive throats. New textures are authored game assets informed by these references; no scene image is projected indiscriminately onto a ship.

Exact reused mesh donors, extraction transforms, material references and refreshed hashes are recorded in the respective Earth, OPA and Mars/Laconia integration audits. Dense existing hull detail is retained; extra triangles are concentrated in curved bells, throats, collars and geometry that changes the silhouette. Material normal/roughness detail handles small surface features. Live engine lighting and particle appearance remain untested.

The CPU previews use nearest-neighbor texture sampling, which exaggerates fine tile grain and the native donor’s colored wear marks. Final DDS textures include mipmaps; live game lighting remains a playtest check.

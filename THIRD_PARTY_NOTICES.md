# Source and redistribution notices

This repository preserves the user-supplied Mouchak requirements kit and attributed legacy source. Public repository visibility alone does not grant a blanket open-source licence. No umbrella MIT/Apache licence has been applied without the owner's licence decision.

Retain these existing notices when redistributing permitted source:
- Bengali font: public/fonts/ contains the upstream SIL Open Font License and embedded attribution.
- OpenCV Zoo helpers: services/model_worker/vendor/opencv_zoo/LICENSE and NOTICE.
- UI/vendor notices: vendor/shadcn-tailwind-4.13.0.LICENSE.md and scripts/vite/sites-vite-plugin.LICENSE.
- BanglaRead legacy passages: CC-BY-4.0 attribution in data/legacy/banglaread-passages.json.
- Authored learning starter: data/authored/learning.json records its original CC0, nonofficial provenance.
- Full original kit: requirements/original-kit/ retains its own source instructions and notices.

Downloaded models, government datasets and remote source references have separate terms. They are not relicensed by this repository. Model weights and restricted/private datasets are excluded from Git. See docs/DATA_AND_MODEL_PROVENANCE.md and the acquisition manifests for sources, model licences and release gates.


## Advanced continuation assets

- Official Google YAMNet classification TFLite v1 and TensorFlow class map: Apache-2.0; exact primary-source URLs, pinned revision, byte lengths and SHA-256 are in `docs/audit/noise-assets.json`. No original AudioSet recordings are redistributed. LiteRT runtime is installed from the pinned public package.
- Bangladesh OpenStreetMap extract and derived road-name records: © OpenStreetMap contributors, **ODbL-1.0**, <https://opendatacommons.org/licenses/odbl/1-0/>. Source/producer: <https://download.geofabrik.de/asia/bangladesh-261028.osm.pbf>, <https://www.geofabrik.de/data/download.html>. The derived database and public development slice retain ODbL; attribution/coverage/hash records accompany them. This licence does not cover the application's code or master prompts.
- `data/authored/launcher-intents.json`: newly authored development query examples only, CC0-1.0. Not real-user data or an independent holdout. No blanket relicense of the original requirements, brands or third-party content is implied.

Client SHA-256 fallback uses `@noble/hashes@2.4.0` (MIT, Paul Miller), loaded only when browser SubtleCrypto is unavailable in an HTTP development preview. The checksum protocol and server verification remain unchanged. Source/licence: <https://github.com/paulmillr/noble-hashes>.

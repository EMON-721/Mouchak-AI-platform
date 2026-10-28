# Preserve and consolidate the four existing tools

The connected GitHub repository inventory was read. The four existing tool repositories named by the kit were not accessible in that inventory. No external repository, deployment, identity or user database was modified. Three local V3 static snapshots have since been preserved and selected workflow logic ported; see `LEGACY_PORTS.md`.

Pending sources:

| Tool | Central route | Source commit | Migration |
|---|---|---|---|
| ChuktiShield AI | /tools/chuktishield-ai | Remote commit unavailable | No live identity/data migration |
| DokanLens AI | /tools/dokanlens-ai | Remote commit unavailable | No live identity/data migration |
| BazarCompare AI | /tools/bazarcompare-ai | Remote commit unavailable | No live identity/data migration |
| BanglaRead Coach | /tools/banglaread-coach | Remote commit unavailable | No live identity/data migration |

Before import: obtain each exact repository URL and readable branch; record the real commit; export an encrypted database/object backup; inspect identity provider, schema, licenses, queues and existing test evidence. Create a migration branch without altering the old repository. Namespace imported features, preserve original record IDs in an immutable mapping ledger, and link accounts only after verified identity linking and explicit data-transfer permission.

Suggested mapping contract: `legacy_provider`, `legacy_repository`, `legacy_commit`, `legacy_user_id`, `verified_central_user_id`, `legacy_record_id`, `central_record_id`, `consent_id`, `checksum`, `migration_batch_id`, `rollback_reference`. The current implementation contains no fabricated mapping rows.

Run output parity, visual comparison, account continuity, private access and reversible rollback tests before any production redirect. Keep original sites and repositories intact until the owner accepts parity. No force-push, database reset, repository archive or DNS redirect is part of this delivery.

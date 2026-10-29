# Reviewed Site Builder

This is a bounded presentation CMS for the existing 50-tool platform. It does not complete every original advanced tool, model lifecycle or moderation requirement. No production hosting is created by this workflow.

## Operator workflow

1. Open `/admin/site-builder` with a `content_editor` or `super_admin` operator session and MFA verified within 15 minutes. Visitors continue to use the platform without accounts.
2. Edit bilingual brand names/taglines, owned logo/favicon, light/dark palette, type scale, navigation/footer, homepage text/order/featured tools/FAQ, public information pages, category labels, approved UI labels, individual tool names/descriptions/logos/field labels/help/placeholders, and search metadata. Field types/options/required rules, consent, safety, model readiness, processing engines and private data permissions are not editable here.
3. Validate and save a private immutable draft. The visual editor and advanced JSON editor both use the same server schema. Saving a draft never publishes it. Existing legacy CMS branding/content remain active until the first reviewed Site Builder publication; later removing a page override restores the earlier page CMS or built-in copy.
4. Inspect the saved version in the private preview at 390, 768 or 1440 pixels, or open its preview tab. The iframe renders the actual homepage with shared header/footer/theme, not a simulated AI response. The iframe's size creates an actual CSS viewport. Navigation out of the preview restores the published configuration. Previewing removal of a tool override uses the original presentation metadata returned by the API, retaining current operational readiness.
5. A **different** current content editor, with fresh MFA, previews the exact version and records approval or rejection with a reason. Authors cannot approve their own work. A rejected version cannot be edited or approved in place; copy it to the editor and save a new version.
6. Publish an approved version immediately, or schedule it 30 seconds–366 days ahead. The existing `/admin/publishing` console lists outcomes and cancellation. Run `python -m services.model_worker.scheduler` with the dedicated database role in production. At execution time the worker revalidates content, assets, approval hash, current author/reviewer roles, bans, MFA enrollment and the base publication hash. It does not impersonate a human session or weaken the recent-MFA checks on operator requests.
7. Roll back only to a previously published, independently reviewed version. The author and reviewer must still be authorized. The explicit current revision prevents overwriting another editor's intervening publication. Rollback intentionally restores an older base, whereas ordinary drafts must be reviewed against the current published base.

The editor keeps the draft’s base revision separate from refreshed version/asset lists; a background list refresh cannot silently rebase unsaved edits over another editor’s publication. Draft changes remain in browser memory until saved. Reloading published settings intentionally replaces unsaved local edits. Saved versions remain durable in the database. The latest 100 versions and up to 200 asset metadata entries appear in the editor; older version IDs remain directly accessible to authorized operators. This is not an arbitrary HTML/CSS/JavaScript page builder.

## Branding artwork

Upload only an original or otherwise licensed **public brand mark**, accompanied by a credential-free HTTPS licence link, rights explanation and explicit rights attestation. Private tool uploads cannot be repurposed as artwork. An asset attestation is an operator declaration; it is not an external legal verification. Another editor must inspect the declared rights when reviewing its containing site version.

The SVG parser permits a deliberately small static subset: `svg`, `g`, `path`, basic shapes, `title`, `desc` and `text`, in the SVG namespace with a `viewBox`. It rejects scripts, event attributes, external resources, linked images, styles, transforms, XML declarations/entities/DOCTYPE, unknown attributes, excessive nesting/nodes and unbounded geometry. Limits: 30 KB, 300 nodes, 12 levels, finite geometry within ±1,000,000. Complex design files should be simplified to this subset before uploading; unsupported SVG is not silently accepted.

Normalized bytes have immutable SHA-256 identifiers. Draft-only/unreferenced assets require CMS authorization and fresh MFA and return `no-store`; unauthorized requests receive 404. Only assets referenced by the current published configuration are publicly served, with `nosniff` and a sandboxed `default-src 'none'` CSP. Previously public bytes may remain in a client cache for up to five minutes; brand assets must contain no private data. The system never downloads the licence link or arbitrary asset URLs.

## Schema and publication safety

- Defaults: `packages/ui-tokens/site-defaults.json`. Safe locale keys: `packages/ui-tokens/editable-locales.json`.
- Unknown fields, tool IDs, field paths, page IDs, locale keys and external navigation URLs are rejected. Public links must resolve to known platform routes; Explore and legal footer links remain available.
- The hero stays first and the honest readiness/principles section remains visible. Advanced readiness and consent statements are excluded from locale overrides.
- Both themes require at least **4.5:1** contrast for core text/background pairs. The preview preserves the visitor's dark-mode and larger-text controls. This check is not a full accessibility certification.
- Total configuration size is bounded at 120,000 JSON characters. Body text renders through React as plain text; no raw HTML, `dangerouslySetInnerHTML`, remote CSS/font or executable layout is accepted.
- Publication uses a PostgreSQL transaction advisory lock and optimistic published revision/base hash. Review is bound to the immutable body's SHA-256. Generic CMS publication and generic scheduling cannot bypass Site Builder review.
- No new tables or destructive migrations are needed: existing `cms_versions`, `configuration`, publication schedules and append-only audit events are reused. Dedicated scheduler grants already include only the user columns needed for role/reviewer validation.
- Only `/admin/site-preview/*` permits **same-origin** framing. All other pages retain frame denial. Preview API requests independently require CMS authorization and recent MFA. An iframe is not an authorization bypass.
- Public SEO metadata reads only the fixed operator-configured private backend. Failure uses built-in public metadata. Admin and session-work pages remain `noindex` even if indexing is enabled for public pages. Netlify still requires verified HTTPS/internal-token configuration.

## Implemented API

`GET /api/public/site` returns the active revision and validated config. CMS-authorized routes provide state, dry-run validation, draft creation, immutable preview, independent review, guarded publication/rollback and owned SVG ingestion. See [API_REFERENCE.md](API_REFERENCE.md) and `services/model_worker/site_builder.py` for exact routes/schemas.

Tests in `tests/test_site_builder.py` cover privacy, rights attestation, SVG rejection, independent review, stale drafts, revoked roles, scheduler revalidation, rollback, CSRF, schema limits, preserved tool safety and engine-schema immutability. `node scripts/test-site-presentation.mjs` executes the actual presentation helpers to check draft removal of published overrides, bilingual field text, preserved operational gates and safe theme generation. The actual standalone web image test checks narrow same-origin framing and private-page noindex. The real Docker/TLS integration controller also exercises two MFA operators, publication, private/public asset access, actual scheduler execution under its restricted PostgreSQL role and rollback. Its latest CI result is recorded separately; adding a test is not a claim that it passed.

Browser QA remains separate: the current supported preview rendered bilingual public pages, all 50 catalogue entries and filtering. The origin configuration was repaired after a visitor-session failure; a subsequent browser navigation was denied by browser URL security policy. No bypass, alternate browser transport or injected operator session was used. Protected visual-editor/browser MFA, three preview widths, a complete browser inference run and browser PDF acceptance remain unverified in this continuation.

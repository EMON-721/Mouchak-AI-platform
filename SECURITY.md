# Security and private data

Report a vulnerability through the repository's private vulnerability reporting feature when enabled, or contact the repository owner privately through GitHub. Do not include credentials, private files or user records in a public issue. This repository does not declare a public security-response SLA or a production certification.

- No visitor account/signup/profile. Anonymous results use opaque HttpOnly cookies, owner authorization, CSRF and a maximum 24-hour scope.
- Operator permissions require password login and recent TOTP MFA. There is no default administrator password.
- The private service token is server-only. Production rejects missing/short tokens; never use a NEXT_PUBLIC_ variable for a secret.
- Production needs dedicated PostgreSQL roles and verified TLS, encrypted private S3, current scanner signatures and a stable encryption key.
- Development uses encrypted local SQLite/files. It is for owned test inputs, not sensitive public traffic. Experimental pose, speech and private-model mechanics are not production-approved.
- Never commit .env, databases, uploads, model weights, keys, screenshots with credentials, DPAPI/CLIXML exports, recovery archives or private datasets. Model download scripts include checksum/provenance records.
- Rotate exposed credentials through their provider, update consumers and revoke the old login. Removing a screenshot or a Git file does not revoke a secret.
- Run python3 scripts/check-public-source.py --history before publication. The checker reports paths/rules, never matched secret values. It detects selected credential patterns and forbidden runtime artifacts; it cannot certify the absence of every secret or personal identifier.
- Never rewrite shared history or delete existing data merely to pass a scanner. Stop publication, privately rotate an exposed secret, and coordinate any history cleanup with the owner.
- Keep Codespaces port 3000 Private. The development API on 8000 must not be forwarded. Do not make the development server a public production service.

See docs/PUBLIC_ACCESS.md, docs/DATA_AND_MODEL_PROVENANCE.md and docs/DEPLOYMENT.md for the implemented boundaries and remaining controls.

## Bilingual authentication input

Operator TOTP accepts Bengali and ASCII decimal digits. The server canonicalizes digits before verification and replay hashing; switching scripts does not permit replay. Malformed non-ASCII internal-token or CSRF headers return 403 without a string-comparison server error. Passwords and opaque session/CSRF secrets are never language-normalized. These checks supplement the existing recent-MFA, role, origin, CSRF and owner boundaries; they do not certify the unfinished full production scope.

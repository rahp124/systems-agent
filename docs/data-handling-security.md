# Data handling and security review

This repository is prepared only for approved, de-identified offline replay data. It does not accept credentials, connect to SCADA, or expose any control-operation interface.

## Minimum data handling rules

- Transfer data only through a collaborator-approved channel; do not attach exports to issues, commits, pull requests, or public artifacts.
- Keep raw exports outside version control in an ignored, access-restricted local directory. Track only aggregate reports, source checksums, retrieval times, and approved schemas.
- Remove direct identifiers, account/contact information, exact location data, and free-text fields unless the data owner explicitly approves their retention for the stated analysis.
- Use an approved retention period, access list, deletion procedure, and incident contact before receiving data.
- Do not copy partner data into prompts, external tools, logs, screenshots, or third-party services without explicit approval.

## Technical controls to verify with a collaborator

| Area | Required check |
| --- | --- |
| Access | Named users, least privilege, separate nonproduction environment, and no actuator-network route. |
| Integrity | Export checksum, immutable source copy, timestamp ordering, explicit channel map, and versioned policy/configuration. |
| Confidentiality | Encryption in transit and at rest per collaborator policy; approved storage location and access review. |
| Audit | Append-only advisory ledger, reviewer disposition record, access logging, retention/deletion evidence. |
| Incident response | Named security and operational contacts, escalation route, revocation procedure, and reporting timeline. |

## Pre-transfer checklist

1. Data owner approves purpose, fields, de-identification method, transfer path, retention, and deletion.
2. Technical owner approves the read-only offline scope and confirms no controls or production credentials are involved.
3. Security owner approves storage, access, logging, and incident-response controls.
4. The analysis owner records the approved channel map and validation protocol before opening the export.
5. On completion or at retention expiry, delete raw copies under the agreed procedure and retain only permitted aggregate evidence.

These controls are preparation material, not a certification or a substitute for a utility's security, privacy, legal, or regulatory requirements.

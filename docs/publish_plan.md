# Phase 9 — Publication TikTok: Conception & Plan

Objectif: fournir un client `app.publish` et un `PublishStage` pour envoyer des vidéos produites vers TikTok de manière sûre, idempotente et testable.

1) Endpoints & flux (options selon API TikTok)
  - Upload endpoint (multipart): `/upload/video` (provider-specific)
  - Publish endpoint: `/video/publish` (initiate/confirm)
  - Status/check endpoint: `/video/status` (poll pour état)

2) Permissions & scopes
  - Clés d'API OAuth2 ou token d'application
  - Permissions: upload media, publish content, read status

3) Idempotence
  - Générer `external_id` stable (p.ex. `script_id` + `sha256` des métadonnées)
  - Stocker mapping `external_id -> post_id` dans la DB pour éviter doublons
  - `PublishClient.publish()` doit accepter `dry_run` et `idempotency_key`

4) Rétries et backoff
  - Utiliser retries exponentiels pour erreurs 5xx et timeouts
  - Ne pas retry 4xx sauf erreurs transitoires documentées

5) Sécurité
  - Ne pas logguer les clés en clair
  - Supporter `.env` et intégration avec Vault (optionnel)

6) Tests
  - Unit tests: mocker les réponses HTTP (requests-mock / pytest-mock)
  - Integration gated: `RUN_PUBLISH_TESTS=1` (exécuté manuellement avec vraies clés)

7) Schema client (`app.publish`) — méthode publique minimale
  - `PublishClient(upload_url, api_key, timeout=30)`
  - `upload_video(file_path, metadata) -> upload_token` (multipart)
  - `publish(upload_token, idempotency_key) -> post_id`
  - `get_status(post_id) -> status`

8) Pipeline integration
  - `PublishStage` lit `context.current_video` et `context.current_script` puis appelle `PublishClient`
  - Mettre à jour le script/topic en base (`published`, `published_at`, `post_id`)

9) Métriques & monitoring
  - compter succès/erreurs, latence d'upload, échecs d'auth

10) Checklist de sécurité avant test réel
  - Créer compte test TikTok / sandbox
  - Protéger les clés dans `.env` et CI secrets

---
Fichier de suivi: ajoutez `docs/publish_plan.md` au dépôt pour garder l'historique des décisions.

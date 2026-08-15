# TODO - TikTok-Automation

## Phases de migration

- [x] Phase 1 — Créer l'architecture pipeline
- [x] Phase 2 — Migrer la base de données
- [x] Phase 3 — Migrer le collecteur RSS
- [x] Phase 4 — Migrer le scoring (Ollama)
- [x] Phase 5 — Migrer la sélection des sujets
- [x] Phase 6 — Migrer le générateur de scripts
- [x] Phase 7 — Génération média (voix/images/sous-titres)
- [x] Phase 8 — Rendu vidéo (placeholder)
- [ ] Phase 9 — Publication TikTok (global)

## Tâches techniques (Phase 9 & remédiations)

- [ ] Phase 9.1 — Conception API TikTok & flux (endpoints, permissions, scope, idempotence)
- [ ] Phase 9.2 — Spécification du client `app.publish` (interface, retries, timeouts)
- [ ] Phase 9.3 — Gestion des secrets & `.env.example` (FFMPEG_PATH, TIKTOK_* , RUN_* flags)
- [ ] Phase 9.4 — Implémenter `PublishStage` et intégration pipeline
- [ ] Phase 9.5 — Tests unitaires mockés pour `app.publish` et `PublishStage`
- [ ] Phase 9.6 — Test d'intégration gated (`RUN_PUBLISH_TESTS=1`) et playbook de sécurité
- [ ] Phase 9.7 — Idempotence & marqueurs DB (éviter doublons)
- [ ] Phase 9.8 — CI / workflows: gate network/render/publish tests, runner deps

- [ ] Remediation M1 — Remplacer placeholders media (edge-tts, image generator) par implémentations optionnelles
- [ ] Remediation M2 — Implémenter wrapper `ffmpeg` dans `app/media/renderer.py` (production-ready)
- [ ] Remediation M3 — Mettre `requirements.txt` en UTF-8 et ajouter extras (`ffmpeg-python` optional, edge-tts`)

## Documentation & utilitaires

- [ ] Docs — Mettre à jour `README.md` et ajouter `docs/running.md` (+ exemples de commandes)
- [x] Publish plan: `docs/publish_plan.md`
- [x] `.env.example` ajouté

## Notes
- Les tests sont exécutés localement : `16 passed, 2 skipped`.
- Les placeholders media et le client de publication sont présents comme stubs pour développement et tests mockés.

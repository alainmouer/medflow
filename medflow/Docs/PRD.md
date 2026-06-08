## MedFlow — Product Requirements Document (PRD)

**Version :** 1.0 — Greenfield
**Date :** Juin 2026
**Statut :** Source de vérité unique du projet MedFlow
**Plateforme médicale SaaS multi-tenant — IA autonome & transversale — Médecine ambulatoire**
**Multi-support : Ordinateur · Tablette · Smartphone**

---

## Table des matières

1. Vision & Positionnement
2. Principes Fondateurs
3. Architecture Technique
4. Gouvernance IA
5. Modules Fonctionnels
6. Fonctionnalités Transversales
7. Sécurité & Conformité
8. Internationalisation (i18n FR/EN)
9. Décisions Actées & Points en Suspens
10. Annexe — User Stories & Critères d'Acceptation
11. Roadmap (Phases 1–10 + VC + VInt)
12. Modèle de Données — 20 entités
13. Inventaire API — 40+ endpoints
14. Matrice RBAC — 7 rôles × tous les modules
15. Accessibilité WCAG 2.1 AA

---

## 1. Vision & Positionnement

### Nom du projet

MedFlow (M et F en majuscules).

### Tagline

> *« MedFlow — Plateforme médicale intelligente »*

### Concept

MedFlow est une plateforme médicale SaaS de nouvelle génération, conçue pour repenser fondamentalement le parcours de soins en médecine ambulatoire. Elle combine la gestion complète du cabinet médical avec une intelligence artificielle autonome et transversale, permettant un gain de temps significatif pour le personnel médical et paramédical, tout en améliorant la qualité et la continuité des soins.

MedFlow orchestre :

- La **gestion multi-rôles** des utilisateurs et de leurs droits d'accès
- Un **parcours de soins asynchrone** complet (de la collecte terrain à la validation médicale)
- Des **règles de cohérence physiologique** automatiques (moteur de règles embarqué)
- Une **interface de validation IA côte à côte** (vue diff sources / propositions IA)
- Une **planification unifiée** (agenda + missions terrain + triage)
- Des **ordonnances numériques** avec signature électronique
- Un **export PDF** structuré des épisodes de soin

### Positionnement

MedFlow n'est pas un simple logiciel de gestion de cabinet. C'est une plateforme de soins augmentée qui intègre nativement l'IA dans chaque étape du parcours patient, de la prise de rendez-vous jusqu'au suivi post-consultation et la facturation.

### Cible & Trajectoire de déploiement

MedFlow suit une trajectoire de déploiement en trois phases distinctes :

| Phase | Contexte | Utilisateurs | Hébergement | Certification |
|---|---|---|---|---|
| **Version Initiale (VI)** | Cabinet médical du fondateur (cardiologue) | Médecin + équipe interne (secrétaire, infirmière/IPA, assistant médical, patients) | Local / Cloud standard | Non requise (usage interne) |
| **Version Commerciale (VC)** | Expansion vers d'autres structures médicales | Multi-cabinets, multi-tenants | Cloud souverain européen certifié HDS | HDS obligatoire + RGPD renforcé |
| **Version Internationale (VInt)** | Expansion géographique hors France | Structures médicales internationales | Cloud multi-régions | FDA / HIPAA / PIPEDA selon pays |

> **Principe directeur** : La Version Initiale est conçue pour être **immédiatement et pleinement exploitable** dans un cabinet médical, avec toutes les fonctionnalités nécessaires à la pratique quotidienne. Elle constitue simultanément le **socle technique de la Version Commerciale** : architecture multi-tenant préparée, interfaces d'interopérabilité définies, conformité réglementaire anticipée.

> **Décision de passage VI → VC** : Si l'usage en cabinet valide la plateforme, la migration vers la Version Commerciale ne nécessite pas de refonte — uniquement une migration d'hébergement vers un Cloud souverain HDS, l'activation complète du multi-tenant et l'implémentation des connecteurs d'interopérabilité déjà préparés.

### Modèle économique

- **VI** : Usage interne cabinet — pas de modèle économique externe
- **VC** : Abonnement mensuel ou annuel par tenant (structure médicale)
- Architecture multi-tenant : chaque structure = un tenant isolé et sécurisé (préparée dès la VI, activée pleinement en VC)

### Multi-support

Fonctionnement natif sur ordinateur, tablette et smartphone.

> **Stratégie PWA & Offline-first.** Afin de garantir la continuité des soins sur le terrain (missions à domicile, EHPAD, zones de connectivité limitée), MedFlow adopte une stratégie **Progressive Web App (PWA)** dès la conception :
> - **Stockage local** via IndexedDB pour les formulaires terrain, signatures et photos.
> - **File de synchronisation** automatique à la restauration du réseau (stratégie *Conflict-Aware* — voir §3.6).
> - **Indicateurs visuels de connectivité** : 🟢 En ligne / 🔴 Hors ligne / 🔄 Synchronisation en cours.
> - **Mode dégradé** : saisie manuelle classique conservée même sans IA ni réseau.

### Engagements de service (SLA) — Modalité Asynchrone

Pour la modalité de consultation par **télé-expertise augmentée**, les engagements de traitement suivants s'appliquent dès réception du dossier complet (score de complétude ≥ 70 % et consentement validé) :

| Niveau | Délai | Cas concernés | Badge priorité |
|---|---|---|---|
| **Standard** | 10 jours ouvrés | Bilans de routine, contrôles chroniques | 🟢 Basse |
| **Prioritaire** | 48 heures | Dyspnée, palpitations, douleurs thoraciques atypiques, anomalies ECG non urgentes | 🟡 Moyenne |
| **Urgence détectée** | Immédiat — blocage | Symptômes vitaux critiques détectés par le Bouclier de sécurité | 🔴 Haute |

> **Principe** : MedFlow n'est **pas** un service d'urgence. Les cas vitaux immédiats doivent être orientés vers le 15 avant même l'ouverture d'une consultation.

---

## 2. Principes Fondateurs

### Fluidité maximale

L'application doit permettre un gain de temps significatif à chaque étape du parcours. Chaque interaction est pensée pour être la plus rapide et la plus intuitive possible. L'interface s'appuie sur une palette médicale épurée (dominante blanche, accents bleu ciel `#0EA5E9` et cyan), des transitions douces, des *skeleton loaders* pendant les traitements IA, et une **Command Palette** (`Ctrl/Cmd + K`) pour accéder instantanément à toute fonction.

### L'IA fait, l'humain valide

L'IA fonctionne de manière autonome et automatique. Elle prépare, génère et propose. La validation finale appartient toujours à l'humain — au médecin pour tout ce qui est médical, à l'équipe paramédicale pour tout ce qui est paramédical. Aucune action clinique ne peut être validée sans intervention humaine.

### Délégation médicale structurée

MedFlow est conçu pour optimiser la délégation des tâches médicales vers l'équipe paramédicale (IPA, infirmiers, assistants médicaux), dans le respect du cadre légal. La délégation s'effectue **exclusivement au sein de l'équipe interne du cabinet/tenant**, sans externalisation à des tiers non rattachés.

### Modularité & Personnalisation

Chaque module est activable/désactivable par tenant et par médecin. Les paramètres sont configurables selon la spécialité et les habitudes de travail.

### Continuité des soins

MedFlow assure une continuité totale du parcours patient, de la première prise de contact jusqu'au suivi à long terme, avec un dossier longitudinal unifié.

---

## 3. Architecture Technique

### 3.1 Stack technologique

| Couche | Technologie | Rôle / Justification |
|---|---|---|
| Frontend | Next.js (App Router) | React SSR/SSG, file-based routing, performance |
| Langage frontend | TypeScript | Typage strict |
| Styling | CSS custom + utilitaires maison | Palette médicale épurée |
| Polices | Geist Sans + Geist Mono | Lisibilité |
| i18n | i18next + react-i18next + i18next-http-backend + i18next-browser-languagedetector | FR/EN dynamique |
| Backend | FastAPI (Python) | Intégration native IA/ML — choix validé |
| ORM | SQLAlchemy | Persistance |
| Migrations | Alembic | Versionning DB |
| Base de données | SQLite (dev local) / PostgreSQL (prod, via `DATABASE_URL`) | Voir note ci-dessous |
| Cache & File de tâches | **Redis** | Cache recherche patient, sessions, file tâches async (Celery/ARQ) |
| Base vectorielle | **pgvector** (extension PostgreSQL) | RAG, recherche sémantique — souveraineté garantie, même instance PostgreSQL |
| Authentification | JWT + OAuth2 | Sessions stateless |
| Hash mots de passe | bcrypt | Sécurité MDP |
| PDF | ReportLab | Export épisodes de soin |
| Tests backend | pytest + pytest-cov | Couverture |
| Tests E2E | Playwright (Chromium) | Tests bout en bout |
| CI/CD | GitHub Actions (4 jobs) | backend-tests / frontend-build / alembic-check / e2e-tests |
| Hébergement VI | Local / Cloud standard | Usage cabinet interne |
| Hébergement VC | Cloud souverain européen certifié HDS | RGPD + HDS obligatoire |

> **📌 Note — Stratégie base de données VI → VC**
>
> **Contrainte technique VI** : L'environnement de développement local ne supporte pas Docker (problème de virtualisation matérielle). SQLite est donc maintenu comme base de développement local.
>
> **Implications et mitigations** :
> - Les mécanismes de sécurité critiques dépendants de PostgreSQL (RLS, triggers audit, pgvector) **ne sont pas testables en SQLite**. Ils sont développés et validés uniquement lors du déploiement sur l'instance PostgreSQL de production.
> - Les tests unitaires et d'intégration utilisent SQLite. Les tests de sécurité (RLS, audit trail) utilisent une instance PostgreSQL distante dédiée aux tests.
> - La migration SQLite → PostgreSQL est **transparente** : une seule variable d'environnement `DATABASE_URL` suffit, aucune modification de code requise.
>
> ```env
> # Développement local
> DATABASE_URL=sqlite:///./medflow.db
> # Production / Tests sécurité
> DATABASE_URL=postgresql://user:password@host:5432/medflow
> ```
>
> **pgvector** : disponible uniquement sur l'instance PostgreSQL. En développement SQLite, les fonctionnalités RAG sont simulées (mock) ou désactivées.

> **📌 Note — pgvector vs Pinecone**
>
> **Décision actée** : pgvector (extension PostgreSQL native) est le seul provider de base vectorielle retenu.
> - Zéro coût additionnel (même instance PostgreSQL)
> - Souveraineté totale des données (aucun envoi vers un service tiers US)
> - Conformité RGPD/HDS garantie
> - Pinecone : écarté définitivement (SaaS US, incompatible HDS)

### 3.2 Arborescence projet

```
medflow/
├── Docs/                              ← Documentation projet
├── backend/
│   ├── app/
│   │   ├── main.py                    ← FastAPI app, CORS, seeding, rate limiter
│   │   ├── api/routes.py              ← Tous les endpoints REST
│   │   ├── models/models.py           ← Modèles SQLAlchemy (20 entités)
│   │   ├── schemas/schemas.py         ← Schémas Pydantic
│   │   ├── core/
│   │   │   ├── config.py              ← Settings
│   │   │   └── security.py            ← JWT, bcrypt, MFA TOTP
│   │   ├── db/database.py             ← Engine SQLAlchemy
│   │   └── services/
│   │       ├── ai_service.py          ← Abstraction IA (agnostique provider)
│   │       ├── rules_engine.py        ← Moteur de règles physiologiques
│   │       ├── triage_engine.py       ← Moteur de scoring triage (P1–P5)
│   │       ├── cache_service.py       ← Abstraction Redis (cache + files)
│   │       └── sync_engine.py         ← Moteur sync offline Conflict-Aware
│   ├── alembic/                       ← Migrations
│   ├── tests/
│   │   ├── unit/                      ← Tests pytest (SQLite)
│   │   └── security/                  ← Tests RLS + audit (PostgreSQL requis)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                       ← Next.js App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx               ← Accueil → redirect /dashboard
│   │   │   ├── login/
│   │   │   ├── dashboard/
│   │   │   ├── patients/
│   │   │   ├── episodes/[id]/
│   │   │   ├── triage/
│   │   │   ├── ordonnances/
│   │   │   ├── agenda/
│   │   │   ├── settings/
│   │   │   └── admin/users/
│   │   ├── components/
│   │   │   ├── DashboardLayout.tsx    ← Sidebar RBAC + switcher langue
│   │   │   └── CommandPalette.tsx
│   │   ├── utils/
│   │   │   ├── api.ts                 ← Client HTTP centralisé (JWT Bearer)
│   │   │   └── sync.ts                ← Sync engine offline (IndexedDB ↔ API)
│   │   └── i18n.ts
│   ├── public/locales/
│   │   ├── fr/common.json
│   │   └── en/common.json
│   ├── tests/e2e/                     ← Tests Playwright
│   └── playwright.config.ts
└── .github/workflows/ci.yml           ← Pipeline CI/CD
```

### 3.3 Architecture applicative

- Architecture modulaire avec séparation claire des responsabilités
- Architecture multi-tenant avec isolation des données par `tenant_id` (préparée en VI, RLS PostgreSQL activée en VC)
- API RESTful + WebSocket pour les fonctionnalités temps réel (triage P1/P2 en VI, mises à jour épisodes en VC)

### 3.4 Pattern AI Provider & Résilience

L'architecture IA de MedFlow repose sur un **pattern Provider agnostique** avec routage intelligent et fallback automatique :

- **Provider principal** : sélectionnable par tenant (OpenAI, Anthropic [Claude Sonnet/Opus], Google Gemini, modèles open-source souverains Mistral/LLaMA auto-hébergés, modèles personnalisés locaux ou cloud).
- **Fallback automatique** : en cas d'indisponibilité, timeout ou rate-limiting du provider principal, l'orchestrateur bascule sur le provider secondaire sans interruption du workflow.
- **Retry policy** : max 3 tentatives avec backoff exponentiel ; après échec total, bascule en mode manuel avec alerte UI.
- **Journalisation** : chaque appel IA est tracé (provider, modèle, tokens, coût, latence, version du prompt) dans `ai_prompt_logs`.
- La couche `AIService` isole le code métier de l'implémentation LLM.

### 3.5 Rate Limiting & Sécurité API

| Endpoint type | Requêtes | Fenêtre | Action si dépassement |
|---|---|---|---|
| Auth (login) | 5 | 15 min | Blocage compte + notification admin |
| Auth (reset) | 3 | 1 h | Lien invalidé, email de sécurité |
| API générale | 100 | 1 min | HTTP 429 + retry-after header |
| Recherche patient | 30 | 1 min | **Cache Redis priorisé** |
| Export données | 5 | 1 h | **File d'attente Redis async** |
| Analyse IA | 20 | 1 h | **Mise en file Redis** + notification « traitement différé » |

### 3.6 Stratégie Offline & Sync — Conflict-Aware

```
┌───────────────────┐     ┌───────────────────┐
│   ONLINE MODE     │     │  OFFLINE MODE     │
│   Client ◄──────► │     │   Client ◄──────► │
│   API REST + WS   │     │   IndexedDB       │
└───────────────────┘     └───────────────────┘
                                   │
                          Retour réseau
                                   ▼
┌─────────────────────────────────────────────────────┐
│  SYNC MODE — Conflict-Aware Engine                  │
│                                                     │
│  IndexedDB ──► Conflict Detector ──► PostgreSQL     │
│                      │                              │
│              Champs médicaux ?                      │
│             ┌─────────┴──────────┐                  │
│           OUI                   NON                 │
│             │                    │                  │
│    Présenter les 2 versions  Last Write Wins        │
│    à l'utilisateur           (horodatage UTC ms)    │
│    pour arbitrage manuel                            │
└─────────────────────────────────────────────────────┘
```

**Règles de résolution des conflits :**

| Type de champ | Stratégie | Justification |
|---|---|---|
| **Champs médicaux critiques** (constantes vitales, diagnostics, ordonnances, allergies) | **Conflict-Aware** : présentation des 2 versions + arbitrage utilisateur obligatoire | Sécurité patient — une valeur ne peut pas être écrasée silencieusement |
| **Champs administratifs** (adresse, téléphone, notes) | Last Write Wins (horodatage UTC ms) | Risque faible, pas d'impact clinique |
| **Champs calculés** (IMC, score complétude) | Recalcul automatique post-sync | Toujours dérivés des données sources |

**Indicateurs visuels permanents** : 🟢 En ligne / 🔴 Hors ligne / 🔄 Sync en cours / ⚠️ Conflits en attente d'arbitrage.

**Files d'attente visibles** dans l'UI pour les utilisateurs terrain, avec compteur de modifications en attente de synchronisation.

### 3.7 Interopérabilité — Architecture Préparée

Les connecteurs d'interopérabilité sont **préparés architecturalement en VI** mais non implémentés fonctionnellement. L'implémentation réelle est prévue en **Version Commerciale (VC)**.

**Trois niveaux de préparation :**

#### Niveau 1 — Interfaces abstraites (Stubs & Adapters)

```python
# backend/app/services/interop/
├── base_connector.py        ← Interface abstraite commune
├── carte_vitale_stub.py     ← Stub Carte Vitale (CPS/CPE) — VC
├── mssante_stub.py          ← Stub MSSanté (CI-SIS) — VC
├── dmp_stub.py              ← Stub DMP (CDA R2) — VC
├── fhir_stub.py             ← Stub HL7 FHIR R4 — VC
└── dicom_stub.py            ← Stub PACS/DICOM — VC
```

Chaque stub implémente l'interface `BaseConnector` et retourne des données mockées en VI, prêt à être remplacé par l'implémentation réelle en VC sans modification du code métier.

#### Niveau 2 — Tables de données préparées

La table `external_integration_logs` est créée dès la Phase 1 :

| Champ | Type | Description |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | FK |
| `connector_type` | ENUM | `carte_vitale`, `mssante`, `dmp`, `fhir`, `dicom` |
| `direction` | ENUM | `inbound`, `outbound` |
| `status` | ENUM | `pending`, `success`, `failed`, `stub` |
| `payload` | JSONB | Données échangées |
| `error_message` | TEXT | NULLABLE |
| `created_at` | TIMESTAMPTZ | |

> Le statut `stub` indique un appel simulé en VI — traçabilité complète dès le départ.

#### Niveau 3 — Endpoints réservés documentés

Les endpoints suivants sont **déclarés mais non implémentés** en VI (retournent HTTP 501 Not Implemented avec message explicite) :

| Méthode | Route | Connecteur | Version cible |
|---|---|---|---|
| POST | `/api/interop/carte-vitale/read` | Lecture Carte Vitale | VC |
| POST | `/api/interop/mssante/send` | Envoi MSSanté | VC |
| POST | `/api/interop/dmp/push` | Alimentation DMP | VC |
| GET | `/api/interop/fhir/patient/{id}` | Export FHIR R4 | VC |
| POST | `/api/interop/dicom/upload` | Upload DICOM | VC |

> Ces endpoints apparaissent dans la documentation API (OpenAPI/Swagger) avec le tag `[VC - Non implémenté]`, permettant aux intégrateurs futurs de préparer leurs connexions dès VI.

**Standards préparés :** HL7 FHIR R4, CDA R2, CI-SIS MSSanté, PACS/DICOM, SESAM-Vitale (FSE en VC).

---

## 4. Gouvernance IA

### 4.1 Principe général

L'IA est transversale à toute l'application. Elle est présente dans chaque module et fonctionne de manière **autonome et automatique**, sans instruction manuelle.

### 4.2 Multimodalité

- **Texte**
- **Voix** (transcription + diarisation — Web Speech API fr-FR + fallback Whisper)
- **Photo** (caméra native — MediaDevices API)
- **Documents** (PDF, JPG, PNG, comptes rendus, ordonnances — OCR Tesseract.js + serveur)

### 4.3 Architecture multi-modèles

- Routage intelligent selon la nature de la tâche
- Fallback automatique en cas d'indisponibilité
- Modèles open-source hébergés localement pour les données sensibles (Mistral, LLaMA) — souveraineté

### 4.4 RAG — Base de connaissances

- Base personnalisable par spécialité et par médecin/tenant
- Guidelines des sociétés savantes (ESC, ERS…)
- Pratique personnelle du médecin
- Protocoles internes à la structure
- CRUD documents par tenant/médecin
- Stockage dans `knowledge_documents` (vectorisation pgvector)

### 4.5 Gestion des Prompts Système

- Stockés en base (`ai_system_prompts`) — JAMAIS codés en dur
- **Prompts globaux transverses** : non modifiables par le tenant ; modifiables par le super-administrateur
- **Prompts spécifiques tenant** : modifiables par l'administrateur du tenant
- **Versioning sémantique (semver)** : `prompt_key`, `version`, `template`, `specialty`, `tenant_id` (NULL=global), `is_editable`, `changelog` (JSON), `created_at`, `updated_at`, `created_by`
- À chaque release, prompts globaux versionnés automatiquement
- Forks tenant ou médecin = nouvelle version mineure
- Couple `(prompt_key, version)` journalisé dans `ai_prompt_logs`
- UI Paramètres IA : édition, incrémentation patch auto à chaque modification

### 4.6 Workflow IA & États d'analyse

Chaque analyse suit un cycle traçable via `ai_analysis_status` :

| État (back-end) | Libellé front-end | Description | Indicateur UI | Action utilisateur |
|---|---|---|---|---|
| `pending` | En attente d'analyse | En file d'attente | 🔄 Loader circulaire | Aucune — lecture seule |
| `processing` | Analyse en cours | OCR, structuration, inférence | 🔄 Loader avec étape | Aucune |
| `completed` | Analyse terminée | Succès | ✅ Badge vert | Accès résultats + validation |
| `manual_required` | Intervention humaine requise | Confiance faible ou incohérence Rules Engine | ⚠️ Badge jaune + alerte | Saisie/correction manuelle |
| `failed` | Échec de l'analyse | Timeout, API down, contexte trop long | ❌ Badge rouge | « Réessayer » ou saisie manuelle |

**Transitions autorisées** : `pending → processing → (completed | manual_required | failed)`. En cas d'échec, 2 retries automatiques. Retry manuel à tout moment.

### 4.7 Moteur de Règles Physiologiques (`rules_engine.py`)

| Type de règle | Exemple | Seuil / Condition | Effet back-end |
|---|---|---|---|
| Plage physiologique | IMC | < 10 ou > 60 | `manual_required` + alerte « Valeur invraisemblable » |
| Plage physiologique | Fréquence cardiaque | < 30 ou > 200 bpm | `manual_required` + alerte |
| Plage physiologique | SpO₂ | < 92 % alerte, < 85 % erreur | Alerte ou blocage |
| Plage physiologique | Température | < 35 °C ou > 41 °C | Alerte |
| Plage physiologique | Tension | PAS > 180 ou PAD > 110 | Alerte |
| Cross-check logique | Tension | PAS < PAD | Erreur + « Incohérence tensionnelle » |
| Cross-check logique | FEVG (écho) | > 90 % ou < 10 % | `manual_required` + alerte |
| Énumération | Sexe / Score | Hors liste | `manual_required` |
| Dépendance | Score de risque | Champs critiques manquants (âge, sexe, tabac, PAS, LDL) | Blocage + « Données insuffisantes » |
| IMC | Calcul auto (hauteur cm/m détecté) | — | Alimentation automatique |

Règles **configurables par spécialité et par tenant**. Une règle peut être « bloquante » ou « warning ».

### 4.8 Badges de Confiance IA par Champ

| Confiance | Indicateur | Effet UI |
|---|---|---|
| ≥ 90 % | 🟢 Confiance élevée | Aucun surlignage |
| 70–89 % | 🟡 Confiance moyenne | Surlignage jaune, tooltip « Vérification recommandée » |
| < 70 % | 🔴 Confiance faible | Surlignage rouge + champ « À vérifier » |

### 4.9 Widget de Feedback IA

Après validation/modification, le médecin évalue :

- Étoiles 1–5 + commentaire libre
- Flag « Contenu modifié » automatique si édition
- Stockage dans `ai_feedback` : rating, commentaire, prompt_version, provider, contenu_final

### 4.10 Pipeline IA en 8 étapes

```
1. Ingestion (multimodal) — Smart Input Button
2. Pré-traitement (OCR, normalisation, compression)
3. Extraction d'entités (NER, structuration JSON)
4. Validation Rules Engine (physiologie, cohérence)
5. Inférence LLM (synthèse, diagnostic, CAT) — Provider sélectionné, fallback auto
6. Scoring de confiance par champ
7. Génération brouillon (UI côte-à-côte)
8. Validation humaine + feedback + audit (ai_prompt_logs + ai_feedback)
```

### 4.11 Taxonomie des Erreurs IA & UI de Reprise

| Type d'erreur back-end | Cause | Message utilisateur | Action |
|---|---|---|---|
| `RATE_LIMIT` | Quota provider dépassé | « L'assistant est temporairement surchargé. Réessayez dans quelques minutes. » | Retry différé (60 s) |
| `CONTEXT_TOO_LONG` | Document trop volumineux | « Le document dépasse la capacité d'analyse. Veuillez le découper ou sélectionner une section. » | « Sélectionner une section » |
| `CONTENT_FILTER` | Contenu non traitable | « L'assistant n'a pas pu traiter ce contenu. Vérifiez les données d'entrée. » | Saisie manuelle |
| `MODEL_UNAVAILABLE` | Maintenance provider | « Service temporairement indisponible. Basculement automatique en cours. » | Retry + fallback silencieux |
| `INVALID_RESPONSE` | Format inattendu | « L'analyse a produit un résultat illisible. L'équipe technique est alertée. » | Saisie manuelle + log Sentry |
| `NETWORK_ERROR` | Coupure réseau serveur | « Erreur de connexion. Vos données sont sauvegardées localement. » | Retry auto dès réseau OK |

### 4.12 Principe de validation humaine

- Tout output IA est en mode « brouillon »
- Le médecin peut : valider, modifier puis valider, ou régénérer
- Traçabilité complète des modifications (audit trail)

---

## 5. Modules Fonctionnels

### 5.1 — Authentification & Connexion

- Connexion sécurisée avec authentification forte (MFA TOTP)
- `POST /api/auth/login` → JWT Bearer (24 h)
- `GET /api/auth/me` → profil utilisateur courant
- Logout : suppression du token + redirect `/login`
- **Protection de routes** : vérification JWT à chaque chargement ; redirection `/login` si échec
- Accès différencié par profil (médecin, paramédical, patient, admin)
- MFA : setup, verify, disable

**Sessions & Redirections Post-Login :**

| Rôle | Page d'atterrissage par défaut | Durée session | Politique MFA |
|---|---|---|---|
| Médecin (`doctor`) | `/dashboard` (file d'attente épisodes à valider) | 24 h (refresh 7 j) | Recommandée, configurable admin |
| IPA | `/missions` (missions terrain du jour) | 24 h | Recommandée |
| Infirmier (`nurse`) | `/missions` | 24 h | Recommandée |
| Assistant(e) médical(e) | `/patients` | 24 h | Optionnelle |
| Secrétaire | `/agenda` | 24 h | Optionnelle |
| Patient | `/mon-dossier` | 30 j (option « Se souvenir de moi ») | Non |
| Admin Master | `/admin/tenants` | 4 h | Obligatoire (TOTP) |

**Verrouillage de sécurité** : 5 tentatives échouées → blocage 15 min + email de sécurité. Mot de passe : min. 12 caractères, 1 majuscule, 1 chiffre, 1 symbole.

### 5.2 — Module Triage (Optionnel)

#### Objectifs

- Détecter les cas urgents et orienter vers les structures appropriées
- Sous-spécialiser les tenants selon la spécialité

#### Caractéristiques

- Module activable/désactivable par tenant et par médecin
- Configurable : ajout/suppression de symptômes, spécialités, critères

#### Forme d'implémentation

| Version | Forme | Justification |
|---|---|---|
| VI | Questionnaire dynamique et adaptatif | Rapide, fiable, validable médicalement |
| VC | Chatbot IA intégré | Plus fluide — nécessite entraînement |

#### Bouclier de Sécurité

La consultation (toute modalité/canal) est strictement réservée aux cas non urgents. Filtrage actif :

1. **À la saisie** : alertes bloquantes si seuils critiques (douleur thoracique aiguë, FC > 150 repos, PAS > 180, SpO₂ < 85 %) → bandeau rouge orientant vers le 15.
2. **À l'analyse IA** : Rules Engine force `manual_required` avec alerte prioritaire.
3. **À la validation** : bouton « Urgence détectée — Orienter vers les urgences » clôt sans CR et notifie patient + médecin traitant.

Message : « ⚠️ Les symptômes ou paramètres saisis suggèrent une situation potentiellement urgente. Veuillez orienter le patient vers les urgences ou appeler le 15. »

#### Moteur de scoring (`triage_engine.py`) — P1 à P5

| Priorité | Couleur | Description | Orientation typique | Temps d'attente max |
|---|---|---|---|---|
| **P1** | 🔴 Rouge | Urgence vitale (perte de conscience, dyspnée sévère, douleur thoracique typique) | Réanimation / SMUR | Immédiat |
| **P2** | 🟠 Orange | Urgence (SpO₂ < 90 %, FC > 150, PAS < 90, douleur intense) | Urgences | < 20 min |
| **P3** | 🟡 Jaune | Semi-urgent (fièvre élevée, douleur modérée) | Urgences / cabinet | < 1 h |
| **P4** | 🟢 Vert | Non urgent (consultation classique) | Cabinet / infirmerie | < 2 h |
| **P5** | 🔵 Bleu | Administratif | Cabinet | Flexible |

Drapeaux : signes d'alarme (JSON), mode d'arrivée, antécédents, **pédiatrique**, **grossesse**.

#### Workflow

`waiting → called → in_progress → completed / cancelled`

#### Frontend (`/triage`)

- File d'attente auto-rafraîchissement toutes les 30 s (P3–P5)
- **WebSocket `/ws/triage`** — alertes temps réel P1 et P2 (urgences vitales) — **activé en VI** ✅
- Compteurs par priorité, badges colorés
- VitalBadge avec seuils d'alarme visuels
- Actions : Appeler / Prendre en charge / Terminer / Annuler

### 5.3 — Module Agenda & Missions Terrain

Agenda moderne multi-praticiens. Gestion intelligente IA : attribution et optimisation des créneaux. Multi-support.

#### Types de rendez-vous

| Type | Modalité | Sous-types | Couplage automatique |
|---|---|---|---|
| Consultation | Synchrone présentielle (classique) | Initiale / Contrôle / Suivi | — |
| Consultation | Synchrone distancielle (téléconsultation) | Initiale / Contrôle / Suivi | — |
| Consultation | Asynchrone présentielle | Initiale / Contrôle / Suivi | — |
| Consultation | Asynchrone distancielle (Télé-expertise augmentée) | Initiale / Contrôle / Suivi | — |
| Examen | Holter ECG 24h | — | RDV retrait J+1 |
| Examen | Holter ECG 48h | — | RDV retrait J+2 |
| Examen | Holter ECG 72h | — | RDV retrait J+3 |
| Examen | Holter ECG 14j | — | RDV retrait J+14 |
| Examen | MAPA | — | RDV retrait J+1 |
| Examen | ETT | Configurable par tenant | — |
| Examen | PGV | Configurable par tenant | — |
| Mission Terrain | Déplacement interne | Individuelle (domicile) ou Groupe (EHPAD, clinique) | — |

#### Planning Unifié (RDV + Missions)

| Événement | Couleur | Icône | Source |
|---|---|---|---|
| RDV Cabinet | 🔵 Bleu `#0ea5e9` | 🏥 | `appointments` |
| Mission Terrain | 🟢 Vert `#22c55e` | 🚗 | `field_visits` |
| Télé-expertise augmentée | 🟣 Violet `#8b5cf6` | 📨 | `teleexpertise_requests` |

Fonctionnalités : drag & drop replanification, filtres (type/intervenant/statut), conversion RDV → Mission, export iCal (Google Calendar, Outlook), vues Jour/Semaine/Mois avec indicateurs de chevauchement.

#### Structure des Missions Terrain

Mission = entité indépendante traçable. L'équipe paramédicale **interne** se déplace toujours (aucune externalisation).

| Attribut | Type | Description |
|---|---|---|
| `collection_mode` | Enum | `internal_visit`, `remote_only` |
| `location_type` | Enum | `home`, `ehpad`, `clinic`, `hospital`, `other` |
| `patient_count` | Int | 1 par défaut, >1 si groupe |
| `is_group_visit` | Bool | `true` si EHPAD/clinique avec plusieurs patients |
| `scheduled_start_at` | DateTime | Début planifié |
| `scheduled_end_at` | DateTime | Fin planifiée |
| `due_at` | DateTime | Date butoir (sans créneau fixe) |
| `assigned_staff_id` | UUID | Obligatoire pour déplacement interne |
| `status` | Enum | `draft`, `scheduled`, `confirmed`, `in_progress`, `blocked`, `completed`, `cancelled` |
| `checklist` | JSON | Items dynamiques selon le type |
| `checklist_completion_rate` | Int | % calculé temps réel |

**Règle de synchronisation** : mission « En cours » → épisode `collecting` ; mission « Terminée » avec check-list critique OK → épisode `collected`.

**Check-list dynamique — Exemple mission « Collecte cardio complète » :**

| Tâche | Facturable CCAM | Lien entité |
|---|---|---|
| Collecte données administratives | Non | `patients` |
| Anamnèse + examen clinique | Non | `clinical_data` |
| ECG 12 dérivations | ✅ (DEQP003) | `examinations` |
| Upload CR échocardiographie | ✅ | `documents` + `examinations` |
| Biologie (upload + structuration) | Non | `examinations` |
| Pose Holter ECG | ✅ | `examinations` |
| Retrait Holter ECG (J+N selon durée) | ✅ | `examinations` |
| Pose MAPA | ✅ | `examinations` |
| Retrait MAPA (J+1) | ✅ | `examinations` |
| Signature consentement patient | Non | `consents` |

**Garde-fou logique** : statut « Terminée » interdit si items critiques non cochés. L'administrateur configure les items « critiques » vs « optionnels ».

### 5.4 — Dossier Patient Unifié & Longitudinal

Cœur de l'application — tout y est.

#### Structure

**Fiche administrative** : civilité, nom, prénom, DDN, sexe, téléphones, adresse, email, NIR (15 car. avec validation clé), médecin traitant + RPPS, statut remboursement (ALD, CMU-C, ACS, maternité, parcours coordonné), structure de référence, assurance complémentaire, champ « Adressé par ».

**Fiche médicale** : antécédents (cardio, médicaux, chirurgicaux, gynéco-obstétricaux, familiaux — JSON structuré), traitements habituels (liste structurée : nom, dosage, posologie, date début, prescripteur), allergies (allergène, réaction, sévérité, date, flag « médicamenteuse »), facteurs de risque CV, mode de vie (tabac, alcool, drogues, alimentation, activité physique, sommeil), contexte socio-pro.

**Onglet Examens** : tous les examens du patient, résultats intégrés automatiquement ou déposés par le patient.

**Historique chronologique** : consultations, examens, missions, documents, ordonnances, traçabilité (qui, quoi, quand).

---

#### Score de Complétude Administrative (0–100 %, pondéré)

> Mesure la **qualité du dossier administratif** du patient. Utilisé pour l'identification légale, la facturation et la conformité RGPD.
> **N'a aucun impact sur le déclenchement de l'analyse IA.**

Calculé en temps réel via `calculate_patient_completeness_score()`.

**Formule :**
```
Score = Σ (poids du champ si rempli) / Σ (poids total des champs applicables) × 100
```

**Pondérations exactes :**

| Champ | Poids |
|---|---|
| Civilité | 5 % |
| Nom | 15 % |
| Prénom | 15 % |
| Date de naissance | 15 % |
| Sexe | 15 % |
| Téléphone | 10 % |
| Adresse | 10 % |
| Email | 5 % |
| NIR | 10 % |
| **Total** | **100 %** |

**Affichage** : barre de progression dans l'en-tête du dossier + liste déroulante des champs manquants priorisés.

> **Note** : La date de naissance alimente le calcul automatique de l'**âge** (transmis à l'IA à la place de la DDN). Le nom et le prénom ne sont jamais transmis au moteur IA — seuls le **sexe** et l'**âge calculé** lui sont fournis.

---

#### Score de Complétude Clinique (0–100 %, pondéré)

> Mesure la **qualité des données médicales** disponibles pour l'analyse IA.
> C'est **ce score — et uniquement ce score** — qui conditionne le déclenchement de l'analyse IA.

Calculé en temps réel via `calculate_clinical_completeness_score()`.

**Pondérations exactes :**

| Champ clinique | Poids | Criticité IA |
|---|---|---|
| Motif de consultation | 25 % | ✅ Critique |
| Histoire de la maladie | 25 % | ✅ Critique |
| Examen clinique | 20 % | ✅ Critique |
| Antécédents | 15 % | ⚠️ Important |
| Traitements habituels | 10 % | ⚠️ Important |
| Mode de vie (tabac, alcool, activité physique…) | 5 % | 🔵 Utile |
| **Total** | **100 %** | |

**Seuils & impact sur l'analyse IA :**

| Seuil | Badge UI | Déclenchement IA | Action |
|---|---|---|---|
| ≥ 70 % | 🟢 « Données cliniques suffisantes » | ✅ Automatique | Analyse lancée |
| 50–69 % | 🟡 « Données cliniques partielles » | ⚠️ Avec avertissement | Override médecin possible |
| < 50 % | 🔴 « Données cliniques insuffisantes » | ❌ Bloqué | Override médecin + justification obligatoire tracée |

> **Règle de sécurité** : le passage `collected → processing` est conditionné par le **score clinique ≥ 70 %**, pas par le score administratif.

**Affichage** : barre de progression distincte dans l'onglet Préconsultation + liste des champs cliniques manquants priorisés.

---

#### Ce que l'IA reçoit — Données anonymisées

> L'IA ne reçoit **jamais** les données nominatives du patient. Seules les données médicales pertinentes lui sont transmises, sous forme anonymisée.

| Donnée | Transmise à l'IA | Forme transmise |
|---|---|---|
| Nom / Prénom | ❌ Non | — |
| Date de naissance | ❌ Non | → **Âge calculé automatiquement** ✅ |
| NIR | ❌ Non | — |
| Adresse / Email / Téléphone | ❌ Non | — |
| Sexe | ✅ Oui | `M / F / X` |
| Âge | ✅ Oui | Calculé depuis DDN, en années |
| Motif de consultation | ✅ Oui | Texte libre |
| Histoire de la maladie | ✅ Oui | Texte structuré |
| Constantes vitales | ✅ Oui | Valeurs numériques + unités |
| Antécédents médicaux | ✅ Oui | JSON structuré |
| Traitements habituels | ✅ Oui | Liste structurée |
| Allergies | ✅ Oui | Liste structurée |
| Mode de vie | ✅ Oui | Enums + valeurs |
| Documents uploadés (OCR) | ✅ Oui | Texte extrait anonymisé |

---

#### Architecture Données d'Entrée / Sortie

**Entrée — Sections fixes** :

| Section | Champs clés | Obligatoire |
|---|---|---|
| Administratif | Civilité, nom, prénom, DDN, sexe, téléphone, adresse, email, NIR, médecin traitant + RPPS | ✅ |
| Anamnèse | Motif de consultation, histoire de la maladie, contexte | Motif + histoire ✅ |
| Terrain | Antécédents (JSON par catégorie), facteurs de risque CV, traitements habituels | ❌ (fortement pondérés score clinique) |
| Mode de vie | Tabac, alcool, drogues, alimentation, activité physique, sommeil | ❌ |
| Contexte socio-pro | Profession, situation familiale, stress (1–10), conditions de vie | ❌ |
| Allergies | Liste structurée (allergène, réaction, sévérité, date) + flag « médicamenteuse » | ❌ |
| Examen clinique | Poids, taille, IMC auto, TA, FC, SpO₂, T° ; examen ciblé par spécialité | Partiellement ✅ |

**Sortie — Sections dynamiques générées par l'IA, validées médecin** :

| Section | Condition | Validation |
|---|---|---|
| Évaluation risque | Si données critiques présentes | Obligatoire |
| Synthèse clinique | Si analyse IA réalisée | Obligatoire |
| Diagnostic principal | Si synthèse réalisée | Obligatoire |
| Diagnostics différentiels | Si pertinents | Optionnelle |
| Conduite à tenir (CAT) | Si synthèse réalisée | Obligatoire |
| Bilan complémentaire | Si analyse IA réalisée | Optionnelle |
| Suivi recommandé | Si synthèse réalisée | Obligatoire |
| Ordonnances | Si ordonnances générées | Validation obligatoire avant envoi |

Toutes en mode brouillon avant validation. **Bidirectionnalité IA ↔ Dossier** avec audit trail.

---

#### Règles GED

| Règle | Spécification |
|---|---|
| Formats acceptés | PDF, JPG, PNG, TIFF (opt.), DICOM (si module imagerie) |
| Taille max | 10 Mo par fichier (configurable par tenant) |
| Compression | Optimisation auto client avant upload |
| Liaison obligatoire | `patient_id` + (`episode_id` OU `examination_id` OU `field_visit_id`) |
| OCR | Tesseract.js client + API serveur, indexé full-text |
| Viewer | react-pdf, images, viewer DICOM basique (VI) |

### 5.5 — Épisode de Soin (3 onglets, 10 statuts)

Préconsultation + Consultation + Post-consultation = **une seule entité** « Épisode de Soin » avec 3 onglets distincts dans une même interface.

#### Workflow 10 statuts (vue complète — rôles médicaux)

| État back-end | Libellé front | Couleur | Description | Déclencheur transition |
|---|---|---|---|---|
| `pending` | En attente | ⚪ Gris | Demande créée, consentement en attente | Création par secrétaire |
| `consent_sent` | Consentement envoyé | ⚪ Gris | Consentement envoyé au patient | Action secrétaire |
| `consented` | Consentement signé | ⚪ Gris | Reçu | Signature patient |
| `collecting` | Collecte en cours | 🔵 Bleu | Mission active | Mission « En cours » |
| `collected` | Collecte terminée | 🔵 Bleu | En attente d'analyse IA | Mission « Terminée » + check-list OK |
| `processing` | Analyse en cours | 🟠 Orange | OCR, structuration, synthèse | Auto si complétude ≥ 70 % |
| `ready_review` | En attente de validation | 🟠 Orange | Validation médecin requise | Fin analyse IA |
| `reviewing` | Validation en cours | 🟠 Orange | Médecin en validation côte-à-côte | Ouverture dossier |
| `completed` | Validé et signé | 🟢 Vert | Signature électronique | Signature médecin |
| `cancelled` | Annulé | ⚫ Noir | Annulé à tout moment | Médecin / secrétaire |

**Règle de sécurité** : `collected → processing` bloqué si score < 70 %, sauf override médecin avec justification tracée.

---

#### Vue simplifiée 3 états (rôles non-médicaux)

> Destinée aux rôles : **secrétaire**, **assistant médical**, **infirmier**.
> Masque la complexité interne du workflow — affichée dans la liste des épisodes et les notifications.

| État simplifié | Couleur | Statuts internes couverts | Description affichée |
|---|---|---|---|
| 🔵 **En cours** | Bleu | `pending` → `consent_sent` → `consented` → `collecting` → `collected` → `processing` | « Dossier en cours de constitution » |
| 🟠 **En attente du médecin** | Orange | `ready_review` → `reviewing` | « En attente de validation médicale » |
| 🟢 **Terminé** | Vert | `completed` | « Épisode validé et signé » |
| ⚫ **Annulé** | Noir | `cancelled` | « Épisode annulé » |

**Règles d'affichage :**
- La vue simplifiée est affichée **par défaut** pour les rôles `nurse`, `medical_assistant`, `secretary`
- Le médecin (`doctor`) et l'IPA (`ipa`) voient la vue complète 10 statuts par défaut
- Un bouton « Voir le détail du statut » permet à tout rôle d'accéder à la vue complète si besoin
- Les **notifications** utilisent toujours le libellé simplifié pour les rôles non-médicaux

---

#### Onglet 1 — Préconsultation

Réalisée **souvent** par l'équipe paramédicale **interne** au tenant (parfois réalisée par le médecin).

- Acteurs : assistant(e) médical(e), infirmier(ère), IPA, secrétaire
- **Smart Input Button** universel : dictée vocale, OCR document, caméra mobile, saisie manuelle
- Constantes vitales (poids, taille, IMC auto, PAS, PAD, FC, SpO₂, température)
- Examen clinique ciblé selon spécialité
- **Bouclier de sécurité** : alertes valeurs atypiques
- Champs dynamiques créés automatiquement par l'IA selon type d'examen
- Génération brouillon IA : synthèse clinique, diagnostic, plan, ordonnance

---

#### Onglet 2 — Consultation (Vue diff IA)

**Interface côte-à-côte** :

```
┌─────────────────────────────┐  ┌─────────────────────────────────────┐
│   SOURCES & DONNÉES BRUTES  │  │   PROPOSITIONS IA & VALIDATION      │
├─────────────────────────────┤  ├─────────────────────────────────────┤
│ • Document original (viewer)│  │ • Champ pré-rempli par l'IA         │
│ • Données structurées       │  │ • Badge de confiance par champ      │
│ • Résultats OCR extraits    │  │ • ✅ Accepter / ✏️ Modifier / ❌   │
└─────────────────────────────┘  └─────────────────────────────────────┘
```

- Synchronisation bidirectionnelle texte ↔ données
- Surlignage intelligent (confiance < 70 % rouge, 70–89 % jaune)
- Justification rejet obligatoire (alimente `ai_feedback`)
- Historique modifications horodaté
- Sidebar : protocoles cliniques par spécialité (ESC, ERS…)
- Bouton « Signer & Clôturer l'Épisode »

**Modalités** :
- *Consultation classique* (synchrone présentielle)
- *Téléconsultation* (synchrone distancielle)
- *Consultation asynchrone* (asynchrone présentielle)
- *Télé-expertise augmentée* (asynchrone distancielle)
- *Mission Terrain* (EHPAD, domicile)

**Assistant IA temps réel** : mode « copilote discret » (panneau latéral rétractable / bouton flottant), recommandations sociétés savantes, interactions médicamenteuses, bilan recommandé, RAG + guidelines.

**Rôle IPA** : suivi maladies chroniques par délégation.

---

#### Onglet 3 — Post-consultation

- Suivi bilans complémentaires + résultats
- Réception automatique (laboratoire, imagerie) ou manuelle (dépôt patient)
- Analyse IA automatique des résultats + nouveau CR brouillon
- Récapitulatif ordonnances validées + impression
- **Chatbot post-consultation** :

| Autorisé | Interdit |
|---|---|
| Explication des prescriptions | Nouveau diagnostic |
| Rappel des consignes médicales | Modification de traitement |
| Orientation si nouveau symptôme | |

Disclaimer permanent : « Ce chatbot ne remplace pas l'avis médical. En cas d'urgence, appelez le 15. »

- Export PDF de l'épisode complet

---

#### Consentement Patient (Modalités Asynchrones)

Deux consentements requis et horodatés (table `consents`) :
1. **Principe de consultation asynchrone** (patient ne verra pas le médecin sur place)
2. **Traitement IA des données**

Révocables, tracés dans audit trail.

---

#### Préférences Notifications & Heures Silencieuses

| Canal | Soignant | Patient |
|---|---|---|
| In-app | ✅ défaut | ✅ défaut |
| Email | ✅ défaut | ✅ défaut |
| SMS | Opt. admin tenant | Opt. (rappels RDV) |
| Push mobile | PWA | PWA |

Heures silencieuses : 20h–8h + week-ends (configurable). Alertes vitales traversent toujours.

---

#### Skeleton Loading

Pendant les traitements IA, squelettes shimmer (3–5 lignes) à la place du futur contenu, mise à jour progressive avec fondu 200 ms. Annonce `aria-live="polite"` pour lecteurs d'écran (WCAG 2.1 AA).

### 5.6 — Ordonnances Numériques

Workflow : `brouillon → signé → envoyé → annulé`

**Lignes d'ordonnance (JSON)** : `{ dci, forme, dosage, posologie, duree, quantite, renouvelable, instructions }`

**Signature** : hash SHA-256 du contenu + prescripteur + date. Validité par défaut : 3 mois.

**Permissions** :
- Création / modification : `doctor` ET `ipa`
- **Signature** : `doctor` UNIQUEMENT
- Suppression : brouillons uniquement, par `doctor` ou `ipa`

**Frontend** (`/ordonnances`) :
- Liste filtrable par statut
- Panneau latéral sticky pour détail
- Création multi-lignes avec suggestions DCI

### 5.7 — Module Facturation Intelligente

Facturation automatique par l'IA sur la base des actes.

| Statut Patient | Taux remboursement |
|---|---|
| Parcours de soins coordonné | 70 % |
| Hors parcours | 30 % |
| ALD / Maternité | 100 % (hors dépassement) |
| CMU-C / ACS | 100 % (dépassement interdit) |

> Taux paramétrables, non codés en dur.

- Codage automatique CCAM
- Gestion règles de cumul d'actes
- Calcul reste à charge
- Tiers payant SS + part complémentaire mutuelle
- Adaptable nomenclatures internationales

**Règles détaillées** :

| Règle | Description | Priorité |
|---|---|---|
| Association acte/mission | Chaque tâche facturable → code CCAM auto | 🟢 Basse |
| Cumul d'actes | Vérification incompatibilités CCAM + choix optimal | 🟡 Moyenne |
| Tiers payant SS | Détection auto statut patient | 🟢 Basse |
| Reste à charge | = Total – SS – mutuelle | 🟢 Basse |
| Dépassement d'honoraires | Selon conventions + statut (interdit CMU-C) | 🟡 Moyenne |
| Export comptable | FEC + standards | 🔴 Haute |

> **Note** : partenariat avec éditeur facturation envisagé pour cas particuliers (CCAM + NGAP).

### 5.8 — Messagerie Sécurisée

**VI — Messagerie interne :**
- Messagerie interne entre membres de l'équipe du cabinet
  (médecins ↔ paramédicaux)
- Boîte de réception, rédaction, lecture, suppression
- Bandeau UI permanent :
  « Messagerie externe (MSSanté) disponible en Version Commerciale »

**VC — Messagerie externe :**
- Externe : structure ↔ patient
- Externe : structure ↔ médecin traitant du patient
- Chiffrement bout en bout + archivage légal
- Conformité MSSanté (CI-SIS)

### 5.9 — Téléconsultation & Télé-expertise Augmentée

#### Téléconsultation (Synchrone Distancielle) — Architecture préparée VI / Fonctionnel VC

> En VI, le type de RDV "téléconsultation" est créé et planifiable dans l'agenda.
> La session vidéo elle-même est déléguée à un lien externe (Doctolib, Whereby, Zoom Santé…)
> fourni manuellement par le secrétaire. L'implémentation vidéo native (WebRTC) est prévue en VC.

**VI — Fonctionnel :**

- Création et planification du RDV de type "synchrone distancielle" dans l'agenda
- Champ `video_link` sur le RDV : URL de session externe saisie manuellement
- Notification patient avec lien de connexion (email + push PWA)
- Épisode de soin créé et lié au RDV (workflow 10 statuts identique)
- Bandeau UI permanent sur le RDV :
  « Session vidéo via lien externe — intégration native disponible en Version Commerciale »

**VC — À implémenter :**

- Session vidéo native intégrée (WebRTC ou SDK Whereby/Jitsi auto-hébergé)
- Salle d'attente virtuelle patient (accès depuis le portail patient)
- Enregistrement optionnel de la session (consentement obligatoire)
- Partage d'écran (documents, résultats)
- Conformité HDS pour les flux vidéo

---

#### Télé-expertise Augmentée (Asynchrone Distancielle)

> Modalité clé de MedFlow : le patient ne voit pas le médecin en temps réel.
> L'équipe paramédicale collecte les données sur le terrain, l'IA prépare le dossier,
> le médecin valide à distance dans son propre temps.
> **Cette modalité est entièrement fonctionnelle en VI** — elle ne nécessite pas de vidéo.

**Workflow VI :**

```
Patient (via son médecin) → Demande → Consentement (×2) → Mission terrain
→ Collecte données → Analyse IA → Validation médecin → CR signé
```

**Statuts `TeleexpertiseRequest` :**

| Statut | Description |
|--------|-------------|
| `draft` | Demande créée, en attente de planification |
| `scheduled` | Mission terrain planifiée |
| `collecting` | Collecte en cours (mission active) |
| `collected` | Données collectées, en attente d'analyse IA |
| `processing` | Analyse IA en cours |
| `ready_review` | En attente de validation médecin |
| `completed` | CR signé et transmis |
| `cancelled` | Annulée |

**SLA de traitement (dès réception dossier complet ≥ 70 %) :**

| Niveau | Délai | Cas concernés |
|--------|-------|---------------|
| Standard | 10 jours ouvrés | Bilans de routine, contrôles chroniques |
| Prioritaire | 48 heures | Dyspnée, palpitations, anomalies ECG non urgentes |
| Urgence détectée | Immédiat — blocage | Seuils critiques détectés par le Bouclier de sécurité |

**VI — Fonctionnel :**

- Création de la demande (secrétaire ou médecin)
- Double consentement patient (principe asynchrone + traitement IA)
- Planification mission terrain liée
- Collecte données + analyse IA + validation côte-à-côte (workflow épisode standard)
- CR signé + export PDF + archivage GED
- Suivi statut visible patient (portail patient — vue simplifiée)

**VC — À implémenter :**

- Accès expert externe (rôle dédié, authentification isolée)
- Réponse structurée de l'expert dans le dossier
- Réseau d'experts partenaires avec scores de pertinence et disponibilités
- Messagerie sécurisée médecin ↔ expert (MSSanté)

### 5.10 — Portail Patient

| Fonctionnalité | Description | Priorité VI |
|---|---|---|
| Création de compte | Email + validation identité + MFA optionnel | P1 |
| Connexion sécurisée | Session 30 j (« Se souvenir de moi ») | P0 |
| Dépôt documents | Upload PDF/JPG/PNG, description, rattachement épisode | P1 |
| Consultation CR | Lecture seule CR finalisés signés, téléchargement PDF | P1 |
| Consultation recommandations | Plan PEC, suivi, ordonnances validées | P1 |
| Signature consentement | Formulaire RGPD + télé-expertise, signature électronique horodatée | P0 |
| Suivi d'avancement | Vue simplifiée statut épisode | P2 |
| Prise de RDV | Créneaux par type/praticien, confirmation immédiate | P1 |
| Messagerie sécurisée | Chat avec cabinet + pièces jointes | P1 |
| Notifications | Push PWA + email (RDV, CR, rappel suivi) | P1 |
| Chatbot post-consultation | Avec disclaimers permanents | P2 |

Mobile-first (PWA) + accès navigateur web.

### 5.11 — Analytics & Tableau de Bord

- Statistiques activité (consultations, examens, RDV)
- Indicateurs qualité de soins
- Suivi pathologies chroniques à l'échelle patientèle
- Tableaux de bord personnalisables par rôle
- Palette de commandes (`CommandPalette`) accessible via `Ctrl+K`
- Panel « Patients récents » avec score de complétude
- Panel « Missions terrain actives » avec taux de complétion

**KPIs Opérationnels, Qualité & IA :**

| Catégorie | KPI | Objectif VI | Source données | Méthode de mesure | Fréquence |
|---|---|---|---|---|---|
| **Efficacité** | Temps moyen création dossier | < 3 min | `patients.created_at` → premier champ rempli | Moyenne arithmétique des délais `created_at → updated_at` (première sauvegarde) | Hebdomadaire |
| **Efficacité** | Validation épisode asynchrone | < 30 min | `field_visits.completed_at` → `episodes.signed_at` | Médiane des délais entre `collected` et `completed` | Hebdomadaire |
| **Efficacité** | Taux RDV honorés | > 95 % | `appointments.status` | Ratio `status = completed` / total RDV planifiés | Mensuel |
| **Qualité** | Score complétude médian à l'analyse | > 85 % | `episodes.completeness_score` au moment du passage en `processing` | Médiane des scores à l'entrée en analyse IA | Mensuel |
| **Qualité** | Taux « Intervention humaine requise » | < 10 % | `episodes.ai_status = manual_required` | Ratio `manual_required` / total analyses IA | Hebdomadaire |
| **Qualité** | Taux corrections médecin par section | < 15 % | Audit trail — champs modifiés post-proposition IA | Ratio champs modifiés / total champs proposés par l'IA | Mensuel |
| **Qualité** | Taux erreurs facturation | < 1 % | `billings` — factures corrigées après validation | Ratio factures corrigées / total factures émises | Mensuel |
| **Satisfaction** | NPS Praticiens | > 50 | Enquête in-app | Calcul NPS standard (% promoteurs − % détracteurs) | Trimestriel |
| **Satisfaction** | NPS Patients | > 40 | Enquête in-app portail patient | Calcul NPS standard | Trimestriel |
| **Sécurité** | Incidents de sécurité | 0 | `audit_logs` + journal sécurité | Comptage incidents classifiés | Continu (alerte immédiate) |
| **Sécurité** | Temps réponse incident | < 1 h | Horodatage détection → résolution | Delta timestamps détection/résolution | Par incident |
| **Performance** | Uptime | > 99,5 % | Monitoring infrastructure | Calcul disponibilité mensuelle (downtime / total) | Mensuel |
| **Performance** | Temps réponse API P95 | < 500 ms | Logs FastAPI + Redis | Percentile 95 des temps de réponse | Hebdomadaire |
| **IA** | Taux échec IA | < 5 % | `ai_prompt_logs` — `status = failed` | Ratio `failed` / total appels IA | Hebdomadaire |
| **IA** | Coût moyen IA / épisode | < 2 € | `ai_prompt_logs.cost_usd` | Somme coûts / nombre épisodes analysés | Mensuel |
| **IA** | Distribution confiance champs | > 80 % champs ≥ 90 % | `ai_outputs.confidence_score` | Histogramme distribution scores de confiance | Mensuel |
| **Offline** | Taux conflits sync résolus manuellement | < 5 % | `sync_engine` — conflits arbitrés | Ratio conflits arbitrage manuel / total syncs | Hebdomadaire |
| **Offline** | Délai moyen sync après reconnexion | < 30 s | `sync.ts` — timestamps sync | Médiane délais reconnexion → sync complète | Hebdomadaire |

### 5.12 — Notifications & Rappels Intelligents

| Événement | Destinataire | Canaux | Déclencheur |
|---|---|---|---|
| Nouvel épisode à valider | Médecin assigné | In-app + Email | `ready_review` |
| Mission assignée | IPA / Infirmier | In-app + Push | Création mission |
| Mission bloquée | Secrétaire + Médecin | In-app + Email | `blocked` |
| Consentement signé | Secrétaire | In-app | `consented` |
| Résultat critique | Médecin | In-app + Email + SMS (bypass heures silencieuses) | Réception résultat |
| Rappel RDV J-2 | Patient | SMS | Cron quotidien 10h |
| Rappel RDV J-1 | Patient | Email | Cron quotidien 18h |
| Rappel suivi chronique | Patient | Email | Délai dépassé |
| Échec IA | Médecin + Admin | In-app + Email | `failed` après 2 retries |

---

## 6. Fonctionnalités Transversales

### 6.1 Smart Input Button

Bouton universel multimodal présent **partout où une saisie est possible**. Modale plein écran 4 onglets :

| Onglet | Fonctionnalité | Technologie | Cible |
|---|---|---|---|
| 🎤 Dictée vocale | Transcription temps réel + diarisation | Web Speech API + Whisper fallback | Champ actif |
| 📄 Import document | Drag & drop PDF/JPG/PNG, prévisualisation, rattachement auto | File API + OCR Tesseract.js | GED |
| 📷 Photo directe | Capture caméra native + compression auto | MediaDevices API | GED |
| ✏️ Saisie manuelle | Formulaire React Hook Form + Zod | RHF | Champ cible |

- **Reconnaissance patient automatique** : extraction nom/prénom/DDN → proposition création/rattachement (similarité ≥ 85 %)
- **Détection nom tiers** : alerte si document contient un nom différent du dossier ouvert

### 6.2 Command Palette (`Ctrl/Cmd + K`)

| Raccourci | Action | Contexte |
|---|---|---|
| `Ctrl/Cmd + K` | Command Palette globale | Global |
| `Ctrl/Cmd + N` | Nouveau patient | Global |
| `Ctrl/Cmd + Shift + A` | Nouveau RDV | Agenda |
| `Ctrl/Cmd + Shift + E` | Nouvel examen | Dossier patient |
| `Ctrl/Cmd + Shift + D` | Basculer dictée vocale | Champs texte |
| `Ctrl/Cmd + S` | Sauvegarder | Formulaires |
| `Ctrl/Cmd + P` | Imprimer / Générer PDF | Dossier complet |
| `Ctrl/Cmd + Shift + R` | Lancer analyse IA | Épisode |
| `Escape` | Fermer modale / panneau | Global |
| `?` | Aide contextuelle | Global |

Accessibilité WCAG 2.1 AA (focus visible, skip links, ordre tab logique).

### 6.3 Audit Trail

Voir §7 — table `audit_logs`, triggers PostgreSQL `INSERT ONLY`, RLS restrictive.

### 6.4 Export PDF

- `GET /api/episodes/{id}/export-pdf` → PDF ReportLab
- Structure : en-tête MedFlow, identité patient, épisode, constantes, anamnèse, synthèse IA, ordonnances signées, pied de page confidentiel
- `StreamingResponse` (`application/pdf`)
- Nom fichier : `medflow_episode_{id[:8]}_{patient_name}.pdf`

### 6.5 Réseau d'Experts & Partenariats

Fonctionnalité transversale intégrée Dossier + Messagerie (pas de module dédié VI).

- Annuaire d'experts partenaires
- Bouton « Adresser ce patient »
- Génération automatique IA d'un courrier d'adressage
- Envoi via messagerie sécurisée
- VC : scores pertinence, disponibilités, délais

---

## 7. Sécurité & Conformité

### 7.1 Sécurité VI

| Aspect | Implémentation |
|---|---|
| Authentification | Email + MDP (12 car. min, 1 maj, 1 chiffre, 1 symbole) + MFA TOTP (obligatoire admin, recommandé médecins) |
| Session | JWT 24 h, refresh 7 j, expiration 30 min inactivité |
| Verrouillage | 5 tentatives échouées → blocage 15 min + email |
| Chiffrement transit | TLS 1.3 obligatoire |
| Chiffrement repos | AES-256 (clé via `ENCRYPTION_KEY`) ; client-side optionnel pour documents ultra-sensibles |
| Isolation tenant | RLS PostgreSQL stricte, filtre `tenant_id` auto |
| Backups | Quotidiens chiffrés, rétention 30 j min, région différente |
| Audit | `audit_logs` immuable (INSERT ONLY + RLS) |

### 7.2 Sécurité backlog VC

- HSM (Hardware Security Module) pour clés signature
- Signature électronique qualifiée eIDAS
- Pen-test annuel + bug bounty
- Détection d'anomalies comportementales

### 7.3 Structure Audit Trail — `audit_logs`

| Champ | Type | Description | Exemple |
|---|---|---|---|
| `id` | UUID | Identifiant unique | `a1b2c3…` |
| `timestamp` | TIMESTAMPTZ | Horodatage UTC | `2026-06-15T14:32:01.123Z` |
| `user_id` | UUID | Référence utilisateur | `u123…` |
| `tenant_id` | UUID | Isolation multi-tenant | `t456…` |
| `action_type` | ENUM | `CREATE`, `READ`, `UPDATE`, `DELETE`, `VALIDATE`, `SIGN`, `EXPORT` | `SIGN` |
| `entity_type` | TEXT | Table/entité concernée | `episodes`, `prescriptions`, `ai_outputs` |
| `entity_id` | UUID | ID enregistrement | `p789…` |
| `old_value` | JSONB | Valeur avant | `{"diagnosis":"HTA"}` |
| `new_value` | JSONB | Valeur après | `{"diagnosis":"HTA + dyslipidémie"}` |
| `ip_address` | INET | IP source | `192.168.1.10` |
| `user_agent` | TEXT | Client navigateur | `Mozilla/5.0…` |
| `session_id` | UUID | Session | `s012…` |

Triggers automatiques sur `patients`, `episodes`, `examinations`, `documents`, `invoices`, `ai_outputs`. Admin ne peut ni modifier ni supprimer.

### 7.4 Conformité réglementaire

- **Certification HDS** (Hébergeur Données de Santé) — obligatoire
- **RGPD** : consentement horodaté, droit d'accès (export JSON/PDF), droit à l'oubli (anonymisation sur demande), portabilité
- Hébergement Cloud souverain européen
- Disclaimer systématique sur tous les outputs IA
- Recommandation : juriste spécialisé droit santé numérique dès conception (cadre IA Act UE)

---

## 8. Internationalisation (i18n FR/EN)

### 8.1 État VI

- Langues : **Français (fr)** [défaut] + **Anglais (en)**
- Configuration : `i18next-http-backend` + `i18next-browser-languagedetector` (clé `localStorage` `medflow_lang`)
- Switcher 🇫🇷 / 🇬🇧 dans la sidebar de `DashboardLayout`
- Namespace : `common` (couvrant tous les modules)

### 8.2 Architecture cible & Expansion

| Phase | Langues UI | Nomenclature | Réglementation |
|---|---|---|---|
| VI   | Français (référence)              | CCAM France        | RGPD + HDS France    |
| VC   | Anglais, Espagnol, Italien        | SNOMED CT, ICD-10 local | RGPD UE + locales |
| VInt | Allemand, Portugais, Néerlandais  | Adaptation pays    | FDA / HIPAA / PIPEDA |

**Structure technique** :
- Namespaces séparés : `common`, `auth`, `patients`, `examinations`, `appointments`, `billing`, `ai`, `notifications`, `medical`
- Terminologie médicale `medical` overridable par spécialité et tenant
- Fallback : `fr` → `en` → clé brute
- Override par API admin pour termes spécifiques cabinet

---

## 9. Décisions Actées & Points en Suspens

### 9.1 Décisions actées

| Sujet | Décision |
|---|---|
| **Versionnage** | Terminologie actée : **Version Initiale (VI)** / **Version Commerciale (VC)** / **Version Internationale (VInt)** |
| **Cible VI** | Cabinet médical du fondateur (cardiologue) + équipe interne (secrétaire, infirmière/IPA, assistant médical, patients) |
| **Trajectoire VI → VC** | Migration sans refonte : hébergement HDS + activation multi-tenant + connecteurs interop. Décision de passage prise si usage VI validé |
| **Multi-tenant VI** | `tenant_id` propagé sur **toutes les tables dès la Phase 1** — architecture préparée, isolation complète activée en VC (RLS PostgreSQL) |
| **Base de données dev** | SQLite maintenu en VI (contrainte technique : Docker non disponible, pb virtualisation). Migration PostgreSQL transparente via `DATABASE_URL`. Tests de sécurité (RLS, audit) sur instance PostgreSQL distante dédiée |
| **Base vectorielle** | **pgvector acté** (extension PostgreSQL native) — Pinecone écarté définitivement (SaaS US, incompatible HDS/RGPD). pgvector activé sur instance PostgreSQL (prod/tests sécurité) |
| **Cache & Files de tâches** | **Redis ajouté à la stack VI** — cache recherche patient, sessions, file tâches async (Celery/ARQ), rate limiting |
| **Sync offline** | Stratégie **Conflict-Aware** (remplace Last Write Wins) : arbitrage utilisateur obligatoire pour champs médicaux critiques / Last Write Wins conservé pour champs administratifs uniquement |
| **WebSocket triage** | **Avancé en VI** pour priorités P1 et P2 (urgences vitales) — polling 30 s conservé pour P3–P5 |
| **Interopérabilité** | **Option C actée** : stubs + tables + endpoints réservés dès VI. Implémentation fonctionnelle en VC. Statut `stub` tracé dans `external_integration_logs` |
| **Messagerie sécurisée** | Messagerie **interne** fonctionnelle en VI (médecins ↔ paramédicaux). Messagerie **externe** (MSSanté, CI-SIS) : architecture préparée en VI — implémentation fonctionnelle en VC |
| **Téléconsultation** | Architecture préparée en VI (type RDV, champ `video_link`, lien externe manuel). Session vidéo native (WebRTC) en VC |
| **Télé-expertise augmentée** | Workflow complet fonctionnel en VI (collecte terrain → IA → validation médecin interne). Accès expert externe et réseau partenaires en VC |
| **Facturation** | Module complet en VI (CCAM, tiers payant, cumul actes, reste à charge, export FEC). FSE SESAM-Vitale → VC |
| **Portail Patient** | 11 fonctionnalités maintenues en VI — périmètre complet |
| **Accessibilité** | WCAG 2.1 AA **transversale** à toute l'application (niveau Synthétique Orienté Médical — voir §15) |
| **Vue statuts épisode** | Vue simplifiée 3 états (En cours / En attente médecin / Terminé) pour rôles non-médicaux, en plus de la vue complète 10 statuts |
| **KPIs** | Colonnes *Méthode de mesure* et *Fréquence* ajoutées à la table KPIs (§5.10) |
| **Triage VI** | Questionnaire dynamique et adaptatif |
| **Triage VC** | Chatbot IA intégré conversationnel |
| **Préconsult./Consult./Post-consult.** | 1 entité « Épisode de Soin » — 3 onglets distincts |
| **Chatbot post-consultation** | Oui — strictement limité au dossier patient |
| **Assistant IA en consultation** | Oui — mode copilote discret |
| **Réseau d'experts** | Fonctionnalité transversale (pas de module dédié VI) |
| **Backend** | Python / FastAPI |
| **Mission terrain domicile** | Prévu — non prioritaire VI |
| **RDV couplés Holter ECG** | Création automatique RDV retrait : 24h→J+1, 48h→J+2, 72h→J+3, 14j→J+14 |
| **RDV couplés MAPA** | Création automatique RDV retrait J+1 |
| **Champ « Adressé par »** | Intégré fiche administrative |
| **Statut remboursement** | Intégré fiche administrative + facturation |
| **Structure de référence** | Intégrée fiche administrative |
| **Rôle IPA** | Intégré dans droits — suivi maladies chroniques |
| **Score complétude** | Pondéré — patient + épisode |
| **États IA robustes** | En attente → Échec (5 états) |
| **Rules Engine validation métier** | Avant persistance données IA |
| **Planning unifié (RDV + missions)** | Vue unique agenda |
| **PWA / Offline-first** | Pour missions terrain — stratégie Conflict-Aware |
| **Badges de confiance IA par champ** | Dans toutes les interfaces de validation |
| **4 modalités de consultation** | Synchrone présentielle, synchrone distancielle, asynchrone présentielle, asynchrone distancielle |
| **Workflow unifié** | Prise de RDV → Préconsultation → Consultation → Post-consultation |
| **Gouvernance prompts** | Globaux super-admin ; spécifiques admin tenant |
| **Consentement asynchrone** | 2 consentements requis |
| **Champs dynamiques examens** | Créés auto par IA selon type |
| **Flexibilité providers IA** | Pattern provider agnostique + fallback |
| **Séparation back/front termes** | IDs techniques back / libellés naturels front |
| **Mission terrain groupe/individuel** | `patient_count` + `is_group_visit` — pas de type dédié |
| **Préconsultation par équipe externe** | **EXCLUE** — responsabilité médicale |
| **Ordonnances numériques** | Workflow brouillon→signé, signature SHA-256, permissions doctor/ipa |
| **Export PDF épisode** | ReportLab, StreamingResponse |
| **Command Palette** | `Ctrl/Cmd + K`, 10 raccourcis, WCAG 2.1 AA |
| **CI/CD** | GitHub Actions 4 jobs |
| **Suite E2E** | Playwright Chromium |

---

### 9.2 Points encore ouverts

| Sujet | Statut | Version cible |
|---|---|---|
| Contenu détaillé fiche médicale | À finaliser | VI |
| Partenariat facturation externe (cas particuliers CCAM + NGAP) | À évaluer | VI / VC |
| Modèles IA spécifiques retenus (OpenAI / Anthropic / Mistral…) | À définir phase technique | VI |
| Détail droits par rôle | Voir §14 (matrice RBAC) | VI |
| Géolocalisation temps réel missions | À spécifier | VC |
| Analyse images médicales par IA Vision (ECG, écho, radio) | À spécifier | VC |
| Intégration DMP / HL7 FHIR / Carte Vitale | Architecture préparée VI — implémentation | VC |
| Module Triage conversationnel patient (chatbot) | À spécifier | VC |
| Transcription audio Whisper (API réelle) | Mock en VI | VC |
| HSM + signature qualifiée eIDAS | À spécifier | VC |
| Pro Santé Connect (SSO national) | À spécifier | VC |
| FSE SESAM-Vitale | À spécifier | VC |
| Expansion linguistique (EN, ES, IT) | À spécifier | VC |
| Application mobile native (iOS/Android) | À spécifier | VInt |
| IA prédictive & analytics avancées | À spécifier | VInt |
| Expansion géographique (FDA/HIPAA/PIPEDA) | À spécifier | VInt |

---

### 9.3 Matrice des Risques & Mitigations

| Risque | Probabilité | Impact | Mitigation VI |
|---|---|---|---|
| Hallucination IA / proposition erronée | Moyenne | 🔴 Critique | Rules Engine + validation médecin obligatoire + disclaimers permanents |
| Panne API IA / provider indisponible | Moyenne | 🟡 Élevé | Fallback multi-provider + mode manuel |
| Données incomplètes en analyse IA | Moyenne | 🟡 Élevé | Score complétude bloquant + warning |
| Fuite données inter-tenant | Faible | 🔴 Critique | RLS stricte (PostgreSQL prod) + audits auto + chiffrement repos |
| Non-conformité HDS / RGPD | Faible (VI) / Moyenne (VC) | 🔴 Critique | VI : hébergement standard acceptable (usage interne) · VC : Cloud souverain UE + juriste obligatoire |
| Adoption insuffisante | Moyenne | 🟡 Élevé | UX mobile-first + mode manuel conservé + formation équipe cabinet |
| Surcharge serveur | Faible (VI mono-cabinet) | 🟡 Élevé | Rate limiting + **cache Redis** + scalabilité FastAPI |
| Perte connectivité terrain | Élevée | 🟡 Élevé | PWA offline-first + sync auto Conflict-Aware |
| **Conflits sync offline champs médicaux** | Moyenne | 🔴 Critique | **Conflict-Aware Engine** : arbitrage utilisateur obligatoire — aucune valeur médicale écrasée silencieusement |
| Tests sécurité incomplets en dev SQLite | Élevée (VI dev) | 🟡 Élevé | Instance PostgreSQL distante dédiée aux tests de sécurité (RLS, audit trail) |
| Régression tests | Moyenne | 🟡 Élevé | CI 4 jobs + Playwright E2E |

---

## 10. Annexe — User Stories & Critères d'Acceptation

> **Convention** : 🔴 P0 MVP indispensable — 🟡 P1 Important — 🟢 P2 Ultérieur / V2

### 10.1 Authentification & Sécurité

| ID | User Story | Critères d'acceptation | Priorité |
|---|---|---|---|
| US-AUTH-01 | Praticien — connexion sécurisée | Email/MDP (12 car. min), MFA TOTP opt., session 24 h + refresh 7 j, verrouillage 5 essais (15 min), redirection rôle | 🔴 P0 |
| US-AUTH-02 | Admin — gérer utilisateurs du tenant | CRUD, attribution rôles, désactivation, reset MDP email (1 h), journal connexions (IP/UA/timestamp) | 🔴 P0 |
| US-AUTH-03 | Utilisateur — reset MDP | Lien email 1 h, validation complexité, invalidation sessions, notification email | 🟡 P1 |
| US-AUTH-04 | Utilisateur — voir/gérer sessions actives | Liste device/IP/date, révocation, alerte nouvelle connexion appareil inconnu | 🟢 P2 |

### 10.2 Gestion du Dossier Patient

| ID | User Story | Critères | Priorité |
|---|---|---|---|
| US-PAT-01 | Secrétaire — créer fiche administrative | Civilité, nom, prénom, DDN, sexe, téléphones, adresse, email, NIR (clé), médecin traitant + RPPS, statut remboursement, structure, assurance | 🔴 P0 |
| US-PAT-02 | IPA/Infirmier — saisir anamnèse | Motif, histoire, contexte, transcription vocale + diarisation | 🔴 P0 |
| US-PAT-03 | IPA/Infirmier — renseigner terrain | Antécédents JSON par catégorie, facteurs risque CV, traitements (nom/dosage/posologie/date/prescripteur) | 🔴 P0 |
| US-PAT-04 | IPA/Infirmier — saisir mode de vie | Tabac, alcool, drogues, alimentation, activité, sommeil — enums + quantités | 🟡 P1 |
| US-PAT-05 | IPA/Infirmier — allergies | Liste (allergène, réaction, sévérité, date), flag « médicamenteuse » UI | 🔴 P0 |
| US-PAT-06 | IPA/Infirmier — examen clinique ciblé | Constantes (poids, taille, IMC auto, TA, FC, SpO₂, T°), examen spécialité | 🔴 P0 |
| US-PAT-07 | Praticien — score complétude temps réel | Calcul pondéré, badge couleur, liste champs manquants priorisés | 🔴 P0 |
| US-PAT-08 | Praticien — rechercher patient | Recherche nom/prénom/NIR/DDN, auto-complétion 3 car., Soundex, < 200 ms | 🔴 P0 |
| US-PAT-09 | Praticien — historique chronologique | Timeline consult/examens/missions/docs/ordonnances + traçabilité | 🟡 P1 |

### 10.3 Épisodes de Soin

| ID | User Story | Critères | Priorité |
|---|---|---|---|
| US-TE-01 | Secrétaire — créer demande consultation/RDV | Origine, envoi consentement auto, création épisode selon modalité, assignation médecin | 🔴 P0 |
| US-TE-02 | Système — gérer consentement patient | PDF + signature électronique/checkbox certifiée, stockage horodaté immuable, relance J+3 | 🔴 P0 |
| US-TE-03 | IPA/Infirmier — saisir données terrain | Formulaires par onglets, upload docs, score complétude visible | 🔴 P0 |
| US-TE-04 | Praticien — file d'attente épisodes | Code couleur, tri priorité/date, filtres, full-text | 🔴 P0 |
| US-TE-05 | Système — déclencher analyse IA auto | Si complétude ≥ 70 % + consentement OK, états visibles, skeleton, timeout 2 min | 🔴 P0 |
| US-TE-06 | Praticien — valider IA côte-à-côte | Sources vs propositions, badges confiance, accepter/modifier/rejeter + justification | 🔴 P0 |
| US-TE-07 | Praticien — générer & signer CR | Template, pré-remplissage IA, édition, signature électronique, scellement, horodatage | 🔴 P0 |
| US-TE-08 | Système — envoyer CR médecin traitant | PDF, messagerie sécurisée/email, AR, archivage GED | 🟡 P1 |
| US-TE-09 | Système — bloquer cas urgents | Alerte rouge, blocage transition, message « Appelez le 15 », notification | 🔴 P0 |

### 10.4 Missions Terrain

| ID | User Story | Critères | Priorité |
|---|---|---|---|
| US-FV-01 | Secrétaire — planifier mission | Liée épisode, mode (interne/distant), flag groupe + `patient_count`, assignation, créneau ou butoir, check-list dyn. | 🔴 P0 |
| US-FV-02 | IPA/Infirmier — voir missions du jour | Filtre date/statut/patient, taux complétion visible | 🔴 P0 |
| US-FV-03 | IPA/Infirmier — exécuter check-list | Items cochables, alertes Rules Engine, upload photo/doc, offline + sync différée | 🔴 P0 |
| US-FV-04 | Système — synchroniser mission ↔ épisode | Mappings statuts + notification auto médecin | 🔴 P0 |
| US-FV-05 | Secrétaire — reporter/annuler mission | Drag&drop, relance staff, notification patient, raison obligatoire | 🟡 P1 |

### 10.5 Intelligence Artificielle & Examens

| ID | User Story | Critères | Priorité |
|---|---|---|---|
| US-AI-01 | Système — structurer documents auto | OCR + NER → JSON, remplissage champs, score confiance | 🔴 P0 |
| US-AI-02 | Système — valider via Rules Engine | Plages physio, cross-checks, enums ; `manual_required` si bloquant | 🔴 P0 |
| US-AI-03 | Médecin — voir confiance propositions | Badges 🟢🟡🔴, tooltip, surlignage | 🔴 P0 |
| US-AI-04 | Médecin — feedback IA | Widget 5 étoiles + commentaire, flag « modifié » auto, `ai_feedback` | 🟡 P1 |
| US-AI-05 | Admin — configurer prompts IA tenant | Back-office, édition versionnée (semver), test sandbox, rollback, historique | 🟡 P1 |
| US-EXAM-01 | Praticien — créer examen structuré | Types par spécialité (ECG, écho, biologie, MAPA, Holter, polygraphie), champs structurés, upload | 🔴 P0 |
| US-EXAM-02 | Praticien — pré-analyse IA résultats structurés | Interprétation données chiffrées/texte (pas image VI), diagnostic différentiel, RAG | 🔴 P0 |

### 10.6 Portail Patient

| ID | User Story | Critères | Priorité |
|---|---|---|---|
| US-PT-01 | Patient — créer compte sécurisé | Email, validation SMS/code, MFA opt., politique MDP | 🟡 P1 |
| US-PT-02 | Patient — déposer documents | Upload PDF/JPG/PNG, description, attribution proposée, confirmation | 🟡 P1 |
| US-PT-03 | Patient — consulter CR finalisés | Lecture seule, PDF, téléchargement, liste chronologique | 🟡 P1 |
| US-PT-04 | Patient — signer consentement en ligne | Formulaire, signature électronique/checkbox certifiée, email, horodatage | 🟡 P1 |
| US-PT-05 | Patient — prendre RDV en ligne | Créneaux par type/praticien, confirmation, rappels, annulation jusqu'à 24 h | 🟡 P1 |

---

## 11. Roadmap

> **Légende des versions :**
> - **VI** — Version Initiale : cabinet médical du fondateur, équipe interne, toutes fonctionnalités exploitables
> - **VC** — Version Commerciale : expansion multi-cabinets, HDS certifié, connecteurs interop fonctionnels
> - **VInt** — Version Internationale : expansion géographique, mobile natif, IA prédictive

---

### VI — Version Initiale (Phases 1 à 10)

---

#### Phase 1 — Bootstrap & Infrastructure

- Initialisation projet (FastAPI + Next.js + SQLAlchemy + Alembic)
- Configuration JWT + bcrypt + OAuth2
- Pipeline CI/CD GitHub Actions (4 jobs : backend-tests, frontend-build, alembic-check, e2e-tests)
- Base de données SQLite (dev local) / PostgreSQL (prod) avec bascule automatique via `DATABASE_URL`
- **Redis** : intégration dès le départ (cache, file de tâches async, rate limiting)
- **`tenant_id`** : propagé sur toutes les tables dès cette phase (architecture multi-tenant préparée)
- **Interopérabilité Option C** : création table `external_integration_logs` + stubs `BaseConnector` + endpoints réservés HTTP 501

---

#### Phase 2 — Authentification & RBAC

- Authentification complète (login, logout, MFA TOTP setup/verify/disable)
- RBAC 7 rôles avec middleware `require_role()`
- Comptes utilisateurs seed par rôle
- DashboardLayout avec sidebar RBAC-aware
- Protection de routes JWT côté frontend
- Pages d'atterrissage différenciées par rôle (§5.1)

---

#### Phase 3 — Dossier Patient

- CRUD patient complet (fiche administrative + médicale)
- Score de complétude pondéré (9 champs, 100 %)
- Consentement patient (génération + signature + horodatage)
- Recherche patient (nom/prénom/NIR/DDN, Soundex, < 200 ms) — **résultats mis en cache Redis**

---

#### Phase 4 — Épisodes de Soin

- Workflow 10 statuts complet
- **Vue simplifiée 3 états** pour rôles non-médicaux (En cours / En attente médecin / Terminé)
- 3 onglets (Préconsultation / Consultation / Post-consultation)
- Smart Input Button (dictée vocale, OCR, caméra, saisie manuelle)
- Bouclier de sécurité (alertes valeurs critiques)
- Consentement asynchrone (×2)

---

#### Phase 5 — Intelligence Artificielle

- Vue diff IA côte-à-côte (sources vs propositions)
- Badges de confiance par champ (🟢🟡🔴)
- `rules_engine.py` — validation physiologique avant persistance
- `ai_service.py` — abstraction provider agnostique (OpenAI / Anthropic / Gemini / Mistral)
- **pgvector** : vectorisation base de connaissances RAG (instance PostgreSQL prod/tests)
- `ai_prompt_logs` — journalisation complète des appels IA
- `ai_feedback` — widget feedback 5 étoiles
- Versioning sémantique des prompts système

---

#### Phase 6 — Module Triage

- `triage_engine.py` — scoring P1–P5
- File d'attente avec auto-rafraîchissement polling 30 s (P3–P5)
- **WebSocket `/ws/triage`** — alertes temps réel P1 et P2 (urgences vitales) ✅ avancé de VC → VI
- VitalBadge avec seuils d'alarme visuels
- Workflow `waiting → called → in_progress → completed / cancelled`

---

#### Phase 7 — Agenda & Missions Terrain

- Planning unifié (RDV cabinet + missions terrain + télé-expertise)
- RDV couplés automatiques : Holter 24h/48h/72h/14j + MAPA
- Missions terrain : check-list dynamique, modes interne/distant, groupe/individuel
- Synchronisation bidirectionnelle mission ↔ épisode
- **Sync engine Conflict-Aware** : `sync_engine.py` (backend) + `sync.ts` (frontend)
- Drag & drop, filtres, export iCal
- **Télé-expertise augmentée** : entité `TeleexpertiseRequest`, workflow complet,
  SLA automatique, double consentement, lien mission ↔ épisode
- **Téléconsultation** : type RDV créé, champ `video_link`, notification patient
  avec lien externe — session vidéo native en VC

---

#### Phase 8 — Ordonnances Numériques & Facturation

- **Ordonnances** : workflow complet `brouillon → signé → envoyé → annulé`
- Signature électronique ordonnances (SHA-256)
- Permissions strictes : création/modif doctor+ipa, signature doctor uniquement
- Suggestions DCI, panneau latéral sticky
- **Facturation complète** :
  - Codage automatique CCAM
  - Gestion règles de cumul d'actes
  - Calcul reste à charge
  - Tiers payant SS + part complémentaire mutuelle
  - Export comptable FEC
  - Adaptable nomenclatures internationales (préparation VInt)
- ⚠️ FSE SESAM-Vitale → VC (dépendance infrastructure SESAM)

---

#### Phase 9 — i18n & Paramètres IA

- i18n FR/EN complet (switcher sidebar, 9 namespaces)
- Interface Paramètres IA : édition prompts versionnés par tenant
- Module Admin Users (CRUD utilisateurs par admin_master)

---

#### Phase 10 — Export, Messagerie Préparée, CI/CD & Tests

- Export PDF ReportLab (épisode complet, StreamingResponse)
- Command Palette (`Ctrl/Cmd + K`, 10 raccourcis, WCAG 2.1 AA)
- **Messagerie sécurisée** :
  - Tables `messages` créées et migrées
  - Messagerie interne fonctionnelle (médecins ↔ paramédicaux)
  - Interfaces `BaseMessagingConnector` définies
  - Endpoints réservés HTTP 501 pour messagerie externe (MSSanté CI-SIS)
  - Messagerie externe prête pour implémentation en VC sans refonte
- **Accessibilité WCAG 2.1 AA transversale** : audit et corrections sur tous les modules (voir §15)
- CI/CD GitHub Actions 4 jobs finalisé
- Suite Playwright E2E complète
- Tests de sécurité PostgreSQL (RLS + audit trail) sur instance dédiée

---

### VC — Version Commerciale (post-VI)

> Déclenchée si décision d'expansion commerciale prise après validation de la VI en cabinet.

**Infrastructure & Conformité**
- Migration hébergement → Cloud souverain européen certifié **HDS**
- Activation complète **RLS PostgreSQL** (multi-tenant strict)
- Généralisation `tenant_id` sur toutes les tables (déjà préparé en VI)
- HSM + signature qualifiée **eIDAS**
- Pen-test annuel + bug bounty
- Détection d'anomalies comportementales

**Interopérabilité (connecteurs fonctionnels)**
- Carte Vitale (lecteur CPS/CPE)
- MSSanté (Messagerie Sécurisée de Santé — CI-SIS)
- DMP (Dossier Médical Partagé — CDA R2)
- HL7 FHIR R4
- PACS / DICOM avancé
- **FSE SESAM-Vitale** (Feuille de Soins Électronique)
- **Pro Santé Connect** (SSO national professionnels de santé)

**Messagerie Sécurisée (implémentation fonctionnelle)**
- Messagerie interne médecins ↔ paramédicaux
- Messagerie externe structure ↔ patient
- Messagerie externe structure ↔ médecin traitant
- Chiffrement bout en bout + archivage légal
- Conformité MSSanté (CI-SIS)

**Nouvelles fonctionnalités VC**
- Triage Chatbot IA conversationnel (interview adaptative, détection urgence vitale)
- Analyse images médicales IA Vision (ECG numérisés, écho, radio thoracique)
- Interview Anamnèse IA conversationnelle (portail patient / tablette salle d'attente)
- Géolocalisation & optimisation tournées terrain (check-in/out, routing OSRM/OpenStreetMap)
- WebSocket mises à jour épisodes temps réel
- Transcription audio Whisper (API réelle — mock en VI)
- Scores risque spécialisés : SCORE2 complet (CV), CHA₂DS₂-VASc (FA)
- Module Rapports : tableau de bord analytique, KPIs agrégés, graphiques
- Notifications temps réel complètes
- Messagerie patient : envoi ordonnances email/SMS
- **Expansion linguistique** : Anglais, Espagnol, Italien — RGPD UE, NHS UK, HIPAA préparation

---

### VInt — Version Internationale (post-VC)

**Mobile & Performance**
- Application mobile native (iOS/Android) : push natifs, SQLite local, sync background, caméra optimisée

**IA Avancée**
- IA prédictive & analytics avancées : prédiction décompensation cardiaque, détection patients « perdus de vue », créneaux rappel proactifs (conformité AI Act UE)
- Imagerie avancée DICOM : télé-radiologie complète

**Expansion Géographique**
- Allemand, Portugais, Néerlandais
- Conformité FDA / HIPAA (USA)
- Conformité PIPEDA (Canada)
- Conformité TGA (Australie)

---

## 12. Modèle de Données — 20 entités

### 12.1 Tableau des 20 entités

> **Règle transversale** : `tenant_id` (UUID, FK → `tenants`) est présent sur **toutes les tables** dès la Phase 1.
> L'isolation RLS PostgreSQL est activée en VC. En VI, le filtre `tenant_id` est appliqué au niveau applicatif (middleware FastAPI).

| # | Entité | Table SQL | Description | Phase VI | Activation complète |
|---|---|---|---|---|---|
| 1 | `User` | `users` | Comptes utilisateurs (rôles, spécialité, MFA) | Phase 1 | VI |
| 2 | `Tenant` | `tenants` | Structure médicale multi-tenant | Phase 1 | VI (mono) → VC (multi) |
| 3 | `Patient` | `patients` | Fiche admin + médicale + score complétude | Phase 3 | VI |
| 4 | `Episode` | `episodes` | Épisode de soin (workflow 10 statuts) | Phase 4 | VI |
| 5 | `Appointment` | `appointments` | RDV (consult, exam, field_visit) | Phase 7 | VI |
| 6 | `FieldVisit` | `field_visits` | Mission terrain (check-list, modes) | Phase 7 | VI |
| 7 | `Prescription` | `prescriptions` | Ordonnance numérique (signature SHA-256) | Phase 8 | VI |
| 8 | `TriageEntry` | `triage_entries` | File de triage P1–P5 | Phase 6 | VI |
| 9 | `Consent` | `consents` | Consentement patient (asynch + IA) | Phase 3 | VI |
| 10 | `AIPromptLog` | `ai_prompt_logs` | Audit appels IA (provider, tokens, coût, latence, version) | Phase 5 | VI |
| 11 | `AISystemPrompt` | `ai_system_prompts` | Templates prompts versionnés (semver) par spécialité/tenant | Phase 5 | VI |
| 12 | `AIFeedback` | `ai_feedback` | Retours utilisateurs sur sorties IA (1–5 étoiles) | Phase 5 | VI |
| 13 | `Message` | `messages` | Messagerie sécurisée — interne (VI) · externe MSSanté (VC) | Phase 10 | VI (interne) · VC (externe) |
| 14 | `Billing` | `billings` | Facturation CCAM (cumul, tiers payant, reste à charge) | Phase 8 | VI |
| 15 | `Waitlist` | `waitlists` | Liste d'attente RDV | Phase 7 | VI |
| 16 | `KnowledgeDocument` | `knowledge_documents` | RAG — base de connaissances (guidelines, protocoles, vectorisation pgvector) | Phase 5 | VI |
| 17 | `RiskAssessment` | `risk_assessments` | Scores de risque spécialisés (SCORE2, CHA₂DS₂-VASc) | VC | VC |
| 18 | `TeleexpertiseRequest` | `teleexpertise_requests` | Demande de télé-expertise augmentée (sous-entité épisode) | Phase 4 / 7 | VI |
| 19 | `ExternalIntegrationLog` | `external_integration_logs` | Journal connecteurs interop — **créé Phase 1 (Option C)** | Phase 1 (préparé) | VC (fonctionnel) |
| 20 | `AuditLog` | `audit_logs` | Trail immuable (INSERT ONLY + RLS) | Phase 7 | VI |

---

### 12.2 Détail des champs clés — tables principales

#### `users`

| Champ | Type | Contrainte |
|---|---|---|
| `id` | UUID (String 36) | PK |
| `tenant_id` | UUID | FK → `tenants` — **Phase 1** |
| `email` | String 100 | UNIQUE, NOT NULL |
| `hashed_password` | String 200 | bcrypt, NOT NULL |
| `full_name` | String 100 | NOT NULL |
| `role` | String 50 | ENUM (doctor, ipa, nurse, medical_assistant, secretary, patient, admin_master) |
| `specialty` | String 100 | NULLABLE |
| `mfa_enabled` | Boolean | DEFAULT false |
| `mfa_secret` | String 64 | NULLABLE (TOTP) |
| `is_active` | Boolean | DEFAULT true |
| `created_at` | TIMESTAMPTZ | DEFAULT now() |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() |

---

#### `tenants`

| Champ | Type | Contrainte |
|---|---|---|
| `id` | UUID | PK |
| `name` | String 200 | NOT NULL |
| `slug` | String 100 | UNIQUE, NOT NULL |
| `specialty` | String 100 | NULLABLE |
| `address` | TEXT | NULLABLE |
| `phone` | String 20 | NULLABLE |
| `email` | String 100 | NULLABLE |
| `is_active` | Boolean | DEFAULT true |
| `plan` | ENUM | `internal` (VI) / `commercial` (VC) |
| `hds_certified` | Boolean | DEFAULT false — activé en VC |
| `ai_provider` | String 50 | Provider IA sélectionné pour ce tenant |
| `settings` | JSONB | Paramètres configurables par tenant |
| `created_at` | TIMESTAMPTZ | DEFAULT now() |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() |

---

#### `patients`

| Champ | Type | Contrainte |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | FK → `tenants` — **Phase 1** |
| `civilite` | String 10 | NULLABLE |
| `name` | String 100 | NOT NULL |
| `firstname` | String 100 | NOT NULL |
| `birth_date` | DATE | NOT NULL |
| `sex` | ENUM | M / F / X — NOT NULL |
| `phone` | String 20 | NULLABLE |
| `address` | TEXT | NULLABLE |
| `email` | String 100 | NULLABLE |
| `nir` | String 15 | UNIQUE, CHECK (clé Luhn) |
| `medecin_traitant` | String 100 | NULLABLE |
| `rpps_medecin` | String 11 | NULLABLE |
| `ref_structure` | String 200 | NULLABLE |
| `insurance_info` | JSONB | NULLABLE |
| `status_remboursement` | ENUM | parcours_coord / hors_parcours / ald / cmu_c / acs / maternite |
| `addressed_by` | String 200 | NULLABLE |
| `completeness_score` | INT | 0–100, calculé auto via `calculate_patient_score()` |
| `created_at` | TIMESTAMPTZ | DEFAULT now() |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() |

---

#### `episodes`

| Champ | Type | Contrainte |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | FK → `tenants` — **Phase 1** |
| `patient_id` | UUID | FK → `patients` |
| `doctor_id` | UUID | FK → `users` |
| `modality` | ENUM | synch_pres / synch_dist / asynch_pres / asynch_dist |
| `category` | ENUM | initiale / controle / suivi |
| `status` | ENUM | pending / consent_sent / consented / collecting / collected / processing / ready_review / reviewing / completed / cancelled |
| `status_simplified` | ENUM (calculé) | en_cours / attente_medecin / termine — **vue rôles non-médicaux** |
| `ai_status` | ENUM | pending / processing / completed / manual_required / failed |
| `motif` | TEXT | NULLABLE |
| `histoire_maladie` | TEXT | NULLABLE |
| `poids_kg` / `taille_cm` | FLOAT | NULLABLE |
| `imc` | FLOAT | Calculé auto |
| `pas` / `pad` / `fc` / `spo2` / `temperature` | FLOAT | NULLABLE |
| `examen_clinique` | JSONB | Ciblé par spécialité |
| `evaluation_risque` | JSONB | Sortie IA |
| `synthese_clinique` | TEXT | Sortie IA |
| `diagnostic_principal` | TEXT | Sortie IA |
| `diagnostics_differentiels` | JSONB | Sortie IA |
| `conduite_a_tenir` | TEXT | Sortie IA |
| `bilan_complementaire` | TEXT | Sortie IA |
| `suivi_recommande` | TEXT | Sortie IA |
| `ordonnances_proposees` | JSONB | Sortie IA |
| `ai_confidence_scores` | JSONB | Par champ |
| `completeness_score` | INT | 0–100 |
| `signed_at` | TIMESTAMPTZ | NULLABLE |
| `signature_hash` | String 64 | SHA-256 |
| `created_at` / `updated_at` | TIMESTAMPTZ | DEFAULT now() |

---

#### `prescriptions`

| Champ | Type | Contrainte |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | FK → `tenants` — **Phase 1** |
| `episode_id` | UUID | FK → `episodes` |
| `patient_id` | UUID | FK → `patients` |
| `prescriber_id` | UUID | FK → `users` (rôle doctor/ipa) |
| `status` | ENUM | brouillon / signe / envoye / annule |
| `lines` | JSONB | `[{dci, forme, dosage, posologie, duree, quantite, renouvelable, instructions}]` |
| `signature_hash` | String 64 | SHA-256 |
| `signed_at` | TIMESTAMPTZ | NULLABLE |
| `signed_by` | UUID | FK → `users` (rôle doctor uniquement) |
| `validity_months` | INT | DEFAULT 3 |
| `created_at` / `updated_at` | TIMESTAMPTZ | DEFAULT now() |

---

#### `triage_entries`

| Champ | Type | Contrainte |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | FK → `tenants` — **Phase 1** |
| `patient_id` | UUID | FK NULLABLE (anonyme possible) |
| `pas` / `pad` / `fc` / `spo2` / `temperature` / `freq_resp` / `glycemie` | FLOAT | NULLABLE |
| `signes_alarme` | JSONB | Liste structurée |
| `mode_arrivee` | ENUM | pieds / brancard / smur / autre |
| `antecedents_flag` | Boolean | |
| `pediatrique` | Boolean | |
| `grossesse` | Boolean | |
| `priority` | ENUM | P1 / P2 / P3 / P4 / P5 |
| `priority_color` | ENUM | rouge / orange / jaune / vert / bleu |
| `score_numerique` | INT | 0–100 |
| `rules_declenchees` | JSONB | |
| `action_recommandee` | TEXT | |
| `orientation` | ENUM | cabinet / infirmerie / urgences / reanimation / smur |
| `temps_attente_max` | INT (min) | |
| `status` | ENUM | waiting / called / in_progress / completed / cancelled |
| `created_at` / `updated_at` | TIMESTAMPTZ | DEFAULT now() |

---

#### `billings`

| Champ | Type | Contrainte |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | FK → `tenants` — **Phase 1** |
| `episode_id` | UUID | FK → `episodes` |
| `patient_id` | UUID | FK → `patients` |
| `created_by` | UUID | FK → `users` |
| `status` | ENUM | brouillon / validee / envoyee / payee / annulee |
| `actes` | JSONB | `[{code_ccam, libelle, quantite, montant_base, taux_remboursement}]` |
| `montant_total` | FLOAT | Calculé auto |
| `part_ss` | FLOAT | Calculé selon statut patient |
| `part_mutuelle` | FLOAT | NULLABLE |
| `reste_a_charge` | FLOAT | Calculé auto |
| `tiers_payant_ss` | Boolean | DEFAULT false |
| `depassement_honoraires` | FLOAT | NULLABLE (interdit CMU-C) |
| `export_fec_at` | TIMESTAMPTZ | NULLABLE |
| `created_at` / `updated_at` | TIMESTAMPTZ | DEFAULT now() |

---

#### `messages`

| Champ | Type | Contrainte |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | FK → `tenants` — **Phase 1** |
| `sender_id` | UUID | FK → `users` |
| `recipient_id` | UUID | FK → `users` NULLABLE |
| `recipient_patient_id` | UUID | FK → `patients` NULLABLE |
| `channel` | ENUM | `internal` / `external_patient` / `external_medecin` / `mssante` |
| `subject` | String 200 | NULLABLE |
| `body` | TEXT | NOT NULL |
| `attachments` | JSONB | `[{filename, url, size, mime_type}]` |
| `is_read` | Boolean | DEFAULT false |
| `status` | ENUM | `stub` (VI) / `sent` / `delivered` / `failed` (VC) |
| `mssante_message_id` | String 200 | NULLABLE — référence MSSanté (VC) |
| `created_at` | TIMESTAMPTZ | DEFAULT now() |

> **Note** :
> - `channel = internal` : messagerie interne entre membres du cabinet — VI.
> - `channel = external_patient / external_medecin / mssante` : messagerie externe — VC uniquement. En VI, l'interface affiche un bandeau permanent :   « Messagerie externe (MSSanté) disponible en Version Commerciale ».

---

#### `external_integration_logs` *(créée Phase 1 — Option C)*

| Champ | Type | Contrainte |
|---|---|---|
| `id` | UUID | PK |
| `tenant_id` | UUID | FK → `tenants` |
| `connector_type` | ENUM | `carte_vitale` / `mssante` / `dmp` / `fhir` / `dicom` / `sesam_vitale` |
| `direction` | ENUM | `inbound` / `outbound` |
| `status` | ENUM | `stub` (VI) / `pending` / `success` / `failed` (VC) |
| `endpoint_called` | String 200 | Route appelée |
| `payload` | JSONB | Données échangées (anonymisées si sensibles) |
| `response_code` | INT | Code HTTP retourné |
| `error_message` | TEXT | NULLABLE |
| `duration_ms` | INT | Latence en millisecondes |
| `created_at` | TIMESTAMPTZ | DEFAULT now() |

> **Note** : En VI, tous les enregistrements ont `status = stub`. Cela permet de tracer les appels simulés et de valider le bon fonctionnement des stubs avant l'implémentation réelle en VC.

---

#### `teleexpertise_requests`

| Champ | Type | Contrainte |
|-------|------|------------|
| `id` | UUID | PK |
| `tenant_id` | UUID | FK → `tenants` — Phase 1 |
| `episode_id` | UUID | FK → `episodes` |
| `patient_id` | UUID | FK → `patients` |
| `requesting_doctor_id` | UUID | FK → `users` (rôle doctor) |
| `field_visit_id` | UUID | FK → `field_visits` NULLABLE |
| `status` | ENUM | `draft` / `scheduled` / `collecting` / `collected` / `processing` / `ready_review` / `completed` / `cancelled` |
| `priority` | ENUM | `standard` / `prioritaire` / `urgence` |
| `motif` | TEXT | NOT NULL |
| `sla_deadline_at` | TIMESTAMPTZ | Calculé selon priorité dès réception dossier complet |
| `consent_asynch_signed_at` | TIMESTAMPTZ | NULLABLE |
| `consent_ai_signed_at` | TIMESTAMPTZ | NULLABLE |
| `video_link` | String 500 | NULLABLE — URL session externe (téléconsultation VI) |
| `completeness_score_at_processing` | INT | Score clinique au moment du passage en analyse |
| `expert_response` | JSONB | NULLABLE — VC uniquement |
| `expert_id` | UUID | FK → `users` NULLABLE — VC uniquement |
| `created_at` | TIMESTAMPTZ | DEFAULT now() |
| `updated_at` | TIMESTAMPTZ | DEFAULT now() |

> **Note** :
> - En VI, `expert_id` et `expert_response` sont toujours `NULL` — la validation
>   est réalisée par le médecin interne du cabinet.
> - Le champ `video_link` est partagé avec la téléconsultation synchrone distancielle
>   (lien externe saisi manuellement en VI).

---

### 12.3 Règle transversale `tenant_id` — Récapitulatif

| Table | `tenant_id` présent | Phase d'introduction | Isolation active |
|---|---|---|---|
| `users` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `tenants` | — (table racine) | Phase 1 | — |
| `patients` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `episodes` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `appointments` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `field_visits` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `prescriptions` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `triage_entries` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `consents` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `ai_prompt_logs` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `ai_system_prompts` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `ai_feedback` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `messages` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `billings` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `waitlists` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `knowledge_documents` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `risk_assessments` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `teleexpertise_requests` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `external_integration_logs` | ✅ | Phase 1 | Applicatif VI / RLS VC |
| `audit_logs` | ✅ | Phase 1 | INSERT ONLY + RLS VC |

---

## 13. Inventaire API — 40+ endpoints

### 13.1 Endpoints VI — 40 endpoints

| Méthode | Route | Auth | Rôles | Description |
|---|---|---|---|---|
| POST | `/api/auth/login` | Non | Tous | Connexion → JWT Bearer (24 h) |
| GET | `/api/auth/me` | JWT | Tous | Profil utilisateur courant |
| POST | `/api/auth/mfa/setup` | JWT | Tous | Génère secret TOTP + QR code |
| POST | `/api/auth/mfa/verify` | JWT | Tous | Vérifie code TOTP |
| POST | `/api/auth/mfa/disable` | JWT | Tous | Désactive MFA (avec confirmation) |
| GET | `/api/patients` | JWT | Tous | Liste patients (filtre `?q=`) |
| POST | `/api/patients` | JWT | doctor, ipa, secretary, medical_assistant, admin_master | Créer patient |
| GET | `/api/patients/{id}` | JWT | Tous (du tenant) | Détail patient |
| PUT | `/api/patients/{id}` | JWT | doctor, ipa, secretary, medical_assistant, admin_master | Modifier patient + recalc complétude |
| POST | `/api/episodes` | JWT | Tous (sauf patient) | Créer épisode |
| GET | `/api/episodes/{id}` | JWT | Tous (du tenant) | Détail épisode |
| PUT | `/api/episodes/{id}` | JWT | Tous (sauf patient) | Modifier + Rules Engine auto |
| POST | `/api/episodes/{id}/analyze` | JWT | doctor, ipa | Déclencher analyse IA (complétude ≥ 70 % + consentement) |
| POST | `/api/episodes/{id}/calculate-scores` | JWT | Tous (sauf patient) | Recalculer scores risque/complétude |
| GET | `/api/episodes/{id}/export-pdf` | JWT | Tous (du tenant) | Exporter PDF ReportLab |
| GET | `/api/agenda/appointments` | JWT | Tous | Liste RDV (filtres date/intervenant) |
| POST | `/api/agenda/appointments` | JWT | doctor, ipa, secretary, admin_master | Créer RDV (+ retrait auto Holter/MAPA) |
| GET | `/api/agenda/missions` | JWT | Tous | Liste missions terrain |
| POST | `/api/agenda/missions` | JWT | doctor, ipa, nurse, secretary, admin_master | Créer mission + check-list |
| PUT | `/api/agenda/missions/{id}` | JWT | doctor, ipa, nurse | MAJ mission + sync statut épisode |
| GET | `/api/ai/prompts` | JWT | doctor, ipa, admin_master | Liste prompts système |
| PUT | `/api/ai/prompts/{key}` | JWT | admin_master (globaux) / admin tenant (spécifiques) | Modifier prompt + versioning auto |
| POST | `/api/ai/transcribe` | JWT | Tous (sauf patient) | Transcription audio |
| POST | `/api/ai/ocr` | JWT | Tous (sauf patient) | OCR document |
| POST | `/api/triage` | JWT | doctor, ipa, nurse, medical_assistant, secretary | Créer entrée triage + scoring P1–P5 |
| GET | `/api/triage` | JWT | Tous (sauf patient) | File triée P1→P5 puis FIFO |
| GET | `/api/triage/{id}` | JWT | Tous (sauf patient) | Détail entrée triage |
| PATCH | `/api/triage/{id}` | JWT | doctor, ipa, nurse, medical_assistant, secretary | MAJ statut workflow |
| DELETE | `/api/triage/{id}` | JWT | doctor, admin_master | Supprimer entrée |
| POST | `/api/prescriptions` | JWT | doctor, ipa | Créer ordonnance (brouillon) |
| GET | `/api/prescriptions` | JWT | Tous (du tenant) | Liste ordonnances |
| GET | `/api/prescriptions/{id}` | JWT | Tous (du tenant) | Détail ordonnance |
| PUT | `/api/prescriptions/{id}` | JWT | doctor, ipa | Modifier ordonnance (brouillon) |
| POST | `/api/prescriptions/{id}/sign` | JWT | **doctor uniquement** | Signer ordonnance (SHA-256) |
| DELETE | `/api/prescriptions/{id}` | JWT | doctor, ipa | Supprimer brouillon |
| GET | `/api/admin/users` | JWT | admin_master | Liste utilisateurs |
| GET | `/api/admin/users/{id}` | JWT | admin_master | Détail utilisateur |
| POST | `/api/admin/users` | JWT | admin_master | Créer utilisateur |
| PUT | `/api/admin/users/{id}` | JWT | admin_master | Modifier utilisateur (rôle, statut, reset MDP) |
| WS | `/ws/triage` | JWT | Tous (sauf patient) | WebSocket file de triage — alertes P1/P2 temps réel (VI) |
| GET | `/api/billing` | JWT | doctor, ipa, secretary, admin_master | Liste des factures du tenant |
| POST | `/api/billing` | JWT | doctor, ipa, secretary, admin_master | Créer une facture (codage CCAM auto) |
| PUT | `/api/billing/{id}` | JWT | doctor, ipa, secretary, admin_master | Modifier le statut d'une facture |
| POST | `/api/billing/{id}/fse` | JWT | doctor, secretary | Générer FSE (mock VI — réel VC SESAM-Vitale) |
| GET | `/api/messages` | JWT | Tous (sauf patient) | Liste des messages internes |
| POST | `/api/messages` | JWT | Tous (sauf patient) | Envoyer un message interne |
| GET | `/api/messages/{id}` | JWT | Tous (sauf patient) | Lire un message + marquer comme lu |
| DELETE | `/api/messages/{id}` | JWT | Tous (sauf patient) | Supprimer un message |
| GET | `/api/waitlist` | JWT | doctor, ipa, secretary, admin_master | Liste des patients en attente |
| POST | `/api/waitlist` | JWT | doctor, ipa, secretary, admin_master | Ajouter un patient à la liste |
| PUT | `/api/waitlist/{id}` | JWT | doctor, ipa, secretary, admin_master | Modifier priorité ou statut |
| DELETE | `/api/waitlist/{id}` | JWT | doctor, ipa, secretary, admin_master | Retirer de la liste |
| GET | `/api/agenda/appointments/{id}` | JWT | Tous (du tenant) | Détail RDV (inclut `video_link` pour téléconsultation) |
| POST | `/api/teleexpertise` | JWT | doctor, ipa, secretary, admin_master | Créer demande de télé-expertise (dossier + SLA + consentements) |
| GET | `/api/teleexpertise` | JWT | doctor, ipa, secretary, admin_master | Liste des demandes de télé-expertise |
| GET | `/api/teleexpertise/{id}` | JWT | Tous (du tenant) | Détail demande + statut + SLA restant |
| PUT | `/api/teleexpertise/{id}` | JWT | doctor, ipa, secretary | Mettre à jour statut / lier mission / lier épisode |

### 13.2 Endpoints backlog VC — par domaine fonctionnel

#### Authentification & Sécurité

| Méthode | Route | Auth | Rôles | Description |
|---|---|---|---|---|
| POST | `/api/auth/refresh` | JWT | Tous | Rotation du token de session (fenêtre 7 jours) |
| POST | `/api/auth/psc/callback` | Non | Tous | Callback d'authentification Pro Santé Connect (SSO national) |

#### Facturation

| Méthode | Route | Auth | Rôles | Description |
|---|---|---|---|---|
| GET | `/api/billing/acts` | JWT | doctor, secretary | Nomenclature CCAM réelle — VC |
| POST | `/api/billing/fse` | JWT | doctor, secretary | FSE SESAM-Vitale réelle — VC |

#### Rapports & Analytics

| Méthode | Route | Auth | Rôles | Description |
|---|---|---|---|---|
| GET | `/api/rapports/kpis` | JWT | doctor, admin_master | Tableau de bord KPIs (qualité, IA, performance) |

#### Base de Connaissances (RAG)

| Méthode | Route | Auth | Rôles | Description |
|---|---|---|---|---|
| GET | `/api/knowledge/documents` | JWT | Tous (du tenant) | Liste documents RAG |
| POST | `/api/knowledge/upload` | JWT | doctor, admin_master | Upload document (vectorisation pgvector) |
| DELETE | `/api/knowledge/documents/{id}` | JWT | doctor, admin_master | Supprimer document RAG |
| GET | `/api/knowledge/search` | JWT | Tous | Recherche sémantique vectorielle dans la base de connaissances |

#### Téléconsultation — Vidéo native

| Méthode | Route | Auth | Rôles | Description |
|---------|-------|------|-------|-------------|
| POST | `/api/teleconsultation/{appointment_id}/session` | JWT | doctor, ipa, secretary | Créer session vidéo native (WebRTC/SDK) — VC |
| GET | `/api/teleconsultation/{appointment_id}/session` | JWT | Tous (du tenant) | Rejoindre session vidéo — VC |
| DELETE | `/api/teleconsultation/{appointment_id}/session` | JWT | doctor | Clôturer session vidéo — VC |

#### Télé-expertise — Expert externe

| Méthode | Route | Auth | Rôles | Description |
|---------|-------|------|-------|-------------|
| POST | `/api/teleexpertise/{id}/expert-response` | JWT | expert (VC) | Soumettre réponse structurée de l'expert — VC |

#### Audit

| Méthode | Route | Auth | Rôles | Description |
|---|---|---|---|---|
| GET | `/api/audit` | JWT | doctor, admin_master | Consulter audit trail (lecture seule) |

---

## 14. Matrice RBAC — 7 rôles × tous les modules

**Légende** : ✅ Accès complet · 👁️ Lecture seule ou limitée · ❌ Pas d'accès

### 14.1 Matrice par module

| Module / Action | doctor | ipa | nurse | medical_assistant | secretary | patient | admin_master |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Dashboard** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Patients (lecture)** | ✅ | 👁️ | 👁️ | 👁️ | 👁️ | 👁️ (siens) | ✅ |
| **Patients (création/modif)** | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| **Épisodes de Soin** | ✅ | ✅ | ✅ | ✅ | 👁️ | 👁️ (siens) | ✅ |
| **Analyse IA (déclencher)** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Triage** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **Ordonnances (création/modif)** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Ordonnances (signature)** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Agenda & RDV** | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ (ses RDV) | ✅ |
| **Missions Terrain** | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| **Messagerie** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (cabinet) | ✅ |
| **Facturation** | ✅ | ❌ | ❌ | ❌ | ✅ | 👁️ (siennes) | ✅ |
| **Rapports & Analytics** | ✅ | 👁️ | ❌ | ❌ | 👁️ | ❌ | ✅ |
| **Paramètres IA** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Base de Connaissances (RAG)** | ✅ | 👁️ | 👁️ | ❌ | ❌ | ❌ | ✅ |
| **Portail Patient** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | 👁️ |
| **Gestion Utilisateurs** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Liste d'attente** | 👁️ | ❌ | ❌ | ❌ | ✅ | ✅ (inscription) | ✅ |

### 14.2 Matrice par action (granularité fine)

| Action | admin_master | doctor | ipa | nurse | medical_assistant | secretary | patient |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Gérer tenants (multi-tenant) | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Configurer prompts IA globaux | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Créer / modifier utilisateurs | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Créer dossier patient | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Consulter dossier patient (tous du tenant) | ✅ | ✅ | 👁️ | 👁️ | 👁️ | 👁️ | ❌ |
| Consulter son propre dossier | — | — | — | — | — | — | ✅ |
| Saisir préconsultation / anamnèse | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Réaliser examen clinique / constantes | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Créer / gérer missions terrain | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ |
| Exécuter mission terrain (check-list) | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| Valider / signer épisode de soin | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Modifier proposition IA | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Créer / modifier ordonnance | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Signer ordonnance | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Gérer agenda (RDV + missions) | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ (ses RDV) |
| Créer facture / gérer facturation | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ | 👁️ (ses factures) |
| Envoyer messagerie interne | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Envoyer messagerie externe patient | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (réception) |
| Consulter audit trail | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Exporter données patient | ✅ | ✅ (siens) | ❌ | ❌ | ❌ | ❌ | ✅ (siennes) |
| Configurer paramètres cabinet | ✅ | 👁️ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Middleware RBAC backend** : `require_role(*allowed_roles)` — factory de dépendance FastAPI, retourne HTTP 403 si rôle non autorisé.

---

## 15. Accessibilité — WCAG 2.1 AA (Synthétique Orienté Médical)

> **Principe directeur** : L'accessibilité est **transversale** à toute l'application MedFlow, pas un module isolé.
> Elle s'applique dès la Phase 1 et est vérifiée à chaque phase du développement.
> Le profil cible est **Synthétique Orienté Médical** : interface épurée, dense en information, lisible sous contrainte (urgence, terrain, fatigue).

---

### 15.1 Périmètre & Niveaux de Conformité

| Niveau | Cible | Statut |
|---|---|---|
| WCAG 2.1 A | Toutes les interfaces | ✅ Obligatoire VI |
| WCAG 2.1 AA | Toutes les interfaces | ✅ Obligatoire VI |
| WCAG 2.1 AAA | Sélectif (lecture critique médicale) | 🎯 Effort best-effort |
| EN 301 549 | Conformité européenne (VC) | 📋 Préparé VI |
| RGAA 4.1 | Conformité française (VC) | 📋 Préparé VI |

---

### 15.2 Principes POUR (Perceptible, Utilisable, Compréhensible, Robuste)

#### 15.2.1 Perceptible

**Contraste des couleurs**

| Contexte | Ratio minimum | Ratio cible MedFlow |
|---|---|---|
| Texte normal (< 18pt) | 4.5:1 | **7:1** |
| Texte large (≥ 18pt ou 14pt gras) | 3:1 | **4.5:1** |
| Composants UI (boutons, champs) | 3:1 | **4.5:1** |
| Alertes critiques (P1/P2 triage, valeurs vitales) | 4.5:1 | **≥ 7:1 + icône redondante** |

> MedFlow dépasse les minimums WCAG AA sur tous les éléments médicaux critiques.

**Alternatives textuelles**
- Toute image médicale (ECG, radio, écho) : `alt` descriptif clinique obligatoire
- Icônes décoratives : `aria-hidden="true"`
- Icônes fonctionnelles : `aria-label` explicite
- Badges de confiance IA : texte alternatif « Confiance IA : 87 % — Vérification recommandée »

**Redondance sensorielle (jamais couleur seule)**

| Signal | Couleur | Redondance |
|---|---|---|
| Priorité P1 (triage) | 🔴 Rouge | + Icône ⚠️ + Libellé « CRITIQUE » + `role="alert"` |
| Priorité P2 | 🟠 Orange | + Icône ⚡ + Libellé « URGENT » |
| Badge confiance faible | 🔴 Rouge | + Icône ❌ + Texte « Vérification requise » |
| Badge confiance moyen | 🟡 Jaune | + Icône ⚠️ + Texte « À vérifier » |
| Badge confiance élevé | 🟢 Vert | + Icône ✅ + Texte « Confiance élevée » |
| Statut épisode | Couleur | + Libellé textuel toujours visible |
| Valeur vitale hors norme | Couleur | + Icône + Valeur numérique + unité |

**Médias**
- Transcriptions textuelles pour tout contenu audio (dictée vocale, instructions)
- Sous-titres pour contenus vidéo (téléconsultation — VC)
- Pas d'autoplay audio ou vidéo

---

#### 15.2.2 Utilisable

**Navigation clavier complète**

Toute l'application est utilisable sans souris :

| Action | Raccourci |
|---|---|
| Ouvrir Command Palette | `Ctrl/Cmd + K` |
| Nouveau patient | `Ctrl/Cmd + N` |
| Recherche patient | `Ctrl/Cmd + F` |
| Valider épisode | `Ctrl/Cmd + Enter` |
| Signer ordonnance | `Ctrl/Cmd + S` |
| Annuler / Fermer modal | `Escape` |
| Navigation sidebar | `Tab` / `Shift+Tab` |
| Activation élément focalisé | `Enter` / `Space` |
| Navigation liste patients | `↑` / `↓` |
| Basculer onglet épisode | `Ctrl/Cmd + 1/2/3` |

**Focus visible**
- Outline focus : `3px solid #2563EB` (bleu médical) sur fond blanc — ratio ≥ 3:1 garanti
- Focus trap dans les modales et drawers (pas de focus qui s'échappe)
- Focus retourné à l'élément déclencheur à la fermeture de modale
- Skip link « Aller au contenu principal » en première position du DOM

**Temps suffisant**
- Aucun timeout automatique sur les formulaires médicaux
- Sessions JWT : avertissement 5 min avant expiration avec option de prolongation
- Animations désactivables (`prefers-reduced-motion` respecté partout)

**Pas de piège clavier**
- Toutes les modales, drawers, Command Palette : `Escape` ferme et retourne le focus

**Taille des cibles tactiles**
- Minimum : 44×44 px (WCAG 2.5.5)
- Cibles critiques (Signer, Valider, Alertes P1) : ≥ 48×48 px
- Espacement minimum entre cibles adjacentes : 8 px

---

#### 15.2.3 Compréhensible

**Langue déclarée**
- `<html lang="fr">` ou `<html lang="en">` selon la langue active (i18n dynamique)
- Termes médicaux latins ou abrégés : `<abbr title="...">` systématique

**Libellés & Instructions**
- Tous les champs de formulaire ont un `<label>` explicite associé (jamais `placeholder` seul)
- Champs obligatoires : `aria-required="true"` + indicateur visuel `*` + légende en bas de formulaire
- Instructions de format avant le champ (ex : « Format : JJ/MM/AAAA »)

**Gestion des erreurs**
- Message d'erreur : identifie le champ + décrit le problème + propose la correction
- `aria-describedby` lie le champ à son message d'erreur
- `aria-invalid="true"` sur le champ en erreur
- Focus automatique sur le premier champ en erreur après soumission
- Erreurs critiques (valeur vitale hors plage) : `role="alert"` pour annonce immédiate

**Prévention des erreurs médicales**
- Toute action irréversible (signature, annulation épisode, suppression) : dialogue de confirmation avec résumé de l'action
- Ordonnance : récapitulatif complet avant signature (patient, médicaments, posologies)
- Délai de grâce 30 s avec annulation possible pour les envois (email ordonnance, export)

---

#### 15.2.4 Robuste

**Sémantique HTML**
- Landmarks ARIA : `<main>`, `<nav>`, `<header>`, `<aside>`, `<footer>` sur toutes les pages
- Hiérarchie de titres stricte : `h1` unique par page → `h2` sections → `h3` sous-sections
- Listes : `<ul>/<ol>/<li>` pour toute liste de patients, résultats, médicaments
- Tableaux de données : `<th scope="col/row">` + `<caption>` obligatoires

**Composants interactifs**
- Tous les composants custom (Command Palette, badges, drawers, toasts) implémentent les patterns ARIA Authoring Practices Guide (APG)
- `role`, `aria-expanded`, `aria-selected`, `aria-current`, `aria-live` utilisés correctement
- Pas de `div` ou `span` cliquables sans `role="button"` + `tabindex="0"` + gestion `Enter/Space`

**Annonces dynamiques**

| Événement | Région live | Politesse |
|---|---|---|
| Résultat recherche patient | `aria-live` | `polite` |
| Analyse IA terminée | `aria-live` | `polite` |
| Alerte valeur vitale critique | `role="alert"` | `assertive` |
| Alerte triage P1/P2 (WebSocket) | `role="alert"` | `assertive` |
| Toast succès (sauvegarde, signature) | `aria-live` | `polite` |
| Erreur formulaire | `role="alert"` | `assertive` |
| Sync offline terminée | `aria-live` | `polite` |
| Conflit sync détecté | `role="alert"` | `assertive` |

**Compatibilité technologies d'assistance**
- Lecteurs d'écran : NVDA + Firefox (Windows), VoiceOver + Safari (macOS/iOS)
- Zoom navigateur : 200 % sans perte de contenu ni scroll horizontal
- Zoom texte seul : 200 % (respect `rem`/`em`, pas de `px` pour les tailles de texte)
- Mode contraste élevé Windows : testé et validé

---

### 15.3 Composants Médicaux Critiques — Règles Spécifiques

#### Badges de Confiance IA

```html
<!-- Exemple badge confiance élevée -->
<span
  class="badge badge-high-confidence"
  role="img"
  aria-label="Confiance IA : 94 % — Valeur fiable"
>
  ✅ 94 %
</span>

<!-- Exemple badge confiance faible -->
<span
  class="badge badge-low-confidence"
  role="img"
  aria-label="Confiance IA : 42 % — Vérification médicale requise"
>
  ❌ 42 %
</span>
```

#### Alertes Valeurs Vitales

```html
<div role="alert" aria-atomic="true" class="vital-alert critical">
  <span aria-hidden="true">⚠️</span>
  <strong>Alerte critique</strong> : PAS 185 mmHg — Valeur hors norme.
  Vérification immédiate recommandée.
</div>
```

#### File de Triage — Mises à jour temps réel

```html
<!-- Région live pour les mises à jour polling P3-P5 -->
<div aria-live="polite" aria-label="File de triage — mise à jour automatique">
  <!-- Contenu mis à jour toutes les 30 s -->
</div>

<!-- Alerte assertive pour P1/P2 via WebSocket -->
<div role="alert" aria-atomic="true" aria-label="Alerte triage priorité critique">
  <!-- Injecté dynamiquement par WebSocket -->
</div>
```

#### Formulaires Médicaux

```html
<label for="pas">
  Pression artérielle systolique (mmHg)
  <span aria-hidden="true">*</span>
  <span class="sr-only">(obligatoire)</span>
</label>
<input
  id="pas"
  type="number"
  min="60" max="250"
  aria-required="true"
  aria-describedby="pas-hint pas-error"
  aria-invalid="false"
/>
<span id="pas-hint" class="field-hint">Valeur normale : 90–140 mmHg</span>
<span id="pas-error" role="alert" class="field-error" hidden>
  Valeur hors plage (60–250 mmHg). Vérifiez la mesure.
</span>
```

---

### 15.4 Tests & Validation Accessibilité

#### Outils automatisés (CI/CD)

| Outil | Intégration | Seuil d'échec |
|---|---|---|
| **axe-core** | Playwright E2E — chaque test | 0 violation critique |
| **Lighthouse Accessibility** | GitHub Actions — build | Score ≥ 90 |
| **eslint-plugin-jsx-a11y** | Lint TypeScript | 0 erreur |

#### Tests manuels (par phase)

| Test | Fréquence | Responsable |
|---|---|---|
| Navigation clavier complète (toutes pages) | Chaque phase | Dev |
| VoiceOver macOS (parcours critiques) | Chaque phase | Dev |
| NVDA + Firefox (parcours critiques) | Phases 5, 8, 10 | Dev |
| Zoom 200 % (toutes pages) | Chaque phase | Dev |
| Contraste élevé Windows | Phases 2, 6, 10 | Dev |
| Mode `prefers-reduced-motion` | Phases 4, 7 | Dev |
| Taille cibles tactiles (mobile) | Phases 7, 10 | Dev |

#### Parcours critiques testés en priorité

1. Login + MFA (authentification)
2. Création patient + formulaire fiche médicale
3. Création épisode + validation IA côte-à-côte
4. Signature ordonnance
5. File de triage + alertes P1/P2
6. Command Palette (`Ctrl+K`)
7. Sync offline + arbitrage conflit

---

### 15.5 Déclaration d'Accessibilité (VC)

Une déclaration de conformité WCAG 2.1 AA + RGAA 4.1 sera publiée lors du passage en VC, incluant :
- Périmètre audité
- Non-conformités résiduelles documentées avec plan de correction
- Moyens de contact pour signalement
- Date du dernier audit

> En VI (usage interne cabinet), la déclaration formelle n'est pas obligatoire mais les standards sont appliqués dès le premier commit.

---

**MedFlow — PRD v1.0 Greenfield — Juin 2026 — Document confidentiel — Usage interne uniquement**
**Ce document est la source de vérité unique du projet MedFlow.**

---

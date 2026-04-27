# TP 4.b (bis) — AI Agent **"Briefing matinal"** en no-code avec n8n

> Pendant du **Notebook 2** du TP 4.a (`tp4a-agent-morning-briefing.ipynb`).
> Même use case, même 8 outils, même boucle de réflexion — mais reconstruit avec **n8n** pour comparer **profil dev (Python)** ↔ **profil ops (no-code)**.
>
> **Durée :** ~ 1 h 30 · **Coût :** 0 € (Groq + Google free tier + Slack webhook gratuit) · **Format :** runbook pas-à-pas.

---

## Sommaire

- [0. Pourquoi cette variante ?](#0-pourquoi-cette-variante-)
- [1. Architecture cible](#1-architecture-cible)
- [2. Pré-requis](#2-pré-requis)
- [Étape 1 — Stack Docker (mutualisée)](#étape-1--stack-docker-mutualisée)
- [Étape 2 — Credentials Google OAuth dans n8n](#étape-2--credentials-google-oauth-dans-n8n)
- [Étape 3 — Credentials Slack + Groq](#étape-3--credentials-slack--groq)
- [Étape 4 — Construire le workflow Briefing](#étape-4--construire-le-workflow-briefing)
- [Étape 5 — Tester (manuel puis planifié)](#étape-5--tester-manuel-puis-planifié)
- [Étape 6 — Garde-fous : idempotence & sandbox](#étape-6--garde-fous--idempotence--sandbox)
- [Étape 7 — Comparaison Notebook 2 ↔ n8n](#étape-7--comparaison-notebook-2--n8n)
- [Annexes](#annexes)

---

## 0. Pourquoi cette variante ?

Le briefing matinal est un **workflow récurrent, lourd en intégrations Google**. C'est exactement le terrain où n8n brille : connecteurs Gmail/Calendar/Drive/Slack natifs, gestion OAuth via UI, **Schedule Trigger** intégré (cron 8h30), retries et dead-letter prêts à l'emploi.

Là où le notebook Python apprend la **mécanique interne** d'un agent, le runbook n8n apprend les **réflexes opérationnels** :
- OAuth en 3 clics au lieu de 15 min de Google Cloud Console.
- Cron natif au lieu d'un `papermill` à orchestrer.
- Idempotence et reprise sur erreur **fournies** par le runtime.

Le **fond pédagogique** reste identique (8 outils, 6 patterns Anthropic) — seule la **forme** change.

---

## 1. Architecture cible

```
   ┌─────────────────────┐
   │ Schedule Trigger    │   cron : 30 8 * * 1-5  (lun-ven 8h30)
   │  + bouton manuel    │
   └──────────┬──────────┘
              │
              ▼
   ┌─────────────────────┐
   │ Google Calendar     │   getAll, max 3, timeMin = now
   │ "fetch_calendar"    │
   └──────────┬──────────┘
              │
   ┌──────────┴───────────────┐
   ▼                          ▼
┌──────────────────┐    ┌──────────────────┐
│ Loop Over Items  │    │ Gmail            │
│ "enrich_meetings"│    │ getAll q=is:unread
│  ├─ Gmail search │    │  newer_than:1d   │
│  ├─ Drive search │    │ "scan_inbox"     │
│  └─ Aggregate    │    └────────┬─────────┘
└────────┬─────────┘             │
         │                        ▼
         │              ┌───────────────────┐
         │              │ AI Agent          │
         │              │ "classify_urgency"│  → JSON {urgent: bool}
         │              └────────┬──────────┘
         │                       │
         │                       ▼
         │             ┌─────────────────┐
         │             │ IF urgent==true │
         │             └────┬─────────┬──┘
         │                  │ true    │ false
         │                  ▼         │
         │       ┌────────────────────┐│
         │       │ AI Agent + Gmail   ││
         │       │ "draft_replies"    ││  → crée des drafts (jamais send)
         │       └─────────┬──────────┘│
         │                 │           │
         │                 └────┬──────┘
         │                      ▼
         │            ┌───────────────────┐
         │            │ AI Agent          │
         │            │ "extract_deadlines"│ → JSON [{date, sujet}]
         │            └────────┬──────────┘
         │                     │
         └─────────┬───────────┘
                   ▼
         ┌────────────────────┐
         │ Merge              │   réunit enriched + urgent + deadlines
         └────────┬───────────┘
                  ▼
         ┌────────────────────┐
         │ AI Agent           │
         │ "assemble_briefing"│  → markdown final
         └────────┬───────────┘
                  ▼
         ┌────────────────────┐
         │ AI Agent           │
         │ "grade_briefing"   │  → JSON {ok: bool, missing: []}
         └────────┬───────────┘
                  ▼
         ┌────────────────────┐
         │ IF ok==true        │
         └─┬─────────────────┬┘
           │ true            │ false (1 retry)
           ▼                 ▼
      ┌──────────┐    ┌──────────────────┐
      │ Slack    │    │ retour assemble  │
      │ post msg │    │ (compteur ≤ 1)   │
      └──────────┘    └──────────────────┘
```

**~ 13 nodes n8n** pour les 9 nodes LangGraph du notebook (n8n découpe les boucles et les routes en nodes séparés).

---

## 2. Pré-requis

| Élément | Détail |
|---|---|
| **Stack Docker n8n** | celle du runbook `tp4b-n8n-research-assistant.md` (ne pas dupliquer) |
| **Compte Google dédié** | jamais perso/pro — sandbox uniquement |
| **Clé Groq** | `gsk_...` — <https://console.groq.com> |
| **Webhook Slack** | optionnel — <https://api.slack.com/messaging/webhooks> |
| **Projet Google Cloud** | celui de `tp4a-agent-morning-briefing.ipynb` (réutilisé) avec **un client OAuth supplémentaire** (voir Étape 2) |

---

## Étape 1 — Stack Docker (mutualisée)

Si vous avez déjà fait le runbook **`tp4b-n8n-research-assistant.md`**, votre stack `n8n + Postgres + Qdrant` tourne déjà sur `localhost:5678`. **Rien à refaire.**

Sinon, suivre [`tp4b-n8n-research-assistant.md` § Étape 1](./tp4b-n8n-research-assistant.md#étape-1--lancer-la-stack-docker-n8n--qdrant) — exact même setup. Le briefing matinal **n'utilise pas Qdrant** (on s'appuie sur Gmail/Drive directement) mais ne casse rien si présent.

✅ Vérification minimale :

```bash
curl -s http://localhost:5678 > /dev/null && echo "n8n OK"
```

---

## Étape 2 — Credentials Google OAuth dans n8n

⚠️ **Différence majeure avec le notebook Python** : n8n a besoin d'un client OAuth **de type "Web application"** (pas "Desktop"), parce qu'il fait passer le consentement par un **redirect URL**. Donc le `credentials.json` du notebook **ne fonctionne pas tel quel** — il faut créer un **second client OAuth** dans le même projet GCP.

### 2.1 Récupérer le redirect URL de n8n

Dans n8n : **Settings → Credentials → New → chercher "Google OAuth2 API"**.
Tout en haut, n8n affiche son **OAuth Redirect URL** :

```
http://localhost:5678/rest/oauth2-credential/callback
```

**Copier cette URL** — on en a besoin à l'étape suivante.

### 2.2 Créer le client OAuth Web dans Google Cloud

Sur <https://console.cloud.google.com>, projet `tp4-briefing-agent` (le même qu'au TP 4.a) :

1. **APIs & Services → Credentials → + Create credentials → OAuth client ID**.
2. **Application type** : `Web application`.
3. **Name** : `n8n-briefing-agent`.
4. **Authorized redirect URIs** → **+ ADD URI** → coller le redirect URL de l'étape 2.1.
5. **Create**.
6. Copier les deux valeurs affichées : `Client ID` (`...apps.googleusercontent.com`) et `Client Secret`.

> 💡 Vous avez maintenant **2 clients OAuth** dans le même projet : l'un *Desktop* pour le notebook, l'autre *Web* pour n8n. C'est normal et propre — ils partagent les scopes activés (Gmail, Calendar, Drive).

### 2.3 Renseigner le credential dans n8n

Retour dans la fenêtre `Google OAuth2 API` de n8n :
- **Client ID** : coller la valeur copiée.
- **Client Secret** : coller la valeur copiée.
- **Scope** (par défaut) : OK pour Calendar — on créera des credentials **dédiées** pour Gmail et Drive (ils ont des scopes spécifiques mieux gérés via les credentials typés).

**Save**. Cliquer **Sign in with Google** → consentement (mêmes étapes que le notebook : choisir le compte → "Avancé → Accéder" sur l'avertissement test → autoriser).

### 2.4 Créer 3 credentials Google typés (un par service)

n8n offre des credentials **par service** qui pré-remplissent les bons scopes. Plus propre que le credential générique :

Refaire 3 fois **Settings → Credentials → New** avec :

| Type de credential | Scope auto-géré | Usage |
|---|---|---|
| **Google Calendar OAuth2 API** | `calendar.readonly` | Calendar |
| **Gmail OAuth2 API** | `gmail.modify` | Gmail (read + drafts) |
| **Google Drive OAuth2 API** | `drive.readonly` | Drive |

Pour chaque : réutiliser le **même Client ID / Client Secret** (Étape 2.2), puis **Sign in with Google**. Vous obtenez 3 credentials nommées `Calendar account`, `Gmail account`, `Drive account` (renommer si besoin).

✅ À la fin, votre liste **Credentials** doit contenir au moins ces 3 entrées Google + Groq (Étape 3) + Slack (Étape 3).

---

## Étape 3 — Credentials Slack + Groq

### 3.1 Slack (incoming webhook)

Pas vraiment un *credential* OAuth — un webhook nominatif suffit :
- Créer une **Slack app** sur <https://api.slack.com/apps>.
- **Incoming Webhooks → Activate → Add New Webhook to Workspace** → choisir un canal privé / DM perso.
- Copier l'URL `https://hooks.slack.com/services/T.../B.../...`.

Dans n8n, on l'utilisera **directement dans un node HTTP Request** ou via un credential **Slack Webhook** si vous préférez.

### 3.2 Groq

**Settings → Credentials → New → "OpenAI API"** (Groq est OpenAI-compatible — voir astuce du runbook `tp4b-n8n-research-assistant.md`) :
- **Base URL** : `https://api.groq.com/openai/v1`
- **API Key** : `gsk_...`
- Renommer le credential en `Groq` pour clarté.

---

## Étape 4 — Construire le workflow Briefing

**Workflows → + Add workflow → renommer "Morning Briefing"**.

### 4.1 Schedule Trigger (cron + bouton manuel)

- Node : **Schedule Trigger**.
- **Trigger Interval** : `Cron`.
- **Cron Expression** : `30 8 * * 1-5` (8h30, lun-ven).
- En phase de dev, **désactiver l'activation** et utiliser le bouton **Execute Workflow** (en bas).

> 💡 n8n offre aussi un node **Manual Trigger** parallèle si vous voulez les deux en même temps (manuel pour debug, schedule pour prod).

### 4.2 `fetch_calendar` — Google Calendar

- Node : **Google Calendar**.
- **Credential** : `Calendar account`.
- **Resource** : `Event`.
- **Operation** : `Get Many`.
- **Calendar** : Primary.
- **Return All** : off → **Limit** : `3`.
- **Options → Time Min** : `={{ $now.toISO() }}`.
- **Options → Order By** : `startTime`.
- **Options → Single Events** : true.

Brancher Schedule → Google Calendar.

### 4.3 `enrich_meetings` — Loop + 2 sub-tools

n8n n'a pas de "for-each" implicite : on utilise **Loop Over Items**.

- Node : **Split In Batches** (size: `1`) après Calendar.
- À l'intérieur du loop, en **parallèle** :
  - **Gmail (search)** : `Get Many`, `q` = `{{ $json.attendees ? $json.attendees.map(a => 'from:' + a.email).slice(0,3).join(' OR ') + ' newer_than:14d' : '' }}`, Limit 2, Credential `Gmail account`.
  - **Google Drive (search)** : `Search`, `q` = `name contains '{{ $json.summary?.split(' ')[0] }}'`, Limit 2, Credential `Drive account`.
- **Merge** node après le loop pour réagréger les enriched_events.

### 4.4 `scan_inbox` — Gmail

En parallèle de Calendar (depuis Schedule) :
- Node : **Gmail** (`Get Many`).
- **Filters → Search Query** : `is:unread newer_than:1d`.
- **Limit** : `8`.
- Credential : `Gmail account`.

### 4.5 `classify_urgency` — AI Agent (Tools Agent)

Sur la sortie de `scan_inbox` :
- Node : **Loop Over Items** (1 mail à la fois).
- À l'intérieur : **AI Agent** (Tools Agent).
  - **LLM sub-node** : OpenAI Chat Model (credential `Groq`, model `llama-3.3-70b-versatile`, temperature `0`).
  - **Prompt** :
    ```
    Mail :
      De      : {{ $json.from }}
      Sujet   : {{ $json.subject }}
      Aperçu  : {{ $json.snippet }}

    Ce mail est-il URGENT (action attendue dans la journée) ?
    Réponds UNIQUEMENT par un JSON : {"urgent": true|false, "reason": "..."}
    ```
  - **Output Parser** (sub-node) : `Structured Output Parser` avec un JSON schema `{urgent: boolean, reason: string}` — n8n garantit alors que la sortie est typée.

### 4.6 `IF` — router urgent vs non-urgent

- Node : **IF**.
- Condition : `{{ $json.urgent }} = true`.
- Branche **true** → node `draft_replies`.
- Branche **false** → directement `extract_deadlines`.

### 4.7 `draft_replies` — AI Agent + Gmail

Pour chaque mail urgent :
1. **AI Agent** (LLM Groq) — prompt = "Rédige une réponse polie en français, ne signe pas. Thread : ...". Sortie = `body_text`.
2. **Gmail** node — **Resource** : `Draft`, **Operation** : `Create`. Champs :
   - **To** : extraire l'email depuis `from` (utiliser un node **Code** intermédiaire ou la regex `{{ $json.from.match(/<([^>]+)>/)?.[1] || $json.from }}`).
   - **Subject** : `Re: {{ $json.subject }}`.
   - **Message** : `={{ $('AI Agent').item.json.output }}`.
   - **Options → Thread Id** : `{{ $json.threadId }}`.

Ne **jamais** utiliser l'opération `Send` ici. Pédagogique : le coût d'un envoi automatique mal classé est bien plus élevé qu'un draft "perdu".

### 4.8 `extract_deadlines` — AI Agent

- Node : **Gmail** — `Get Many`, q = `newer_than:3d`, Limit 10.
- Node : **Code** (JavaScript) qui concatène en blob :
  ```javascript
  return [{ json: { blob: items.map(i => `- ${i.json.subject} | ${i.json.snippet}`).join('\n') } }];
  ```
- Node : **AI Agent** avec **Structured Output Parser** :
  ```
  Aujourd'hui : {{ $now.toISODate() }}.
  Mails récents :
  {{ $json.blob }}

  Extrais les deadlines explicitement mentionnées qui tombent dans les 7 prochains jours.
  Schema : [{deadline: "YYYY-MM-DD", sujet: string, source: string}]
  ```

### 4.9 `assemble_briefing` — AI Agent + Merge

- Node : **Merge** (mode `Combine` → `Multiplex`) — réunit `enriched_events`, `urgent_mails`, `drafts_created`, `deadlines` en un seul item.
- Node : **AI Agent** avec prompt :
  ```
  Produis un briefing markdown clair et concis pour l'utilisateur, en français.
  Sections obligatoires :
  1. Réunions du jour (avec contexte)
  2. Mails urgents (mention si un draft a été préparé)
  3. Deadlines de la semaine

  Données JSON :
  {{ JSON.stringify($json) }}

  Briefing :
  ```

### 4.10 `grade_briefing` — Reflection loop

- Node : **AI Agent** + Structured Output Parser :
  ```
  Voici un briefing :
  {{ $json.output }}

  Couvre-t-il (1) réunions, (2) urgents, (3) deadlines ? Clair en 30 s ?
  Schema : {ok: boolean, missing: [string]}
  ```
- Node : **IF** sur `ok === true`.
  - Branche **true** → `post_to_slack`.
  - Branche **false** → retour à `assemble_briefing` **avec un compteur**.

#### Implémentation propre du compteur

n8n n'a pas de variable globale facile. Deux options :
- **A.** Ajouter un node **Set** au démarrage qui initialise `iterations: 0`, et un node **Set** dans la branche retry qui fait `iterations: {{$json.iterations + 1}}`. Conditionner le retry à `iterations < 1`.
- **B.** Plus simple : ne pas faire de retry du tout (au pire, `grade_briefing` ne change rien). Pédagogiquement OK pour ce TP. Mentionner la limite.

### 4.11 `post_to_slack`

- Node : **HTTP Request** (ou **Slack** si vous avez configuré le credential).
- **Method** : `POST`.
- **URL** : votre webhook `https://hooks.slack.com/services/...`.
- **Body** (JSON) : `{ "text": "{{ $('AI Agent assemble').item.json.output }}" }`.

### 4.12 Sauvegarder & activer

`Save` → laisser **désactivé** pendant les tests, **Activate** quand la cron doit tourner réellement.

---

## Étape 5 — Tester (manuel puis planifié)

### 5.1 Run manuel (recommandé pour debug)

Bouton **Execute Workflow** (en bas du canvas) → suivre les nodes qui se colorent en vert / rouge en direct.

Cas à tester en priorité :
1. **Calendar vide** → `enrich_meetings` doit produire un tableau vide sans erreur.
2. **Inbox vide** → `classify_urgency` doit court-circuiter, `IF` route vers `extract_deadlines` directement.
3. **Mail urgent détecté** → vérifier que le draft apparaît dans Gmail (dossier *Drafts*) — **et nulle part ailleurs** (pas envoyé).
4. **Slack** → vérifier que le message est posté (sinon un node Slack/HTTP rouge).

### 5.2 Inspecter les traces

**Executions** (panneau de gauche) → cliquer la dernière exécution. Chaque node affiche **Input / Output** en JSON. C'est l'équivalent de `verbose=True` du notebook, mais visuel.

### 5.3 Activer la cron

Toggle **Active** en haut du canvas. n8n exécutera le workflow **lun-ven 8h30**. Pour vérifier immédiatement : modifier temporairement la cron en `*/5 * * * *` (toutes les 5 min), tester, puis remettre.

---

## Étape 6 — Garde-fous : idempotence & sandbox

### 6.1 Idempotence (le piège #1 en prod)

Le briefing tourne tous les jours → **risque de duplication** des drafts si la cron se déclenche 2× (panne, redémarrage, retry n8n).

**Solution simple** dans n8n : ajouter un node **Code** avant `draft_replies` qui vérifie si un draft du jour existe déjà :

```javascript
// Cherche un draft existant avec un marqueur date dans le subject
const today = new Date().toISOString().slice(0, 10);
const marker = `[briefing-${today}]`;
// Renvoyer le mail si pas encore traité aujourd'hui
const subj = $input.item.json.subject || "";
if (subj.includes(marker)) {
  return null;          // skip
}
return $input.item;
```

Et **inclure le marker dans le subject du draft** :
```
Re: {{ $json.subject }} [briefing-{{ $now.toISODate() }}]
```

### 6.2 Sandbox

Compte Google **dédié** au bootcamp. Si vous testez avec votre compte pro, vous risquez :
- de spammer vrai des collègues (un draft mal fait, un envoi accidentel),
- de polluer votre vraie boîte de drafts.

### 6.3 Quota & retries

n8n retry automatiquement les nodes Google sur erreur 429 (quota). À mentionner : le quota Gmail est de **250 unités/utilisateur/seconde** — non-bloquant ici (on fait < 20 appels par briefing).

### 6.4 Privacy

Désactiver la **télémétrie n8n** (`N8N_DIAGNOSTICS_ENABLED=false` dans `docker-compose.yml`). Ne pas activer LangSmith pour ce workflow si vous testez avec de vrais mails sensibles.

---

## Étape 7 — Comparaison Notebook 2 ↔ n8n

| Critère | Notebook 2 (Python) | n8n |
|---|---|---|
| Lignes de code écrites | ~ 600 lignes Python | **0** (config + 2-3 nodes Code) |
| Setup OAuth | `credentials.json` (Desktop) + `token.json` à gérer | UI **Sign in with Google** (Web client) |
| Cron 8h30 | papermill + cron Linux | **Schedule Trigger** natif |
| Connecteurs Gmail/Drive/Calendar | Bibliothèque `googleapiclient` | **Nodes natifs typés** (scopes pré-remplis) |
| Reflection loop | LangGraph `route_after_grade` + retry | IF + retry manuel (compteur dans Set node) |
| Idempotence | À coder (recherche par marker) | À configurer (node Code, mais explicite) |
| Observabilité | LangSmith (optionnel) | **Executions panel** (par défaut, riche) |
| Profil cible | Data Scientist / AI Dev | **Ops / IT / métier** |
| Évolution (ajout d'un outil) | écrire une fonction + Tool wrapper | **glisser un node** dans le canvas |
| Coût LLM | identique (Groq) | identique (Groq) |
| Coût infra | 0 (local) | 0 (local Docker) ou ~ 20 €/mois (n8n Cloud) |

**Question d'arbitrage** (à débattre) :
> *Pour un agent productivité destiné à 1-3 utilisateurs internes (DSI, dirigeants), lequel choisiriez-vous, et pourquoi ?*

Notre recommandation par défaut : **n8n** pour ce cas précis — la valeur n'est pas dans le code de l'agent, elle est dans le **scheduling fiable, l'OAuth simplifié et l'observabilité immédiate**. Le notebook reste meilleur pour **prototyper rapidement** des variations (changer le graph, ajouter un sub-graph, intégrer LangSmith fin) ou pour des cas où la logique métier est trop complexe pour 6-8 nodes.

---

## Annexes

### A. Mapping notebook → n8n

| Notebook (LangGraph node) | n8n (node ou groupe de nodes) |
|---|---|
| `n_fetch_calendar` | `Google Calendar` (Get Many) |
| `n_enrich_meetings` | `Split In Batches` + `Gmail` + `Drive` + `Merge` |
| `n_scan_inbox` | `Gmail` (Get Many, q=is:unread) |
| `n_classify_urgency` | `Loop Over Items` + `AI Agent` + Structured Output Parser |
| `n_draft_replies` | `IF` (urgent) + `AI Agent` + `Gmail` (Draft Create) |
| `n_extract_deadlines` | `Gmail` + `Code` (concat blob) + `AI Agent` |
| `n_assemble_briefing` | `Merge` + `AI Agent` |
| `n_grade_briefing` | `AI Agent` + Structured Output Parser + `IF` |
| `n_post_to_slack` | `HTTP Request` (webhook Slack) |

### B. Export / partage du workflow

**⋯ → Download** → fichier `morning-briefing.json`. Importable sur n'importe quelle instance n8n via **Workflows → Import from File**. ⚠️ Les credentials ne sont **jamais** exportés en clair — le destinataire doit les recréer.

### C. Dépannage

| Symptôme | Cause | Solution |
|---|---|---|
| `Sign in with Google` → "redirect_uri_mismatch" | URI mal copié dans GCP | Recopier exactement le redirect URL affiché par n8n (Étape 2.1) |
| AI Agent JSON invalide | Le LLM a ajouté du texte | Toujours brancher un **Structured Output Parser** sub-node |
| Schedule ne se déclenche pas | Workflow non *Active* | Toggle Activate **+** vérifier la timezone (`GENERIC_TIMEZONE` dans Compose) |
| Drafts en double tous les jours | Pas d'idempotence | Ajouter le Code node de l'étape 6.1 |
| Quota Calendar dépassé | Boucle sur `enrich_meetings` trop large | Limiter `Split In Batches` à `size: 1` + ajouter `Wait` node si > 100 events |

### D. Pour aller plus loin

- **Multi-utilisateur** : un workflow par utilisateur, ou un seul workflow avec **Switch** sur `userId` au début.
- **Notion / Linear** : ajouter un node Notion ou HTTP Request pour aller chercher les pages liées aux participants — extension naturelle de `enrich_meetings`.
- **Voice digest** : passer le markdown final dans **ElevenLabs TTS** → fichier audio dans Google Drive → lien dans Slack. ~ 3 nodes de plus.
- **Approval flow** : remplacer `Slack post` par `Slack interactive message` avec boutons *Envoyer / Modifier / Supprimer* sur chaque draft → on passe en **human-in-the-loop semi-automatisé**.

---

## Livrables attendus

1. ✅ Stack n8n active (mutualisée avec `tp4b-n8n-research-assistant.md`).
2. ✅ 4 credentials créées (Calendar, Gmail, Drive, Groq) + webhook Slack.
3. ✅ Workflow `Morning Briefing` exécutable manuellement avec succès.
4. ✅ Au moins un **draft Gmail** créé par une exécution test, **vérifié dans la boîte Drafts**.
5. ✅ Cron activée (peut être laissée off après le TP pour ne pas spammer).
6. ✅ Tableau comparatif **Notebook 2 ↔ n8n** rempli (Étape 7).
7. ✅ Export `morning-briefing.json`.

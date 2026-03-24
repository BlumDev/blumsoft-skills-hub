# Skills Consolidation And Archive Matrix

## Ziel

Das aktuelle Repo enthält 66 Skills. Für einen freiberuflichen selbständigen Softwareentwickler mit Fokus auf Webseiten, SaaS, Automatisierung und KI ist das zu breit als aktives Daily-Set.

Zielzustand:

- 6 aktive Kern-Skills plus 1 optionaler Bootstrap-Skill
- alte Spezial-Skills nicht sofort löschen
- Inhalte aus Spezial-Skills in Kern-Skills oder deren `references/` übernehmen
- alte Skill-Ordner danach als Archiv belassen, bis Migration abgeschlossen ist

## Warum reduzieren

- Bundles sind in diesem Repo nur Starter-Sets zum Syncen, keine Orchestrierung.
- Die eigentliche Skill-Auswahl passiert später über Skill-Beschreibungen, Trigger und den konkreten Request.
- Zu viele aktive Skills erhöhen Trigger-Überlappung, Pflegeaufwand und Kontextkosten.
- Zu große Monolithen wären aber ebenfalls falsch, weil Trigger dann zu unscharf werden.

## Empfohlene aktive Kern-Skills

### 1. `engineering-core`

Zweck:
- generische Delivery- und Qualitäts-Workflows

Quellen:
- brainstorming
- writing-plans
- systematic-debugging
- verification-before-completion
- requesting-code-review
- receiving-code-review
- test-driven-development
- using-git-worktrees
- finishing-a-development-branch

### 2. `web-product`

Zweck:
- Websites, SaaS-Frontend, UX, Conversion, Frontend-Qualität

Wichtig:
- `ui-ux-pro-max` bleibt hier ausdrücklich ein Kernbestandteil und darf nicht in ein rein optionales Archiv wegrationalisiert werden.

Quellen:
- webdev
- frontend-design
- ui-ux-pro-max
- webapp-testing
- nextjs-best-practices
- react-best-practices
- seo-audit
- ai-seo-auditor
- form-cro
- copywriting

### 3. `security-engineering`

Zweck:
- Secure Coding, Security Reviews, Web/App/API-Sicherheit

Quellen:
- code-review
- security-auditor
- api-security-best-practices
- backend-security-coder
- frontend-security-coder
- auth-implementation-patterns
- vulnerability-scanner
- top-web-vulnerabilities

### 4. `platform-devops`

Zweck:
- Backend, Deployments, Betrieb, Cloud, Observability

Quellen:
- backend
- docker-expert
- deployment-procedures
- terraform-specialist
- observability-engineer
- kubernetes-architect
- devops-troubleshooter
- distributed-tracing
- gitlab-ci-patterns
- incident-responder

### 5. `data-ai-systems`

Zweck:
- KI-Features, Agenten, RAG, Evaluierung, MCP, Knowledge Workflows

Quellen:
- prompt-engineer
- rag-engineer
- rag-implementation
- langgraph
- mcp-builder
- evaluation
- advanced-evaluation
- notebooklm
- context-optimization
- data-scientist

### 6. `business-growth`

Zweck:
- Produktstrategie, Pricing, Go-to-Market, Metriken, SEO/Growth

Quellen:
- product-manager-toolkit
- pricing-strategy
- launch-strategy
- analytics-tracking
- ab-test-setup
- competitive-landscape
- business-analyst

### 7. Optional: `project-bootstrap`

Zweck:
- neues Projekt oder neues Kundenrepo schnell in einen arbeitsfähigen Zustand bringen

Quellen:
- project-bootstrap
- project-development
- docu
- tool-design
- workflow-patterns
- executing-plans

## Bundle-Bewertung

Die Bundles sind nicht per se zu groß, aber die Profile sind zu breit.

Ist-Zustand:
- `web-wizard` core-only resolved zu 10 Skills, weil `essentials` via `compose_with` dazukommt
- `web-wizard` mit extended resolved zu 20 Skills
- `fullstack-founder` core-only resolved zu 34 Skills

Das Problem ist also weniger ein einzelnes Bundle, sondern die Summe mehrerer Bundles in einem Profil.

## Plan fuer `web-product`

Empfohlener interner Ablauf:

1. `webdev`
2. `ui-ux-pro-max`
3. `frontend-design`
4. `webapp-testing`
5. `seo-audit`

Entscheidungslogik:

- `webdev` immer ziehen, wenn Seiten, Landingpages, SaaS-Frontend oder Refactors gebaut werden.
- `ui-ux-pro-max` ziehen, wenn Layout, visuelle Qualität, Interaktion, Hierarchie oder Conversion wichtig sind.
- `frontend-design` ziehen, wenn neue UI-Komponenten oder eine markantere visuelle Richtung gebaut werden.
- `webapp-testing` ziehen, wenn ein UI-Change verifiziert werden muss oder Browser-Verhalten relevant ist.
- `seo-audit` nur ziehen, wenn öffentliche Seiten, Crawlability, Metadata, Structured Data oder Ranking-Relevanz betroffen sind.
- `ai-seo-auditor` nur ziehen, wenn AI-readiness, llms.txt, robots oder JSON-LD explizit relevant sind.
- `copywriting` und `form-cro` nur bei Marketing-, Funnel- oder Formular-Themen ziehen.

Wichtig:
- Ein Bundle entscheidet nicht aktiv, was ausgefuehrt wird.
- Das Bundle macht Skills nur verfuegbar.
- Der Agent entscheidet ueber Skill-Trigger in `description`, die Nutzeranfrage und seine allgemeinen Arbeitsregeln.

Deshalb sollte `web-product` kuenftig nicht als gleichgewichtige Liste gedacht werden, sondern als:

- Base: `engineering-core` + `web-product`
- Default intern: `webdev` + `ui-ux-pro-max`
- Optional on demand: `frontend-design`, `webapp-testing`, `seo-audit`, `ai-seo-auditor`, `copywriting`, `form-cro`

## Empfohlene neue kleine Bundles

### `freelancer-core`

- engineering-core
- web-product
- project-bootstrap

### `freelancer-ai`

- freelancer-core
- data-ai-systems

### `freelancer-platform`

- freelancer-core
- platform-devops

### `freelancer-fullstack`

- freelancer-core
- data-ai-systems
- security-engineering

Hinweis:
- `business-growth` nur bei echten GTM-/Content-/Pricing-Themen aktivieren
- `platform-devops` nur aktivieren, wenn Deployment, Infra oder Betrieb wirklich Teil des Auftrags sind

## Merge Matrix

Legende:

- `keep-active`: als eigener neuer Kern-Skill aktiv fuehren
- `merge-into`: Inhalt in neuen Kern-Skill ueberfuehren
- `archive-reference`: Alt-Skill nach Uebernahme nur noch als Referenz behalten
- `archive-drop`: nach sauberer Inhaltsuebernahme perspektivisch entfallen lassen

| Aktueller Skill | Ziel | Entscheidung | Hinweis |
|---|---|---|---|
| ab-test-setup | business-growth | merge-into | als Growth-Referenz |
| advanced-evaluation | data-ai-systems | merge-into | als Deep-Eval-Referenz |
| ai-seo-auditor | web-product | merge-into | nur on demand triggern |
| analytics-tracking | business-growth | merge-into | Metriken und Instrumentation |
| api-security-best-practices | security-engineering | merge-into | sehr gross, in references aufteilen |
| auth-implementation-patterns | security-engineering | merge-into | Auth-Patterns als Referenz |
| backend | platform-devops | merge-into | Backend plus Betrieb zusammenfuehren |
| backend-security-coder | security-engineering | merge-into | Secure backend coding |
| brainstorming | engineering-core | merge-into | fruehe Ideation und Scope |
| business-analyst | business-growth | merge-into | optionaler Referenzblock |
| code-review | security-engineering | merge-into | Security-first review beibehalten |
| competitive-landscape | business-growth | merge-into | nur bei Strategie-Auftraegen |
| context-optimization | data-ai-systems | merge-into | AI-systems optimization |
| copywriting | web-product | merge-into | im Web-/Conversion-Kontext halten |
| data-scientist | data-ai-systems | merge-into | Analyse/ML als Referenz |
| deployment-procedures | platform-devops | merge-into | Deployment-Workflow |
| devops-troubleshooter | platform-devops | merge-into | Incident- und Troubleshooting-Referenz |
| distributed-tracing | platform-devops | merge-into | Tracing als Referenz |
| docker-expert | platform-devops | merge-into | Build/Container-Referenz |
| docu | project-bootstrap | merge-into | Dokumentation im Bootstrap belassen |
| evaluation | data-ai-systems | merge-into | Basis-Evaluation |
| executing-plans | project-bootstrap | merge-into | Ausfuehrungsphase |
| finishing-a-development-branch | engineering-core | merge-into | Release-/Abschlussphase |
| form-cro | web-product | merge-into | Formoptimierung fuer Websites/SaaS |
| frontend-design | web-product | merge-into | aktiv behalten, aber unter einem Dach |
| frontend-security-coder | security-engineering | merge-into | Frontend secure coding |
| gitlab-ci-patterns | platform-devops | merge-into | CI/CD Referenz |
| incident-responder | platform-devops | merge-into | bei Freelancern eher Referenz |
| kubernetes-architect | platform-devops | merge-into | nur bei Plattform-Projekten |
| langgraph | data-ai-systems | merge-into | Agent-/Workflow-Baustein |
| launch-strategy | business-growth | merge-into | GTM-Referenz |
| mcp-builder | data-ai-systems | merge-into | aktiver Kern innerhalb AI |
| nextjs-best-practices | web-product | merge-into | Framework-spezifische Referenz |
| notebooklm | data-ai-systems | merge-into | Nischen-Referenz |
| observability-engineer | platform-devops | merge-into | produktionsnaher Kern |
| planning-with-files | engineering-core | merge-into | optionaler Planungsmodus |
| pricing-strategy | business-growth | merge-into | Growth/Commercial |
| product-manager-toolkit | business-growth | merge-into | Produktarbeit |
| project-bootstrap | project-bootstrap | keep-active | optionaler aktiver Skill |
| project-development | project-bootstrap | merge-into | Discovery/Architektur frueh |
| prompt-engineer | data-ai-systems | merge-into | aktiver Kern innerhalb AI |
| rag-engineer | data-ai-systems | merge-into | Retrieval-Patterns |
| rag-implementation | data-ai-systems | merge-into | Implementation-Details |
| react-best-practices | web-product | merge-into | Registry-Name behalten, Frontmatter angleichen |
| receiving-code-review | engineering-core | merge-into | Review-Einbau |
| requesting-code-review | engineering-core | merge-into | Review-Anforderung |
| security-auditor | security-engineering | merge-into | aktiver Kern |
| seo-audit | web-product | merge-into | public-web specific |
| subagent-driven-development | engineering-core | merge-into | nur wenn Subagents aktiv genutzt werden |
| systematic-debugging | engineering-core | merge-into | aktiver Kern |
| terraform-specialist | platform-devops | merge-into | IaC-Referenz |
| test-driven-development | engineering-core | merge-into | Qualitaets-Workflow |
| tool-design | project-bootstrap | merge-into | nur wenn Tool-/Agent-Design gefragt ist |
| top-web-vulnerabilities | security-engineering | merge-into | Registry-Name behalten, Frontmatter angleichen |
| ui-ux-pro-max | web-product | merge-into | sehr wichtig, prominent triggern |
| using-git-worktrees | engineering-core | merge-into | optionaler Workflow |
| verification-before-completion | engineering-core | merge-into | aktiver Kern |
| vulnerability-scanner | security-engineering | merge-into | Audit-/Threat-Referenz |
| webapp-testing | web-product | merge-into | Verifikation on demand |
| webdev | web-product | merge-into | aktiver Kern |
| workflow-automation | project-bootstrap | merge-into | fuer Automatisierungsvorhaben referenzieren |
| workflow-orchestration-patterns | project-bootstrap | merge-into | eher AI/Automation-Bootstrap |
| workflow-patterns | project-bootstrap | merge-into | Delivery-/Execution-Muster |
| writing-plans | engineering-core | merge-into | aktiver Kern |
| writing-skills | project-bootstrap | archive-reference | nur fuer Skill-Autoring separat archiviert lassen |

## Archivierungsplan

Phase 1:
- neue Kern-Skills anlegen
- alte Inhalte in `SKILL.md`, `references/`, `scripts/`, `assets/` uebernehmen

Phase 2:
- alte Spezial-Skills im Registry- und Bundle-Default nicht mehr aktiv listen
- Ordner unter `skills/archive/` verschieben oder vendor belassen und per Governance als archiviert markieren

Phase 3:
- nur die Kern-Skills in Standard-Profilen syncen
- Spezialwissen nur noch als Referenzen laden

## Repo-Hygiene vor der Umstellung

Diese zwei Namen angleichen:

- `react-best-practices` in der Registry passt nicht zur Frontmatter `vercel-react-best-practices`
- `top-web-vulnerabilities` in der Registry passt nicht zur Frontmatter `Top 100 Web Vulnerabilities Reference`

Und:

- `metadata:` in [skills/vendor/sickn33/top-web-vulnerabilities/SKILL.md](/D:/Repos/blumsoft-skills-hub/skills/vendor/sickn33/top-web-vulnerabilities/SKILL.md) entfernen oder bewusst standardisieren, wenn ihr strikt dem `skill-creator`-Modell folgen wollt

## Kurzfazit

Ja, die Skill-Landschaft sollte deutlich reduziert werden.

Die beste Reduktion ist:

- nicht 66 Spezialskills dauerhaft aktiv halten
- nicht alles in 2 oder 3 Monster-Skills kippen
- stattdessen 6 aktive Kern-Skills plus 1 optionalen Bootstrap-Skill definieren
- altes Spezialwissen kontrolliert archivieren

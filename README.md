# Search4eu Competition

## ToDo

- [ ] faire un point màj sur la stack Aleph (Memorious compris) ;
- [ ] configurer les crawlers pour DOCX et PDF ;
- [ ] entraîner l'indexation avec des listes d'entreprises ;
- [ ] expérimenter les extensions proposées (notamment le "fine graph", qui me paraît très très cool) ;
- [ ] lister les insuffisances manifestes du moteur de recherche compétition.

## Etat des lieux

### Cible

#### Structure générale

Les cas sont répartis suivants 3 policies :

1. antitrust / cartels ;
2. mergers ;
3. state aid.

Etrangement, le moteur de recherche propose une recherche antitrust / cartels et une recherche cartels qui semblent renvoyer les mêmes résultats pour cartels.

Le sommaire anti-chronologique des dernières décisions n'est pas disponible en lien direct : la page est générée de manière dynamique.

Par ailleurs : chaque page de sommaire est structurée d'une manière différente. La taxonomie des pages évolue par ailleurs périodiquement, engendrant des ruptures dans les séries de code.

La structure des URLs varie selon les policies avec pour base commune "https://ec.europa.eu/competition/elojade/isef/case_details.cfm?" :

| policy | policy_id | case_id | exemple |
| :--- | :---: | ---: | ---: |
| antistrust/cartel | proc_code=1 | _40632 | [40632 Mondelez trade restrictions](https://ec.europa.eu/competition/elojade/isef/case_details.cfm?proc_code=1_40632) |
| mergers | proc_code=2 | _M_10123 | [M.10123 PPG   / TIKKURILA](https://ec.europa.eu/competition/elojade/isef/case_details.cfm?proc_code=2_M_10123) |
| state aids | proc_code=3_SA | _59240 | [SA.59240 COVID-19 – Aid to airport operators](https://ec.europa.eu/competition/elojade/isef/case_details.cfm?proc_code=3_SA_59240) |
| stats aids (variante) | proc_code=3_C1 | _2006 | [C1/2006 Loan to Chupa Chups](https://ec.europa.eu/competition/elojade/isef/case_details.cfm?proc_code=3_C1_2006)

La nomenclature des URLs de cas de *"state aid"* s'avère cependant particulièrement instable (notamment avant 2018).

#### Insuffisances manifestes

Le moteur de recherche de la DG Competition comporte des faiblesses évidentes en terme de référencement :

- **indexation par bloc de texte et non par entité cohérente** : les entreprises

<https://ec.europa.eu/competition/elojade/isef/case_details.cfm?proc_code=1_40632>
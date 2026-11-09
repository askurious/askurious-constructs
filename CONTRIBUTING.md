# Beitragen / Contributing

[Deutsch](#deutsch) · [English](#english)

## Deutsch

Danke, dass du den Katalog erweitern willst. Ein Pull Request (PR) betrifft genau ein Konstrukt, also einen Ordner
unter `constructs/`.

### Ablauf

1. Repository forken, einen Branch anlegen.
2. Neues Konstrukt aus einer Vorlage: `python tools/new.py <vorlage> <key>` (`python tools/new.py --list` zeigt
   die Vorlagen). Der Key besteht aus Kleinbuchstaben, Ziffern und `_` und ändert sich danach nie.
3. `construct.yaml` ausfüllen: Name, Kurzbeschreibung, Beschreibung, Auswertung und Hinweise **auf Deutsch und
   Englisch**, Quelle mit DOI, Lizenz des Wortlauts (Schlüssel aus `schema/vocab/licences.yaml`), Schlagwörter
   aus `schema/vocab/facets.yaml`.
4. Wortlaut nur bei offener Lizenz (`distributable: true`) in `wording/<sprache>.yaml`, Items über ihre Codes.
   Bei lizenziertem Wortlaut kein `wording/`-Ordner, sondern je Sprache der Hash:
   `python tools/hash.py --wording <deine-datei>.yaml`. Die Datei mit dem Text bleibt bei dir.
5. Prüfen: `pip install -r requirements.txt`, dann `python tools/validate.py --base origin/main` und `pytest`.
6. Jeden Commit mit DCO-Sign-off: `git commit -s` (Zeile `Signed-off-by: Name <mail>`).
7. PR öffnen und die Fragen der Vorlage beantworten. Ralf Philipsen oder Philipp Brauner prüfen ihn (Code Owners).

### Änderungen an bestehenden Konstrukten

- Wortlaut korrigiert oder neue Sprache: Nebennummer erhöhen (`2.0` → `2.1`) und einen Eintrag oben in `versions`.
- Struktur geändert (Items, Stufen, Codes, Polung, Subskalen): Hauptnummer erhöhen (`2.1` → `3.0`).
- Zurückziehen: `status: retired` und `retired_since: <release>`. Löschen ist nicht erlaubt, weil bestehende
  Befragungen den Key tragen.

### Rechte

Mit dem PR bestätigst du, dass du jeden Wortlaut, den du einbringst, unter der angegebenen Lizenz weitergeben
darfst. Lizenzierten Wortlaut (z. B. GESIS/ZIS, Verlagsartikel) bitte nie einfügen, auch nicht in Kommentaren,
Issues oder PR-Texten. Eine eigene Beitragsvereinbarung (CLA) gibt es nicht; das DCO-Sign-off genügt
([Developer Certificate of Origin](https://developercertificate.org/)).

### Dein Name ist öffentlich

Wer hier beiträgt, steht mit Namen (und der Mailadresse des Commits) dauerhaft in der öffentlichen Git-Historie.
Nutze bei Bedarf die anonyme GitHub-Adresse (`<id>+<name>@users.noreply.github.com`). Lieber ohne Git? Dann das
Formular „Konstrukt vorschlagen“ unter Issues oder eine Mail.

### Kontakt

- Ralf Philipsen, philipsen@comm.rwth-aachen.de
- Philipp Brauner, brauner@comm.rwth-aachen.de

## English

Thank you for extending the catalogue. A pull request (PR) concerns exactly one construct, one folder under
`constructs/`.

### Steps

1. Fork the repository, create a branch.
2. New construct from a template: `python tools/new.py <template> <key>` (`python tools/new.py --list` lists them).
   The key takes small letters, digits and `_` and never changes afterwards.
3. Fill in `construct.yaml`: name, short description, description, scoring and notes **in German and English**,
   source with DOI, licence of the wording (key from `schema/vocab/licences.yaml`), tags from
   `schema/vocab/facets.yaml`.
4. Wording only with an open licence (`distributable: true`) in `wording/<language>.yaml`, items by their codes.
   With licensed wording no `wording/` folder, but the hash per language:
   `python tools/hash.py --wording <your-file>.yaml`. The file with the text stays with you.
5. Check: `pip install -r requirements.txt`, then `python tools/validate.py --base origin/main` and `pytest`.
6. Every commit with a DCO sign-off: `git commit -s` (line `Signed-off-by: Name <mail>`).
7. Open the PR and answer the questions of the template. Ralf Philipsen or Philipp Brauner review it (code owners).

### Changes to existing constructs

- Wording corrected or a new language: raise the minor number (`2.0` → `2.1`) and add an entry at the top of
  `versions`.
- Structure changed (items, points, codes, polarity, subscales): raise the major number (`2.1` → `3.0`).
- Withdraw: `status: retired` and `retired_since: <release>`. Deleting is not allowed, because existing surveys
  carry the key.

### Rights

With the PR you confirm that you may pass on every wording you contribute under the stated licence. Never add
licensed wording (e.g. GESIS/ZIS, journal articles), not even in comments, issues or PR texts. There is no
contributor licence agreement (CLA); the DCO sign-off is enough
([Developer Certificate of Origin](https://developercertificate.org/)).

### Your name is public

Contributors appear with their name (and the commit's mail address) permanently in the public Git history. Use
GitHub's no-reply address (`<id>+<name>@users.noreply.github.com`) if you prefer. Rather without Git? Use the form
"Konstrukt vorschlagen / Suggest a construct" under Issues, or send a mail.

### Contact

- Ralf Philipsen, philipsen@comm.rwth-aachen.de
- Philipp Brauner, brauner@comm.rwth-aachen.de

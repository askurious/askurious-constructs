# askurious-constructs

[Deutsch](#deutsch) · [English](#english)

## Deutsch

Der offene Katalog der Konstrukte von [Askurious](https://github.com/askurious/askurious): Skalen und
Standardfragen, die Forschende in ihre Befragungen einfügen. Jede Askurious-Instanz gleicht sich mit den Releases
dieses Repositorys ab.

### Was hier liegt

- `constructs/<key>/construct.yaml`: Metadaten (Deutsch und Englisch), Quellen, Lizenz, Schlagwörter und die
  Struktur im Askurious-Elementformat (Codes, Stufen, Subskalen, Umpolung). Der Key ist der, den eingefügte
  Elemente tragen; er ändert sich nie.
- `constructs/<key>/wording/<sprache>.yaml`: der Wortlaut, **nur wo die Lizenz die Weitergabe erlaubt** (eigene
  Konstrukte von Askurious und die RatSWD-Standardfragen, CC BY 4.0). Items und Antworten über ihre Codes.
- Lizenzierte Skalen (z. B. GESIS/ZIS, Verlagsartikel): nur das Gerüst und je Sprache ein SHA-256-Hash des
  Wortlauts. Den Wortlaut hält jede Instanz in ihrem privaten Overlay; Askurious fügt ein solches Konstrukt nur
  ein, wenn der Hash passt.
- `families/`: Kurz- und Langfassungen eines Instruments. `schema/`: JSON Schemas und Vokabulare (Facetten,
  Lizenzen, Sprachen). `examples/`: Vorlagen zum Kopieren. `tools/`: Prüfen, Hashen, Bauen.

### Versionen

Jedes Konstrukt hat die Version `HAUPT.NEBEN`: Ändert sich die Struktur (Items, Stufen, Codes, Polung), steigt
die Hauptnummer; ändert sich nur der Wortlaut, die Nebennummer. Die Prüfung im Pull Request erzwingt das. Ein
Konstrukt wird nie gelöscht, sondern mit `status: retired` zurückgezogen. Releases heißen `JJJJ.MM.N` und
liefern `manifest.json` mit Signatur (`manifest.json.sig`, minisign).

### Signatur prüfen

Der öffentliche Schlüssel liegt als `minisign.pub` im Wurzelordner dieses Repositorys (Schlüssel-ID
`8F880D565AD04DE6`); Askurious trägt denselben Schlüssel im Code. Prüfen:

```bash
minisign -V -p minisign.pub -m manifest.json -x manifest.json.sig
minisign -V -P RWTmTdBaVg2Ij3LgzDuGpbt4rr61X/xFBDIwGjVM/N1qXVfJUOMA3FMG -m manifest.json -x manifest.json.sig
```

Der geheime Schlüssel liegt nur als Secret des Repositorys (`MANIFEST_SIGNING_KEY`, Passwort in
`MANIFEST_SIGNING_PASSWORD`) und offline bei Ralf Philipsen.

### Nutzen

```bash
pip install -r requirements.txt
python tools/validate.py                 # alles prüfen
python tools/build.py --release 2026.11.0   # dist/manifest.json bauen
python tools/hash.py constructs/kamb     # Hashes eines Konstrukts
python tools/new.py likert-offen meinkey # neues Konstrukt aus einer Vorlage
```

### Beitragen

Neue Konstrukte, Übersetzungen und Korrekturen sind willkommen: als Pull Request (siehe
[CONTRIBUTING.md](CONTRIBUTING.md)), über das Formular „Konstrukt vorschlagen“ unter Issues oder per Mail an
Ralf Philipsen (philipsen@comm.rwth-aachen.de) oder Philipp Brauner (brauner@comm.rwth-aachen.de).

### Lizenzen

Nach [REUSE](https://reuse.software/), maschinenlesbar in `REUSE.toml`:

| Was | Lizenz |
|---|---|
| Metadaten, Struktur, Hashes, Schemas, Vokabulare, Beispiele, Dokumentation | CC0 1.0 |
| Wortlaut in `constructs/*/wording/` | CC BY 4.0 (Quelle in der `construct.yaml` daneben) |
| `tools/`, `tests/` | EUPL-1.2 |

Die Quellenangabe je Konstrukt bleibt Pflicht, wenn du es in einer Befragung einsetzt (`sources`, `notes`).
Lizenzierter Wortlaut liegt nicht in diesem Repository. Die Lizenzeinschätzungen sind keine Rechtsberatung.

## English

The open catalogue of the constructs of [Askurious](https://github.com/askurious/askurious): scales and standard
questions that researchers insert into their surveys. Every Askurious instance syncs with the releases of this
repository.

### What is here

- `constructs/<key>/construct.yaml`: metadata (German and English), sources, licence, tags and the structure in
  the Askurious element format (codes, points, subscales, reversed items). The key is the one inserted elements
  carry; it never changes.
- `constructs/<key>/wording/<language>.yaml`: the wording, **only where the licence allows passing it on**
  (Askurious' own constructs and the RatSWD standard questions, CC BY 4.0). Items and answers by their codes.
- Licensed scales (e.g. GESIS/ZIS, journal articles): only the frame and per language a SHA-256 hash of the
  wording. Each instance keeps the wording in its private overlay; Askurious inserts such a construct only when the
  hash matches.
- `families/`: short and long versions of one instrument. `schema/`: JSON Schemas and vocabularies (facets,
  licences, languages). `examples/`: templates to copy. `tools/`: check, hash, build.

### Versions

Each construct has the version `MAJOR.MINOR`: when the structure changes (items, points, codes, polarity), the
major number goes up; when only the wording changes, the minor number. The pull request check enforces this. A
construct is never deleted but withdrawn with `status: retired`. Releases are named `YYYY.MM.N` and ship
`manifest.json` with a signature (`manifest.json.sig`, minisign).

### Checking the signature

The public key is `minisign.pub` in the root folder of this repository (key ID `8F880D565AD04DE6`); Askurious
carries the same key in its code. Check:

```bash
minisign -V -p minisign.pub -m manifest.json -x manifest.json.sig
minisign -V -P RWTmTdBaVg2Ij3LgzDuGpbt4rr61X/xFBDIwGjVM/N1qXVfJUOMA3FMG -m manifest.json -x manifest.json.sig
```

The secret key exists only as a secret of the repository (`MANIFEST_SIGNING_KEY`, password in
`MANIFEST_SIGNING_PASSWORD`) and offline with Ralf Philipsen.

### Use

```bash
pip install -r requirements.txt
python tools/validate.py                    # check everything
python tools/build.py --release 2026.11.0   # build dist/manifest.json
python tools/hash.py constructs/kamb        # hashes of a construct
python tools/new.py likert-offen mykey      # new construct from a template
```

### Contributing

New constructs, translations and corrections are welcome: as a pull request (see
[CONTRIBUTING.md](CONTRIBUTING.md)), through the form "Konstrukt vorschlagen / Suggest a construct" under Issues,
or by mail to Ralf Philipsen (philipsen@comm.rwth-aachen.de) or Philipp Brauner (brauner@comm.rwth-aachen.de).

### Licences

Following [REUSE](https://reuse.software/), machine-readable in `REUSE.toml`:

| What | Licence |
|---|---|
| Metadata, structure, hashes, schemas, vocabularies, examples, documentation | CC0 1.0 |
| Wording in `constructs/*/wording/` | CC BY 4.0 (source in the `construct.yaml` next to it) |
| `tools/`, `tests/` | EUPL-1.2 |

Citing the source of each construct remains required when you use it in a survey (`sources`, `notes`). Licensed
wording is not in this repository. The licence assessments are not legal advice.

# Familien / Families

Eine Familie verbindet Kurz- und Langfassungen desselben Instruments (z. B. BFI-10 und BFI-2-S). Askurious zeigt
auf jeder Karte die anderen Fassungen und vergleicht sie nebeneinander. Bisher setzen Admins die Familien je
Instanz; ab dem Katalog stehen sie hier, eine Datei je Familie. Noch ist keine Familie eingetragen.

A family links short and long versions of the same instrument (e.g. BFI-10 and BFI-2-S). Askurious shows the other
versions on each card and compares them side by side. So far admins set families per instance; with the catalogue
they live here, one file per family. No family is recorded yet.

Format (`schema/family.schema.json`), Datei / file `families/big-five.yaml`:

```yaml
id: big-five                    # = Dateiname / file name
name: {de: Big Five, en: Big Five}
members:
  - key: bfi10
    label: {de: "BFI-10, 10 Items", en: "BFI-10, 10 items"}
  - key: bfi2s
    label: {de: "BFI-2-S, 30 Items", en: "BFI-2-S, 30 items"}
```

Jedes Mitglied nennt in seiner `construct.yaml` die Familie: `family: big-five`.
Each member names the family in its `construct.yaml`: `family: big-five`.

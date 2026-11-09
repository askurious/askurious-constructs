# Security / Sicherheit

## Reporting a vulnerability

Please report security issues privately, not in public issues or pull requests: through GitHub's "Report a
vulnerability" button on the Security tab of this repository, or by mail to Ralf Philipsen
(philipsen@comm.rwth-aachen.de) or Philipp Brauner (brauner@comm.rwth-aachen.de). Describe what you found, how to
reproduce it and which release or commit you looked at.

We confirm receipt within a few working days, keep you informed, and name you in the release notes if you wish.
Please give us reasonable time to fix the issue before you make it public.

## Scope

- The release signature: a manifest that verifies against `minisign.pub` but was not built by the release workflow,
  or any sign that the signing key is exposed.
- The tools in `tools/` and the workflows in `.github/workflows/`.
- Licensed wording that ended up in this repository (it must never be here; see CONTRIBUTING.md). Report it the
  same private way, so we can remove it before it spreads.

The code of Askurious itself is in [askurious/askurious](https://github.com/askurious/askurious), with its own
security policy. For a problem with a particular installation (for example askurious.de), use the contact in that
installation's legal notice ("Impressum").

## Supported versions

Only the latest release and the main branch receive fixes.

## Deutsch, kurz

Sicherheitslücken bitte vertraulich melden: über „Report a vulnerability“ im Reiter Security oder per Mail an
Ralf Philipsen oder Philipp Brauner, nicht in öffentlichen Issues. Dazu zählen Probleme mit der Signatur der
Releases, mit den Werkzeugen und Workflows sowie lizenzierter Wortlaut, der versehentlich ins Repository geraten ist.

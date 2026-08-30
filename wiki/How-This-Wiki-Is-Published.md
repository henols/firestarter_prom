# How This Wiki Is Published

This page describes the mechanics behind this wiki, not the Firestarter project itself. If you are looking for reference documentation on chips, protocols, or hardware, start from [Home](Home) instead.

## The in-repo copy is authoritative

Every page on this wiki is authored as a markdown file inside the `firestarter_prom` repository, under a top-level `wiki` directory. That in-repo copy is the single source of truth for everything published here. The wiki you are reading is a mirror of that directory, not an independent copy of it.

## Edits made here are overwritten

Do not edit pages directly through this web interface. An edit made here is overwritten the next time the wiki is published, because publishing replaces the wiki's content with a fresh copy of the source directory rather than merging changes into it. If you want to fix or add something, change the corresponding file under `wiki/` in the `firestarter_prom` repository and open a pull request there. Your change reaches this wiki the next time it is published.

## Publishing

Publishing is done with a small command-line tool that lives in the repository, `tools/wiki/wiki.py`.

- `python3 tools/wiki/wiki.py publish` computes what would change and prints it, without writing anything. This is the safe way to preview a publish or to confirm the wiki matches the source.
- `python3 tools/wiki/wiki.py publish --push` performs the publish: it replaces the wiki's content with the current source directory and pushes the result.

## How page names are derived

A wiki page's name comes directly from its filename, with no separate list to keep in step. A file named `Shield-Revisions.md` becomes the page "Shield Revisions", reachable at the URL path `/wiki/Shield-Revisions`. Hyphens in the filename render as spaces in the page title, which is why a page title can never contain a literal hyphen — a hyphen in a name is always read as a word separator.

## Linking between pages

The only link form recognized between pages on this wiki is a plain markdown link with no file extension, for example:

```
[Link text](Page-Name)
```

A link that ends in `.md`, a double-bracketed link such as `[[Page Name]]`, or a reference-style link such as `[text][ref]` will fail this wiki's publishing check and will not be accepted. Link by the exact page name, with the correct case.

## The sidebar is generated, not written by hand

The page listing every page on this wiki is generated automatically by `python3 tools/wiki/wiki.py sidebar`, from the current set of pages in the source directory. Do not hand-edit it — a manual change is overwritten the next time it is regenerated, and there is no way to tell a hand edit apart from the real thing until it silently drifts out of date.

## Which branch this wiki tracks

This wiki is published from the project's `beta` integration branch, not from a tagged release. Content here can describe behavior that has not yet reached a stable release.

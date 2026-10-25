# Secret Santa - North Pole Post

A static site: enter a secret Christmas name, see a letter addressed to your real name, tap the wax seal to find out who you are buying for. No build step and no external requests. It can even be opened by double-clicking `index.html`.

## Files

- `data/secrets.js` - real name and secret name. Safe to open; use it to send each person their secret name privately.
- `data/assignments.js` - who buys for whom. **Spoiler. Don't open it if you want to be surprised.**
- `scripts/generate_draw.py` - creates `assignments.js` (Python 3, standard library only). Refuses to overwrite an existing draw unless run with `--redraw`.

## Preview locally

Open `index.html` directly, or run `py -m http.server 8000` and visit http://localhost:8000 (needed to test on a phone via your PC's address).

## Tests

```
py -m unittest discover -s tests
```

Checks the draw (everyone gives and receives once, nobody draws themselves) without printing any pairings.

## Publish on GitHub Pages

Push this folder to a repository, then Settings > Pages > Deploy from a branch > `main` / root. All paths are relative, so the project sub-path works.

## Caveat

The data files are plain text in a public repository. The site hides assignments from casual visitors, but anyone who opens the files can read them. Secret names are not passwords.

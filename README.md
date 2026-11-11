# Warm Paper & Warm Night

Warm light and dark VS Code themes: paper and ink backgrounds with a terracotta accent.

## Colour blindness

Code uses five hues (keywords, strings, functions, types, constants) plus Ink for names and Muted for comments and
punctuation. Parameters and properties are told apart by italics, not by another colour. Every pair of colours
shown together (syntax, git status, errors and warnings, bracket pairs) stays at least 10 apart in CIEDE2000 with
normal vision, protanopia, deuteranopia and tritanopia, and code text keeps a 4.5:1 contrast on the background.
The tests check both.

## Install

```sh
git clone https://github.com/Pierre-Monier/vscode-theme.git
ln -s "$PWD/vscode-theme" ~/.vscode/extensions/pierremonier.warm-theme-1.0.0
```

Then restart VS Code and let the themes follow macOS light/dark mode with these user settings:

```json
"window.autoDetectColorScheme": true,
"workbench.preferredLightColorTheme": "Warm Paper",
"workbench.preferredDarkColorTheme": "Warm Night"
```

## Change a colour

Edit `build_themes.py`, then run it to rewrite `themes/*.json`:

```sh
python3 build_themes.py
```

## Tests

```sh
python3 -m unittest discover -s tests
```

They check that the theme files match the generator and follow the colour blindness rules above.

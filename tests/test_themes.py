# ABOUTME: Checks the theme files match their generator and stay readable with colour blindness.
# ABOUTME: Run with `python3 -m unittest discover -s tests`.
import itertools
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build_themes  # noqa: E402
import colour_vision  # noqa: E402


class VSCodeThemeTest(unittest.TestCase):
    def test_theme_files_match_generator(self):
        for mode in build_themes.PALETTES:
            path, theme = build_themes.build(mode)
            self.assertEqual(json.loads(path.read_text()), theme, f"{path.name} is stale: run build_themes.py")

    def test_manifest_lists_both_themes(self):
        manifest = json.loads((ROOT / "package.json").read_text())
        themes = {t["path"]: t["uiTheme"] for t in manifest["contributes"]["themes"]}
        self.assertEqual(themes, {"./themes/warm-paper.json": "vs", "./themes/warm-night.json": "vs-dark"})


def syntax_colours(theme):
    """Text colours of code, without the diff and invalid-code rules which only appear on their own."""
    return {
        rule["settings"]["foreground"]
        for rule in theme["tokenColors"]
        if rule["name"] != "Invalid" and not rule["name"].startswith("Diff")
    }


def colour_groups(theme):
    """Colours that appear side by side, so each must be told apart from the others in its group."""
    colours = theme["colors"]
    return {
        "syntax": syntax_colours(theme),
        "git": {colours[f"gitDecoration.{k}ResourceForeground"] for k in ("added", "modified", "deleted")},
        "diagnostics": {colours[f"editor{k}.foreground"] for k in ("Error", "Warning", "Info")},
        "brackets": {colours[f"editorBracketHighlight.foreground{i}"] for i in range(1, 7)},
    }


class ColourBlindnessTest(unittest.TestCase):
    MINIMUM_DIFFERENCE = 10  # CIEDE2000: clearly different at a glance, even in small text
    MINIMUM_CONTRAST = 4.5  # WCAG AA for body text

    def test_colours_stay_distinct_with_colour_blindness(self):
        for mode in build_themes.PALETTES:
            theme = build_themes.build(mode)[1]
            for group, colours in colour_groups(theme).items():
                for simulation in colour_vision.SIMULATIONS:
                    for colour1, colour2 in itertools.combinations(sorted(colours), 2):
                        with self.subTest(mode=mode, group=group, simulation=simulation, pair=(colour1, colour2)):
                            self.assertGreaterEqual(
                                colour_vision.difference(colour1, colour2, simulation), self.MINIMUM_DIFFERENCE)

    def test_groups_keep_one_colour_per_role(self):
        for mode in build_themes.PALETTES:
            groups = colour_groups(build_themes.build(mode)[1])
            self.assertEqual({name: len(colours) for name, colours in groups.items()},
                             {"syntax": 7, "git": 3, "diagnostics": 3, "brackets": 6}, mode)

    def test_code_is_readable_on_the_background(self):
        for mode in build_themes.PALETTES:
            theme = build_themes.build(mode)[1]
            background = theme["colors"]["editor.background"]
            for colour in syntax_colours(theme):
                with self.subTest(mode=mode, colour=colour):
                    self.assertGreaterEqual(colour_vision.contrast(colour, background), self.MINIMUM_CONTRAST)


if __name__ == "__main__":
    unittest.main()

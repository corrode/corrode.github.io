#!/usr/bin/env python3
"""Generate social preview images with the site's bundled fonts.

Requires Python 3.11+, ImageMagick (magick), woff2_decompress, and fonttools.
Run without arguments to generate missing cards, or with --force to rebuild all.
"""

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
import tomllib
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
# Keep in sync with sass/_variables.scss.
BG = "#fab71c"
INK = "#1a1c26"
RED = "#ee3856"
MUTED = "#8a691f"


def run(*args):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True)


def magick(*args):
    run("magick", *args)


def dimensions(image):
    result = subprocess.check_output(
        ["magick", "identify", "-format", "%w %h", str(image)], text=True
    )
    return tuple(map(int, result.split()))


def label(output, text, font, size, color=INK, kerning=None, width=None):
    args = ["-background", "none", "-fill", color, "-font", font, "-pointsize", size]
    if kerning is not None:
        args.extend(["-kerning", kerning])
    if width is not None:
        args.extend(["-size", f"{width}x", f"caption:{text}"])
    else:
        args.append(f"label:{text}")
    magick(*args, output)


def composite(canvas, layers, output=None):
    args = [canvas]
    for image, x, y, gravity in layers:
        args.extend([image, "-gravity", gravity, "-geometry", f"+{x}+{y}", "-composite"])
    magick(*args, output or canvas)


def prepare_svg(source, output, width, height, remove_text=False):
    # Explicit viewports keep small viewBox-only partner logos sharp.
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    root = ET.fromstring(source.read_text().replace("#ffc61a", BG))
    root.set("width", str(width))
    root.set("height", str(height))
    if remove_text:
        # Draw text with bundled fonts rather than relying on SVG font lookup.
        for child in list(root):
            if child.tag == "{http://www.w3.org/2000/svg}text":
                root.remove(child)
    ET.ElementTree(root).write(output)


class Generator:
    def __init__(self, tmp, force):
        self.tmp = tmp
        self.force = force
        self.fonts = {}

    def font(self, name):
        if name not in self.fonts:
            source = "InterVariable" if name == "Inter-Bold" else name
            woff = self.tmp / f"{source}.woff2"
            shutil.copyfile(ROOT / "static/fonts" / woff.name, woff)
            run("woff2_decompress", woff)
            ttf = self.tmp / f"{name}.ttf"
            if name == "Inter-Bold":
                run("fonttools", "varLib.instancer", woff.with_suffix(".ttf"),
                    "wght=700", "-o", ttf)
            self.fonts[name] = ttf
        return self.fonts[name]

    def needed(self, output):
        return self.force or not output.exists()

    def standalone(self):
        canvas = self.tmp / "standalone.png"
        layer = self.tmp / "layer.png"
        svg = self.tmp / "standalone.svg"

        def text(value, font, size, x, y, color=INK, gravity="northwest"):
            label(layer, value, self.font(font), size, color)
            composite(canvas, [(layer, x, y, gravity)])

        for path in ("static/social/default.png", "static/social/podcast.png",
                     "static/codecrafters/social.png", "static/svix/social.png"):
            output = ROOT / path
            if not self.needed(output):
                continue
            if path == "static/social/default.png":
                magick("-background", BG, ROOT / "static/social/default-template.svg", canvas)
                for value, y in zip(("Friendly,", "professional", "Rust", "Consulting"),
                                    (85, 190, 295, 400)):
                    text(value, "Inter-Bold", 76, 80, y)
            elif path == "static/social/podcast.png":
                prepare_svg(ROOT / "static/social/raw/podcast.svg", svg, 1200, 630, True)
                magick("-background", BG, svg, canvas)
                text("RUST IN", "BebasNeue-Bold", 123, 367, 152)
                text("PRODUCTION", "BebasNeue-Bold", 123, 367, 262, RED)
            else:
                partner = output.parent.name
                magick("-size", "1200x630", f"xc:{BG}", canvas)
                if partner == "codecrafters":
                    prepare_svg(ROOT / "static/codecrafters/logo.svg", svg, 260, 185)
                    magick("-background", "none", "-density", 144, svg, "-resize", "260x185", layer)
                    composite(canvas, [(layer, 0, 80, "north")])
                    text("CodeCrafters", "Inter-Bold", 60, 0, 295, gravity="north")
                    tagline = "Learn Rust by building real systems"
                else:
                    prepare_svg(ROOT / "static/svix/svix-brand.svg", svg, 440, 200)
                    magick("-background", "none", "-density", 144, svg, "-resize", "440x200", layer)
                    composite(canvas, [(layer, 0, 145, "north")])
                    tagline = "Webhooks your customers can rely on"
                text(tagline, "Inter-Bold", 40, 0, 395, gravity="north")
                magick(canvas, "-fill", RED, "-draw", "rectangle 540,476 660,483", canvas)
                text(f"corrode.dev/{partner}", "JetBrainsMono-Regular", 25, 0, 566,
                     "#685020", "north")
            magick(canvas, "-strip", "-depth", 8, output)
            print(f"Generated {path}")

    def episode(self, output, metadata):
        title = metadata["title"]
        extra = metadata.get("extra", {})
        guest, role = extra["guest"], extra.get("role", "")
        bebas, mono = self.font("BebasNeue-Bold"), self.font("JetBrainsMono-Regular")
        with tempfile.TemporaryDirectory(dir=self.tmp) as directory:
            tmp = Path(directory)
            bg, kicker, accent = (tmp / f"{name}.png" for name in ("bg", "kicker", "accent"))
            title_img, byline, badge, meta = (tmp / f"{name}.png" for name in
                                            ("title", "byline", "badge", "meta"))
            magick("-background", BG, "-density", 200,
                   ROOT / "static/social/podcast-episode.svg", "-resize", "1200x630", bg)
            logo_file = output.parent / "logo.svg"
            logo = None
            if logo_file.exists():
                logo = tmp / "logo.png"
                magick("-background", "none", "-density", 300, logo_file,
                       "-resize", "200x200", "-fill", INK, "-colorize", 100,
                       "-background", "none", "-gravity", "center", "-extent", "200x200", logo)
            label(kicker, "RUST IN PRODUCTION", bebas, 60, kerning=5)
            magick("-size", f"{dimensions(kicker)[0]}x12", f"xc:{RED}", accent)
            title_pt = 88 if len(title) > 24 else 112 if len(title) > 18 else 120 if len(title) > 12 else 130
            label(title_img, title.upper(), bebas, title_pt, kerning=2, width=1040)
            length = len(guest) + len(role) + 2 if role else len(guest)
            byline_pt = 40 if length > 50 else 48 if length > 42 else 56 if length > 36 else 64 if length > 30 else 72
            if role:
                parts = [tmp / f"{name}.png" for name in ("guest", "sep", "role")]
                for part, value, color in zip(parts, (guest.upper(), ", ", role.upper()), (INK, INK, MUTED)):
                    label(part, value, bebas, byline_pt, color, kerning=2)
                magick(*parts, "+append", byline)
            else:
                label(byline, guest.upper(), bebas, byline_pt, kerning=2)
            role_line = None
            if dimensions(byline)[0] > 1040 and role:
                role_line = tmp / "role-line.png"
                label(byline, guest.upper(), bebas, 54, kerning=1)
                label(role_line, role.upper(), bebas, 40, MUTED, kerning=1)
            if dimensions(byline)[0] > 1040:
                magick(byline, "-resize", "1040x", byline)
            badge_text = tmp / "badge-text.png"
            label(badge_text, f"S{extra.get('season', '')} E{extra.get('episode', '')}", mono, 30)
            width, height = dimensions(badge_text)
            width, height = width + 36, height + 20
            magick("-size", f"{width}x{height}", f"xc:{BG}", "-fill", "none",
                   "-stroke", INK, "-strokewidth", 2, "-draw",
                   f"roundrectangle 1,1 {width-2},{height-2} 6,6",
                   badge_text, "-gravity", "Center", "-composite", badge)
            label(meta, f"Published on {metadata.get('date', '')}", mono, 30, MUTED)
            byline_y = 240 + dimensions(title_img)[1]
            meta_y = byline_y + (140 if role_line else 100)
            canvas = tmp / "composed.png"
            if logo:
                composite(bg, [(logo, 60, 60, "NorthEast")], canvas)
            else:
                shutil.copyfile(bg, canvas)
            composite(canvas, [(kicker, 80, 70, "NorthWest"),
                               (accent, 80, 138, "NorthWest"),
                               (title_img, 80, 200, "NorthWest"),
                               (byline, 80, byline_y, "NorthWest")])
            if role_line:
                composite(canvas, [(role_line, 80, byline_y + 55, "NorthWest")])
            composite(canvas, [(badge, 80, meta_y, "NorthWest"),
                               (meta, 104 + dimensions(badge)[0], meta_y + 10, "NorthWest")], output)

    def post(self, post):
        metadata = frontmatter(post)
        title = metadata.get("title")
        output = post.parent / "social.png"
        if not title or not self.needed(output):
            return
        if "podcast" in post.relative_to(ROOT / "content").parts:
            if metadata.get("extra", {}).get("guest"):
                self.episode(output, metadata)
            else:
                shutil.copyfile(ROOT / "static/social/podcast.png", output)
        else:
            text = self.tmp / "caption.png"
            label(text, title, self.font("Inter-Bold"), 80, "#000000", width=670)
            composite(ROOT / "static/social/default-template.svg",
                      [(text, 80, 80, "northwest")], output)
        print(f"Generated {output.relative_to(ROOT)}")


def frontmatter(post):
    lines = post.read_text().splitlines()
    if not lines or lines[0] != "+++":
        raise ValueError(f"Missing TOML frontmatter: {post}")
    try:
        end = lines.index("+++", 1)
        return tomllib.loads("\n".join(lines[1:end]))
    except (ValueError, tomllib.TOMLDecodeError) as error:
        raise ValueError(f"Invalid frontmatter in {post}: {error}") from error


def posts(directory):
    for name in ("_index.md", "index.md"):
        path = directory / name
        if path.is_file():
            yield path
    for path in sorted(directory.iterdir()):
        if path.is_dir() and not path.name.startswith(("_", ".")) and path.name != "target":
            yield from posts(path)
    for path in sorted(directory.glob("*.md")):
        if not path.name.startswith("_") and path.name != "index.md":
            yield path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-f", "--force", action="store_true", help="overwrite existing images")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="social-") as directory:
        generator = Generator(Path(directory), args.force)
        # Generic podcast pages copy the standalone card.
        generator.standalone()
        for path in sorted((ROOT / "content").iterdir()):
            if path.is_dir() and not path.name.startswith(("_", ".")) and path.name != "target":
                for post in posts(path):
                    generator.post(post)


if __name__ == "__main__":
    main()

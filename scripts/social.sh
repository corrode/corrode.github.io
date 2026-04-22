#!/bin/bash
#
# Generate social preview images for the site.
#
# Usage:
#   scripts/social.sh           # Generate any missing social images
#   scripts/social.sh --force   # Regenerate all social images (overwrites)
#
set -euo pipefail

FORCE=0
for arg in "$@"; do
    case "$arg" in
        -f|--force) FORCE=1 ;;
        -h|--help)
            sed -n '2,8p' "$0"
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg" >&2
            echo "Run '$0 --help' for usage." >&2
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Color palette — kept in sync with sass/_variables.scss so the generated
# social images visually match the website's landing pages.
# ---------------------------------------------------------------------------
PODCAST_BG='#fab71c'        # $brightBgrd
PODCAST_ACCENT='#ee3856'    # $brightScnd
PODCAST_TEXT='#1a1c26'      # $darkBgrd
PODCAST_MUTED='#8a691f'     # $darkBgrd at 50% opacity blended over $brightBgrd (matches .episode-byline-role { opacity: 0.5 })
PODCAST_BADGE_BORDER='#1a1c26'

# Function to generate social image for a given title (blog posts etc.)
generate_social_image() {
    local template_file=$1
    local output_file="$2"

    # Title can be unbound
    local title=${3:-}

    echo "Generating social image with title >$title< at $output_file"

    if [[ -z "$title" ]]; then
        # No caption; copy the template file as is
        cp "$template_file" "$output_file"
    else
        # Generate the caption image
        magick -background none -fill '#000000' -font Inter-Bold -pointsize 80 -size 670x caption:"$title" text.png

        # Composite the caption over the background image
        magick "$template_file" text.png -gravity northwest -geometry +80+80 -composite "$output_file"
    fi
}

# Function to generate a per-episode podcast social image.
#
# Builds a 1200x630 image from scratch, in the same dark-navy style as the
# podcast landing page:
#
#   PODCAST                  <- small caps, red underline accent
#   ────
#   COMPANY NAME             <- big bold title (Bebas Neue, like the site)
#   GUEST NAME, ROLE         <- byline, role muted
#   [S0X E0X]  Published on YYYY-MM-DD   <- mono badge + meta line
#
generate_podcast_social_image() {
    local output_file=$1
    local title=$2
    local guest=$3
    local role=$4
    local season=$5
    local episode_num=$6
    local date=$7
    local logo_file=${8:-}

    local episode_label="S${season} E${episode_num}"
    local byline="${guest}"
    if [[ -n "$role" ]]; then
        byline="${guest}, ${role}"
    fi

    echo "Generating podcast episode social image: ${episode_label} – ${title} (with ${guest}) → ${output_file}"

    local tmp_dir
    tmp_dir=$(mktemp -d)
    local bg="$tmp_dir/bg.png"
    local kicker="$tmp_dir/kicker.png"
    local accent="$tmp_dir/accent.png"
    local title_img="$tmp_dir/title.png"
    local byline_img="$tmp_dir/byline.png"
    local badge="$tmp_dir/badge.png"
    local meta="$tmp_dir/meta.png"

    # ---- Background ------------------------------------------------------
    # Use the dot-grid SVG template so the per-episode images share the
    # same texture as the show's main social card.
    magick -background "$PODCAST_BG" -density 200 \
        static/social/podcast-episode.svg \
        -resize 1200x630 "$bg"

    # ---- Company logo (top-right) ---------------------------------------
    # Render the per-episode logo as a flat dark silhouette so logos look
    # consistent across episodes regardless of their original colors.
    # Mirrors `filter: grayscale(1)` used on .podcast-logo-img on the site.
    local logo_img=""
    if [[ -n "$logo_file" && -f "$logo_file" ]]; then
        logo_img="$tmp_dir/logo.png"
        # Render the SVG at high density on the yellow background, then
        # extract a dark-on-transparent silhouette via -colorspace gray +
        # threshold/level. Hardcoded fills and gradients all collapse to
        # the same flat shape.
        #
        # Logos vary wildly in aspect ratio (square icons, wide wordmarks,
        # tall glyphs). To keep them visually consistent on the canvas we
        # fit each silhouette inside a fixed 200x200 square box, preserving
        # aspect ratio (`-resize 200x200` without `!`) and then padding
        # transparent pixels around it with `-extent`.
        local logo_box=200
        magick -background "$PODCAST_BG" -density 300 "$logo_file" \
            -resize "${logo_box}x${logo_box}" \
            -colorspace gray -level 0%,80% \
            -alpha off \
            \( +clone -threshold 60% -negate \) \
            -alpha off -compose copy_opacity -composite \
            -fill "$PODCAST_TEXT" -colorize 100 \
            -background none -gravity center \
            -extent "${logo_box}x${logo_box}" \
            "$logo_img"
    fi

    # ---- "RUST IN PRODUCTION" kicker -------------------------------------
    # Dark Bebas Neue on yellow, with a thick red underline bar beneath to
    # mirror the red highlight used on the site's section headings.
    magick -background none -fill "$PODCAST_TEXT" \
        -font "Bebas-Neue-Regular" -pointsize 60 -kerning 5 \
        label:"RUST IN PRODUCTION" "$kicker"

    # Thicker red accent bar that sits directly under the kicker.
    local kicker_w
    kicker_w=$(magick identify -format "%w" "$kicker")
    magick -size "${kicker_w}x12" "xc:${PODCAST_ACCENT}" "$accent"

    # ---- Title (company / episode name) ----------------------------------
    # Bebas Neue, big — this matches the .episode-byline / hero typography.
    # Adaptive size so longer titles still fit inside the safe area
    # (left margin 80, right margin 80 → max content width 1040).
    local title_len=${#title}
    local title_pt=130
    if [[ $title_len -gt 17 ]]; then
        title_pt=88
    elif [[ $title_len -gt 12 ]]; then
        title_pt=104
    elif [[ $title_len -gt 8 ]]; then
        title_pt=120
    fi

    local title_uc
    title_uc=$(printf '%s' "$title" | tr '[:lower:]' '[:upper:]')

    magick \
        -background none \
        -fill "$PODCAST_TEXT" \
        -font "Bebas-Neue-Regular" \
        -pointsize "$title_pt" \
        -kerning 2 \
        -size 1040x \
        caption:"${title_uc}" \
        "$title_img"

    # ---- Byline (guest, role) -------------------------------------------
    # Build via two label: passes appended horizontally so we can color
    # the role differently from the name (matches .episode-byline-role).
    local guest_uc role_uc
    guest_uc=$(printf '%s' "$guest" | tr '[:lower:]' '[:upper:]')
    role_uc=$(printf '%s' "$role" | tr '[:lower:]' '[:upper:]')

    # Adaptive byline pointsize so long "name, role" combos still fit inside
    # the 1040px safe area. Bebas Neue is condensed; ~0.32× pointsize per
    # character is a reasonable upper bound including the ", " separator.
    local byline_len=${#guest}
    if [[ -n "$role" ]]; then
        byline_len=$(( ${#guest} + ${#role} + 2 ))
    fi
    local byline_pt=72
    if   [[ $byline_len -gt 50 ]]; then byline_pt=40
    elif [[ $byline_len -gt 42 ]]; then byline_pt=48
    elif [[ $byline_len -gt 36 ]]; then byline_pt=56
    elif [[ $byline_len -gt 30 ]]; then byline_pt=64
    fi

    if [[ -n "$role" ]]; then
        local guest_part="$tmp_dir/guest.png"
        local sep_part="$tmp_dir/sep.png"
        local role_part="$tmp_dir/role.png"

        magick -background none -fill "$PODCAST_TEXT" \
            -font "Bebas-Neue-Regular" -pointsize "$byline_pt" -kerning 2 \
            label:"${guest_uc}" "$guest_part"
        magick -background none -fill "$PODCAST_TEXT" \
            -font "Bebas-Neue-Regular" -pointsize "$byline_pt" -kerning 2 \
            label:", " "$sep_part"
        magick -background none -fill "$PODCAST_MUTED" \
            -font "Bebas-Neue-Regular" -pointsize "$byline_pt" -kerning 2 \
            label:"${role_uc}" "$role_part"

        magick "$guest_part" "$sep_part" "$role_part" \
            +append \
            "$byline_img"
    else
        magick -background none -fill "$PODCAST_TEXT" \
            -font "Bebas-Neue-Regular" -pointsize "$byline_pt" -kerning 2 \
            label:"${guest_uc}" "$byline_img"
    fi

    # ---- Episode badge (S0X E0X) ----------------------------------------
    # Mono font, framed in a subtle rounded-corner border to mirror the
    # <code> element used in the article meta line on episode pages.
    local badge_text="$tmp_dir/badge_text.png"
    magick -background none -fill "$PODCAST_TEXT" \
        -font "JetBrains-Mono-Bold" -pointsize 30 \
        label:"$episode_label" "$badge_text"

    # Read text dims to size the surrounding box.
    local tw th
    tw=$(magick identify -format "%w" "$badge_text")
    th=$(magick identify -format "%h" "$badge_text")
    local pad_x=18
    local pad_y=10
    local box_w=$((tw + pad_x * 2))
    local box_h=$((th + pad_y * 2))

    magick -size "${box_w}x${box_h}" "xc:${PODCAST_BG}" \
        -fill none -stroke "$PODCAST_BADGE_BORDER" -strokewidth 2 \
        -draw "roundrectangle 1,1 $((box_w-2)),$((box_h-2)) 6,6" \
        "$badge_text" -gravity Center -composite \
        "$badge"

    # ---- Meta line ("Published on YYYY-MM-DD") --------------------------
    magick -background none -fill "$PODCAST_MUTED" \
        -font "JetBrains-Mono-Bold" -pointsize 30 \
        label:"Published on ${date}" "$meta"

    # ---- Compose everything ---------------------------------------------
    # Layout (1200×630):
    #   PODCAST kicker     (NW +80+80)
    #   red accent bar     (NW +80+118)
    #   title              (NW +80+170)
    #   byline             (NW +80+ ~330..360 — depends on title height)
    #   badge + meta row   (NW +80+ ~480)
    #
    # We use the title image's actual height to position the byline so
    # smaller (wrapped) titles don't leave huge gaps.
    local title_h
    title_h=$(magick identify -format "%h" "$title_img")
    local byline_y=$((210 + title_h + 30))
    local meta_y=$((byline_y + 100))

    # Badge+meta row: place badge then meta to its right with a gap.
    local badge_w
    badge_w=$(magick identify -format "%w" "$badge")
    local meta_x=$((80 + badge_w + 24))

    # Compose the final image. The logo (if any) is placed in the
    # top-right, sitting comfortably over the dot-grid texture.
    if [[ -n "$logo_img" ]]; then
        magick "$bg" \
            "$logo_img"   -gravity NorthEast -geometry +60+60                  -composite \
            "$kicker"     -gravity NorthWest -geometry +80+70                  -composite \
            "$accent"     -gravity NorthWest -geometry +80+138                 -composite \
            "$title_img"  -gravity NorthWest -geometry +80+200                 -composite \
            "$byline_img" -gravity NorthWest -geometry "+80+${byline_y}"       -composite \
            "$badge"      -gravity NorthWest -geometry "+80+${meta_y}"         -composite \
            "$meta"       -gravity NorthWest -geometry "+${meta_x}+$((meta_y + 10))" -composite \
            "$output_file"
    else
        magick "$bg" \
            "$kicker"     -gravity NorthWest -geometry +80+70                  -composite \
            "$accent"     -gravity NorthWest -geometry +80+138                 -composite \
            "$title_img"  -gravity NorthWest -geometry +80+200                 -composite \
            "$byline_img" -gravity NorthWest -geometry "+80+${byline_y}"       -composite \
            "$badge"      -gravity NorthWest -geometry "+80+${meta_y}"         -composite \
            "$meta"       -gravity NorthWest -geometry "+${meta_x}+$((meta_y + 10))" -composite \
            "$output_file"
    fi

    rm -rf "$tmp_dir"
}

process_post() {
    local post="$1"
    local parent_dir="$2"

    local title
    local output_path

    # Extract the title from the frontmatter
    title=$(awk -F'"' '/^title/ {print $2}' "$post")

    # Check if the title is empty
    if [[ -z "$title" ]]; then
        echo "Title not found in $post. Skipping."
        return
    fi

    # Put the social image into the same directory as the post
    output_path="${parent_dir}/social.png"

    # Podcast episodes get per-episode images when guest metadata is present
    if [[ "$parent_dir" == *"/podcast"* ]]; then
        local guest role season episode_num date

        guest=$(awk -F'"' '/^guest[[:space:]]*=/ {print $2}' "$post")
        role=$(awk -F'"'  '/^role[[:space:]]*=/  {print $2}' "$post")
        season=$(awk -F'"' '/^season[[:space:]]*=/ {print $2}' "$post")
        episode_num=$(awk -F'"' '/^episode[[:space:]]*=/ {print $2}' "$post")
        # date is unquoted in TOML frontmatter (e.g. `date = 2026-04-09`)
        date=$(awk -F'=' '/^date[[:space:]]*=/ {gsub(/[[:space:]]/, "", $2); print $2; exit}' "$post")

        local template_file="static/social/podcast.png"

        if [[ -f "$output_path" && $FORCE -eq 0 ]]; then
            echo "File already exists: $output_path. Skipping."
            return
        fi

        if [[ -z "$guest" ]]; then
            # No guest info (teaser, season finale, holiday special, etc.)
            # — just use the generic podcast image.
            generate_social_image "$template_file" "$output_path"
        else
            local logo_path="${parent_dir}/logo.svg"
            [[ -f "$logo_path" ]] || logo_path=""
            generate_podcast_social_image \
                "$output_path" \
                "$title" \
                "$guest" \
                "$role" \
                "$season" \
                "$episode_num" \
                "$date" \
                "$logo_path"
        fi
        return
    fi

    if [[ -f "$output_path" && $FORCE -eq 0 ]]; then
        echo "File already exists: $output_path. Skipping."
        return
    fi

    echo "Generating $title ($output_path)"

    local template_file="static/social/default-template.svg"
    generate_social_image "$template_file" "$output_path" "$title"
}

process_directory() {
    local dir="$1"
    local base_output_name="$2"

    echo "Processing directory: $dir, base_output_name: $base_output_name"

    # Process _index.md if it exists
    if [[ -f "$dir/_index.md" ]]; then
        process_post "$dir/_index.md" "$dir"
    fi

    # Process regular index.md if it exists
    if [[ -f "$dir/index.md" ]]; then
        process_post "$dir/index.md" "$dir"
    fi

    # Recursively Process all subdirectories
    local subdir_basename
    for subdir in "$dir"/*; do
        if [[ -d "$subdir" && $(basename "$subdir") != _* ]]; then
            subdir_basename="${base_output_name}-$(basename "$subdir")"
            process_directory "$subdir" "$subdir_basename"
        fi
    done

    # Process markdown files in current directory
    for file in "$dir"/*.md; do
        if [[ -f "$file" && $(basename "$file") != _* && $(basename "$file") != "index.md" ]]; then
            process_post "$file" "$dir"
        fi
    done
}

# Process all content directories
for content_dir in content/*; do
    if [[ -d "$content_dir" && $(basename "$content_dir") != _* ]]; then
        process_directory "$content_dir" "$(basename "$content_dir")"
    fi
done

# Clean up any stray temporary text image from the blog-post path
rm -f text.png
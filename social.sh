#!/bin/bash

set -euo pipefail

# Function to generate social image for a given title
generate_social_image() {
    local title="$1"
    local output_file="$2"
    
    # Generate the caption image
    magick -background none -fill '#333333' -font Inter-Bold -pointsize 80 -size 740x caption:"$title" text.png

    # Composite the caption over the background image
    magick static/social/social.png text.png -gravity northwest -geometry +20+80 -composite "$output_file"
}

# Iterate over blog posts
for post in content/blog/*.md; do
    # Skip files, which start with an underscore
    if [[ $(basename "$post") == _* ]]; then
        continue
    fi
    
    # Skip directories
    if [[ -d "$post" ]]; then
        continue
    fi
   
    # Extract the title from the frontmatter
    title=$(awk -F '= ' '/title/ {gsub(/"/, "", $2); print $2}' "$post")

    # Generate the output file path
    post_filename=$(basename "$post" .md)
    output_path="static/social/rendered/${post_filename}.png"
    
    # Check if file exists; only overwrite if `--force` is passed
    if [[ -f "$output_path" && ( -z "${1:-}" || "${1:-}" != "--force" ) ]]; then
        echo "File already exists: $output_path. Skipping."
        continue
    fi
    
    echo "$title"
    echo "$output_path"
    echo

    # Call the function to generate the social image
    generate_social_image "$title" "$output_path"
done

# Clean up temporary text image
rm -f text.png

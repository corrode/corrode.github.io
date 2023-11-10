#!/bin/bash

set -euo pipefail

# Function to generate social image for a given title
generate_social_image() {
    local title="$1"
    local output_file="$2"
    
    # Generate the caption image
    magick -background none -fill '#000000' -font Inter-Bold -pointsize 80 -size 740x caption:"$title" text.png

    # Composite the caption over the background image
    magick static/social/social-post-template.svg text.png -gravity northwest -geometry +100+80 -composite "$output_file"
}

process_post() {
    local post="$1"
    local post_filename="$2"
    
    # Extract the title from the frontmatter
    title=$(awk -F '= ' '/title/ {gsub(/"/, "", $2); print $2}' "$post")

    # Generate the output file path
    output_path="static/social/rendered/${post_filename}.png"
    
    if [[ -f "$output_path" ]]; then
        echo "File already exists: $output_path. Skipping."
        return
    fi
    
    echo "Generating $title ($output_path)"

    # Call the function to generate the social image
    generate_social_image "$title" "$output_path"
}

# Iterate over blog posts and folders
for item in content/blog/*; do
    # Skip files, which start with an underscore
    if [[ $(basename "$item") == _* ]]; then
        continue
    fi

    if [[ -d "$item" && -f "$item/index.md" ]]; then
        # Process the index.md inside the folder
        process_post "$item/index.md" "$(basename "$item")"
    elif [[ -f "$item" ]]; then
        # Process the individual markdown file
        process_post "$item" "$(basename "$item" .md)"
    fi
done

# Iterate over other folders in content
for item in content/*; do
    # Skip files, which start with an underscore
    if [[ $(basename "$item") == _* ]]; then
        continue
    fi

    # Include folders, which have an _index.md file
    if [[ -d "$item" && -f "$item/_index.md" ]]; then
        # Process the index.md inside the folder
        process_post "$item/_index.md" "$(basename "$item")"
    fi
done

# Clean up temporary text image
rm -f text.png

#!/bin/bash

set -euo pipefail

# Function to generate social image for a given title
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
    
    # Use the podcast template if the post is in a podcast directory 
    # The title is empty as the image already contains text 
    if [[ "$parent_dir" == *"/podcast"* ]]; then
        template_file="static/social/podcast.png"
        generate_social_image "$template_file" "$output_path"
        return
    fi
    
    if [[ -f "$output_path" ]]; then
        echo "File already exists: $output_path. Skipping."
        return
    fi
    
    echo "Generating $title ($output_path)"

    local template_file="static/social/default-template.svg"
    generate_social_image "$template_file"  "$output_path" "$title" 
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

# Clean up temporary text image
rm -f text.png
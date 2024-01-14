#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script converts the workshops.json file into TOML front matter
and writes it to the content/workshops directory.
"""

import json
import os
import toml

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def generate_markdown(workshop):
    # Add the 'template' field to the workshop data
    workshop['template'] = "workshop.html"

    # Convert the modified workshop dictionary to TOML
    front_matter_toml = toml.dumps(workshop)

    markdown_template = f"""+++
{front_matter_toml}+++

"""

    return markdown_template

def write_markdown_file(workshop_name, markdown_content):
    dir_path = f"content/workshops/{workshop_name}"
    file_path = os.path.join(dir_path, "index.md")
    os.makedirs(dir_path, exist_ok=True)
    with open(file_path, 'w') as file:
        file.write(markdown_content)

def main():
    workshops = read_json_file("content/workshops/workshops.json")
    for workshop_name, workshop_data in workshops.items():
        markdown_content = generate_markdown(workshop_data)
        write_markdown_file(workshop_name, markdown_content)

if __name__ == "__main__":
    main()

"""
Mardblog - Markdown to HTML Parser with CSS Class Names

A command-line tool that converts Markdown files to HTML and adds customizable
CSS class names to elements. Built-in caching and API posting capabilities.

IMPORTANT: Mardblog only adds CSS class names to HTML elements. It does NOT compile
or process CSS. You must include your CSS framework (Tailwind, Bootstrap, etc.)
or custom stylesheet separately in your web page for styling to work.

Features:
    - Add CSS class names to HTML elements via simple JSON configuration
    - Default uses generic semantic class names (heading, paragraph, link, etc.)
    - Frontmatter parsing for metadata (title, slug, description, tags)
    - Smart caching system to skip unchanged files
    - Automatic API posting for new/updated content
    - Support for headings, lists, code blocks, links, and inline formatting
    - Framework agnostic: works with any CSS framework or custom CSS

Usage:
    python main.py [--force]

Arguments:
    --force: Force reprocessing of all files, even if unchanged

Directory Structure:
    posts/         Input markdown files with frontmatter
    artifacts/     Cached HTML and metadata for comparison
    mardblog.config.json  Configuration for styling and API settings

Example:
    $ python main.py
    $ python main.py --force

Author: Mardblog CLI Tool
Version: 2.0.0
"""

import hashlib
import json
import re
import sys
from pathlib import Path

import requests


class MarkdownParser:
    """
    Parse markdown content and convert to HTML with CSS class names.

    This parser converts markdown elements to HTML and adds configurable CSS class
    names to the elements. It does NOT compile or process CSS - it only adds the
    class attributes to HTML tags. You must include your CSS framework or stylesheet
    separately for the styling to work.

    Handles: headings, paragraphs, code blocks, lists, and inline formatting
    (bold, italic, links, inline code).

    Attributes:
        html_output (list): Accumulated HTML output strings
        in_code_block (bool): Flag indicating if currently parsing a code block
        code_language (str): Language identifier for current code block
        code_lines (list): Lines accumulated for current code block
        in_list (bool): Flag indicating if currently parsing a list
        list_items (list): Items accumulated for current list
        config (dict): Styling configuration mapping elements to class names
    """

    def __init__(self, config=None):
        """
        Initialize the MarkdownParser with optional configuration.

        Args:
            config (dict, optional): Custom styling configuration. If None,
                default configuration will be used. The config should map
                HTML elements/components to their CSS class names.
        """
        self.html_output = []
        self.in_code_block = False
        self.code_language = ""
        self.code_lines = []
        self.in_list = False
        self.list_items = []
        self.config = config or self._default_config()

    def _default_config(self):
        """
        Return the default CSS class name configuration for all markdown elements.

        Returns a simple dictionary mapping HTML element identifiers to CSS class names.
        The default uses generic, semantic class names that you can style with your
        own CSS or replace with framework-specific classes (Tailwind, Bootstrap, etc.).

        Returns:
            dict: Default configuration with element->class name mappings
        """
        return {
            # Heading elements
            "h1": "heading heading-1",
            "h2": "heading heading-2",
            "h3": "heading heading-3",
            "h4": "heading heading-4",
            "h5": "heading heading-5",
            "h6": "heading heading-6",
            # Paragraph and text
            "p": "paragraph",
            "strong": "bold",
            "em": "italic",
            # Links
            "a": "link",
            # Code
            "code": "code-inline",
            "pre": "code-block",
            "pre_code": "code-block-content",
            # Lists
            "ul": "list",
            "li": "list-item",
            # Container/wrapper
            "article": "article-container",
        }

    def parse(self, markdown_content):
        """
        Parse markdown content and convert to styled HTML.

        Processes the markdown line by line, handling code blocks, lists,
        headings, and paragraphs. Maintains state for multi-line elements
        like code blocks and lists.

        Args:
            markdown_content (str): Raw markdown text to parse

        Returns:
            str: Complete HTML output with CSS styling
        """
        lines = markdown_content.split("\n")

        for i, line in enumerate(lines):
            # Check for code block
            if line.strip().startswith("```"):
                if not self.in_code_block:
                    # Starting code block
                    self.in_code_block = True
                    self.code_language = line.strip()[3:].strip() or "plaintext"
                    self.code_lines = []
                else:
                    # Ending code block
                    self.in_code_block = False
                    self._add_code_block()
                continue

            if self.in_code_block:
                self.code_lines.append(line)
                continue

            # Check for list items
            if line.strip().startswith(("- ", "* ", "+ ")):
                if not self.in_list:
                    self.in_list = True
                    self.list_items = []
                item_text = line.strip()[2:].strip()
                self.list_items.append(item_text)
                continue
            elif (
                self.in_list
                and line.strip()
                and not line.strip().startswith(("- ", "* ", "+ "))
            ):
                # End of list
                self._add_list()
                self.in_list = False
            elif self.in_list and not line.strip():
                # Empty line in list - end list
                self._add_list()
                self.in_list = False
                continue

            # Check for headings
            if line.strip().startswith("#"):
                self._add_heading(line)
            # Check for empty lines
            elif not line.strip():
                continue
            # Regular paragraph
            else:
                self._add_paragraph(line)

        # Handle any unclosed lists
        if self.in_list:
            self._add_list()

        return "\n".join(self.html_output)

    def _add_heading(self, line):
        """
        Convert a markdown heading to styled HTML.

        Args:
            line (str): Markdown heading line (e.g., "# Title" or "## Subtitle")

        Side Effects:
            Appends formatted HTML heading to self.html_output
        """
        line = line.strip()
        level = 0
        while level < len(line) and line[level] == "#":
            level += 1

        text = line[level:].strip()
        heading_tag = f"h{min(level, 6)}"
        heading_class = self.config.get(heading_tag, "")

        if heading_class:
            html = f'<{heading_tag} class="{heading_class}">{text}</{heading_tag}>'
        else:
            html = f"<{heading_tag}>{text}</{heading_tag}>"

        self.html_output.append(html)

    def _add_paragraph(self, line):
        """
        Convert a paragraph line to styled HTML with inline formatting.

        Processes inline markdown elements including:
        - Inline code (`code`)
        - Bold text (**bold** or __bold__)
        - Italic text (*italic* or _italic_)
        - Links ([text](url))

        Args:
            line (str): Paragraph text with potential inline markdown

        Side Effects:
            Appends formatted HTML paragraph to self.html_output
        """
        text = line.strip()
        if not text:
            return

        # Get class names
        p_class = self.config.get("p", "")
        code_class = self.config.get("code", "")
        strong_class = self.config.get("strong", "")
        em_class = self.config.get("em", "")
        a_class = self.config.get("a", "")

        # Process inline code
        if code_class:
            text = re.sub(
                r"`([^`]+)`",
                rf'<code class="{code_class}">\1</code>',
                text,
            )
        else:
            text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)

        # Process bold text
        if strong_class:
            text = re.sub(
                r"\*\*([^*]+)\*\*",
                rf'<strong class="{strong_class}">\1</strong>',
                text,
            )
            text = re.sub(
                r"__([^_]+)__",
                rf'<strong class="{strong_class}">\1</strong>',
                text,
            )
        else:
            text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
            text = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", text)

        # Process italic text
        if em_class:
            text = re.sub(r"\*([^*]+)\*", rf'<em class="{em_class}">\1</em>', text)
            text = re.sub(r"_([^_]+)_", rf'<em class="{em_class}">\1</em>', text)
        else:
            text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
            text = re.sub(r"_([^_]+)_", r"<em>\1</em>", text)

        # Process links
        if a_class:
            text = re.sub(
                r"\[([^\]]+)\]\(([^\)]+)\)",
                rf'<a href="\2" class="{a_class}">\1</a>',
                text,
            )
        else:
            text = re.sub(
                r"\[([^\]]+)\]\(([^\)]+)\)",
                r'<a href="\2">\1</a>',
                text,
            )

        if p_class:
            html = f'<p class="{p_class}">{text}</p>'
        else:
            html = f"<p>{text}</p>"

        self.html_output.append(html)

    def _add_code_block(self):
        """
        Add a code block with styling.

        Creates a styled code block using accumulated code lines from
        self.code_lines. Escapes HTML entities.

        Side Effects:
            - Appends formatted HTML code block to self.html_output
            - Clears self.code_lines and self.code_language
        """
        code_content = "\n".join(self.code_lines)

        # Escape HTML in code
        code_content = code_content.replace("&", "&amp;")
        code_content = code_content.replace("<", "&lt;")
        code_content = code_content.replace(">", "&gt;")

        pre_class = self.config.get("pre", "")
        pre_code_class = self.config.get("pre_code", "")

        if pre_class and pre_code_class:
            html = f'<pre class="{pre_class}"><code class="{pre_code_class}">{code_content}</code></pre>'
        elif pre_class:
            html = f'<pre class="{pre_class}"><code>{code_content}</code></pre>'
        elif pre_code_class:
            html = f'<pre><code class="{pre_code_class}">{code_content}</code></pre>'
        else:
            html = f"<pre><code>{code_content}</code></pre>"

        self.html_output.append(html)
        self.code_lines = []
        self.code_language = ""

    def _add_list(self):
        """
        Add an unordered list with styled items.

        Creates a list from accumulated items in self.list_items, applying
        inline formatting to each item.

        Side Effects:
            - Appends formatted HTML list to self.html_output
            - Clears self.list_items
        """
        if not self.list_items:
            return

        # Get class names
        ul_class = self.config.get("ul", "")
        li_class = self.config.get("li", "")
        code_class = self.config.get("code", "")
        strong_class = self.config.get("strong", "")
        em_class = self.config.get("em", "")
        a_class = self.config.get("a", "")

        list_items_html = []
        for item in self.list_items:
            # Process inline formatting in list items
            if code_class:
                item = re.sub(
                    r"`([^`]+)`",
                    rf'<code class="{code_class}">\1</code>',
                    item,
                )
            else:
                item = re.sub(r"`([^`]+)`", r"<code>\1</code>", item)

            if strong_class:
                item = re.sub(
                    r"\*\*([^*]+)\*\*",
                    rf'<strong class="{strong_class}">\1</strong>',
                    item,
                )
            else:
                item = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", item)

            if em_class:
                item = re.sub(r"\*([^*]+)\*", rf'<em class="{em_class}">\1</em>', item)
            else:
                item = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", item)

            if a_class:
                item = re.sub(
                    r"\[([^\]]+)\]\(([^\)]+)\)",
                    rf'<a href="\2" class="{a_class}">\1</a>',
                    item,
                )
            else:
                item = re.sub(
                    r"\[([^\]]+)\]\(([^\)]+)\)",
                    r'<a href="\2">\1</a>',
                    item,
                )

            if li_class:
                list_items_html.append(f'<li class="{li_class}">{item}</li>')
            else:
                list_items_html.append(f"<li>{item}</li>")

        if ul_class:
            html = f'<ul class="{ul_class}">\n' + "\n".join(list_items_html) + "\n</ul>"
        else:
            html = "<ul>\n" + "\n".join(list_items_html) + "\n</ul>"

        self.html_output.append(html)
        self.list_items = []


def parse_frontmatter(content):
    """
    Parse YAML-style frontmatter from markdown content.

    Extracts metadata from the top of a markdown file enclosed in "---"
    delimiters. Supports simple key-value pairs and list values (for tags).

    Args:
        content (str): Full markdown file content including frontmatter

    Returns:
        tuple: A tuple containing:
            - dict: Parsed frontmatter as key-value pairs
            - str: Remaining markdown content after frontmatter

    Example:
        >>> content = "---\\ntitle: My Post\\ntags: [python, web]\\n---\\n# Content"
        >>> meta, markdown = parse_frontmatter(content)
        >>> print(meta)
        {'title': 'My Post', 'tags': ['python', 'web']}
    """
    frontmatter = {}
    markdown_content = content

    # Check if content starts with ---
    if content.strip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1].strip()
            markdown_content = parts[2].strip()

            # Parse frontmatter (simple key: value parser)
            for line in frontmatter_text.split("\n"):
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Handle lists (tags)
                    if value.startswith("[") and value.endswith("]"):
                        # Parse as list
                        value = [
                            tag.strip().strip('"').strip("'")
                            for tag in value[1:-1].split(",")
                        ]
                    else:
                        # Remove quotes if present
                        value = value.strip('"').strip("'")

                    frontmatter[key] = value

    return frontmatter, markdown_content


def load_config(config_path):
    """
    Load configuration from a JSON file.

    Args:
        config_path (Path): Path to the configuration JSON file

    Returns:
        dict or None: Parsed configuration dictionary if file exists,
            None otherwise
    """
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def create_default_config(config_path):
    """
    Create a default configuration file with CSS class names and API settings.

    Generates a JSON configuration file with default generic CSS class names
    for all markdown elements and a template for API configuration.

    Note: The generated class names are generic semantic names. You can style
    them with your own CSS or replace them with framework-specific classes.

    Args:
        config_path (Path): Path where the config file should be created

    Side Effects:
        - Creates a new JSON file at config_path
        - Prints confirmation message with file path
    """
    parser = MarkdownParser()
    default_config = {
        "styling": parser._default_config(),
        "api": {
            "enabled": False,
            "url": "https://your-api.com/api/posts",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer YOUR_API_KEY_HERE",
            },
        },
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=2)

    print(f"Created default config file: {config_path}")


def get_file_hash(content):
    """
    Generate a SHA-256 hash of content for change detection.

    Args:
        content (str): Content to hash (typically HTML output)

    Returns:
        str: Hexadecimal SHA-256 hash digest
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def should_process_post(post_slug, html_content, artifacts_dir):
    """
    Check if a post needs processing by comparing with cached version.

    Compares the hash of the current HTML content with the hash stored
    in the artifact cache. Returns True if the post is new or has changed.

    Args:
        post_slug (str): Unique identifier for the post
        html_content (str): Generated HTML content to compare
        artifacts_dir (Path): Directory containing cached artifacts

    Returns:
        bool: True if post should be processed (new or changed),
            False if unchanged
    """
    artifact_file = artifacts_dir / f"{post_slug}.json"

    if not artifact_file.exists():
        return True

    # Load cached artifact
    with open(artifact_file, "r", encoding="utf-8") as f:
        cached = json.load(f)

    # Compare hash
    current_hash = get_file_hash(html_content)
    return cached.get("hash") != current_hash


def save_artifact(post_slug, html_content, metadata, artifacts_dir):
    """
    Save HTML content and metadata to the artifact cache.

    Creates a JSON file containing the post's HTML, metadata, and a hash
    for future comparison. Used to determine if posts need reprocessing.

    Args:
        post_slug (str): Unique identifier for the post
        html_content (str): Generated HTML content
        metadata (dict): Post metadata (title, slug, description, tags, etc.)
        artifacts_dir (Path): Directory to save artifact

    Side Effects:
        Creates or overwrites a JSON file at artifacts_dir/{post_slug}.json
    """
    artifact = {
        "slug": post_slug,
        "hash": get_file_hash(html_content),
        "html": html_content,
        "metadata": metadata,
    }

    artifact_file = artifacts_dir / f"{post_slug}.json"
    with open(artifact_file, "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)


def post_to_api(post_data, api_config):
    """
    Post article data to a configured API endpoint.

    Sends post data (title, slug, content, description, tags) to the
    specified API using either POST or PUT method with custom headers.

    Args:
        post_data (dict): Article data to post containing keys:
            - title (str): Post title
            - slug (str): Post slug/identifier
            - content (str): HTML content
            - description (str): Meta description
            - tags (list): List of tag strings
        api_config (dict): API configuration containing:
            - enabled (bool): Whether API posting is enabled
            - url (str): API endpoint URL
            - method (str): HTTP method (POST or PUT)
            - headers (dict): Request headers

    Returns:
        bool: True if API post succeeded (200/201 response),
            False if disabled, failed, or error occurred

    Side Effects:
        Prints status messages about API posting progress and results
    """
    if not api_config.get("enabled") or requests is None:
        return False

    try:
        url = api_config.get("url")
        if not url:
            print("  ✗ API URL not configured")
            return False

        method = api_config.get("method", "POST").upper()
        headers = api_config.get("headers", {})

        print(f"  Posting to API: {url}")

        if method == "POST":
            response = requests.post(url, json=post_data, headers=headers, timeout=30)
        elif method == "PUT":
            response = requests.put(url, json=post_data, headers=headers, timeout=30)
        else:
            print(f"  Unsupported HTTP method: {method}")
            return False

        if response.status_code in [200, 201]:
            print(f"  ✓ API post successful: {response.status_code}")
            return True
        else:
            print(f"  ✗ API post failed: {response.status_code} - {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"  ✗ API request error: {e}")
        return False


def process_markdown_file(input_path, artifacts_dir, config, force=False):
    """
    Process a single markdown file to generate HTML and prepare for API posting.

    Complete workflow:
    1. Read markdown file
    2. Parse frontmatter for metadata
    3. Convert markdown to HTML with configured styling
    4. Check if content has changed (unless force=True)
    5. Save to artifact cache if new or changed
    6. Return post data for API posting

    Args:
        input_path (Path): Path to the markdown file to process
        artifacts_dir (Path): Directory for artifact cache storage
        config (dict): Configuration containing styling settings
        force (bool, optional): If True, process file even if unchanged.
            Defaults to False.

    Returns:
        dict or None: Post data dictionary if processed, None if skipped.
            Post data contains:
            - title (str): Post title from frontmatter
            - slug (str): URL-friendly slug
            - content (str): Complete HTML content
            - description (str): Meta description
            - tags (list): List of tags

    Side Effects:
        - Prints processing status messages
        - Creates/updates artifact cache file
    """
    print(f"\nProcessing: {input_path.name}")

    # Read markdown content
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse frontmatter
    frontmatter, markdown_content = parse_frontmatter(content)

    # Extract metadata
    title = frontmatter.get("title", input_path.stem)
    slug = frontmatter.get("slug", input_path.stem.lower().replace(" ", "-"))
    description = frontmatter.get("description", "")
    tags = frontmatter.get("tags", [])

    # Parse markdown to HTML
    styling_config = config.get("styling", None)
    parser = MarkdownParser(styling_config)
    html_content = parser.parse(markdown_content)

    # Wrap in article container
    article_class = styling_config.get("article", "") if styling_config else ""
    if article_class:
        full_html = f'<article class="{article_class}">\n{html_content}\n</article>'
    else:
        full_html = f"<article>\n{html_content}\n</article>"

    # Check if needs processing
    if not force and not should_process_post(slug, full_html, artifacts_dir):
        print("  ⊘ Skipped (unchanged)")
        return None

    # Save artifact
    metadata = {
        "title": title,
        "slug": slug,
        "description": description,
        "tags": tags,
        "source_file": input_path.name,
    }
    save_artifact(slug, full_html, metadata, artifacts_dir)

    print("  ✓ Processed and cached")

    # Return post data for API
    return {
        "title": title,
        "slug": slug,
        "content": full_html,
        "description": description,
        "tags": tags,
    }


def main():
    """
    Main CLI entry point for the Mardblog markdown processor.

    Workflow:
    1. Create necessary directories (posts/, artifacts/)
    2. Load or create configuration file
    3. Find all markdown files in posts/ directory
    4. Process each file (parse, convert, cache)
    5. Post new/updated content to API if enabled
    6. Display summary of results

    Command-line Arguments:
        --force: Force reprocessing of all files, ignoring cache

    Side Effects:
        - Creates posts/ and artifacts/ directories if they don't exist
        - Creates mardblog.config.json if it doesn't exist
        - Processes markdown files and updates artifact cache
        - Posts to API if configured and enabled
        - Prints progress and status messages throughout

    Exit Conditions:
        - Returns early if config file is newly created (prompts user to configure)
        - Returns early if no markdown files found in posts/ directory
    """
    print("=" * 60)
    print("Mardblog - Markdown to HTML Converter")
    print("=" * 60)

    # Define directories - use current working directory
    working_dir = Path.cwd()
    posts_dir = working_dir / "posts"
    artifacts_dir = working_dir / "artifacts"
    config_path = working_dir / "mardblog.config.json"

    # Create directories if they don't exist
    posts_dir.mkdir(exist_ok=True)
    artifacts_dir.mkdir(exist_ok=True)

    print("\nDirectories:")
    print(f"  Posts:     {posts_dir}")
    print(f"  Artifacts: {artifacts_dir}")
    print(f"  Config:    {config_path}")

    # Load or create config
    if not config_path.exists():
        print("\n⚠ Config file not found. Creating default config...")
        create_default_config(config_path)
        print(
            "\nPlease edit mardblog.config.json to customize styling and API settings."
        )
        print("Run the program again after configuring.")
        return

    config = load_config(config_path)
    if config is None:
        config = {}
    api_config = config.get("api", {})

    # Check for --force flag
    force = "--force" in sys.argv

    # Find all markdown files
    markdown_files = list(posts_dir.glob("*.md"))

    if not markdown_files:
        print(f"\n⚠ No markdown files found in {posts_dir}")
        print("Please add .md files to process.")
        return

    print(f"\n{'-' * 60}")
    print(f"Found {len(markdown_files)} markdown file(s) to process")
    if force:
        print("Force mode: All posts will be processed")
    print(f"{'-' * 60}")

    # Process each file
    posts_to_api = []
    for md_file in markdown_files:
        try:
            post_data = process_markdown_file(md_file, artifacts_dir, config, force)
            if post_data and api_config.get("enabled"):
                posts_to_api.append(post_data)
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Post to API if enabled
    if posts_to_api and api_config.get("enabled"):
        print(f"\n{'-' * 60}")
        print(f"Posting {len(posts_to_api)} post(s) to API")
        print(f"{'-' * 60}")

        for post_data in posts_to_api:
            print(f"\nPost: {post_data['title']}")
            post_to_api(post_data, api_config)

    print(f"\n{'-' * 60}")
    print("Processing complete!")
    print(f"Artifacts saved to: {artifacts_dir}")
    print(f"{'-' * 60}\n")


if __name__ == "__main__":
    main()

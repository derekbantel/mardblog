# Weave - Markdown to HTML Converter

A powerful CLI tool that converts Markdown files to beautifully styled HTML using Tailwind CSS, with built-in caching and API posting capabilities.

## Features

- 🎨 **Customizable Styling**: Configure Tailwind CSS classes for all markdown elements via JSON config
- 📝 **Frontmatter Support**: Parse metadata (title, slug, description, tags) from markdown files
- 💾 **Smart Caching**: Only processes files that have changed using hash-based comparison
- 🚀 **API Integration**: Automatically post processed content to your API endpoint
- 📁 **Auto-folder Creation**: Creates necessary directories on first run
- ⚡ **Fast Processing**: Skip unchanged files for efficient rebuilds

## Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install requests
```

## Quick Start

1. Run the program for the first time to create the necessary folders and config:

```bash
python main.py
```

2. Add markdown files to the `posts/` folder
3. Edit `weave.config.json` to customize styling and API settings
4. Run again to process your markdown files:

```bash
python main.py
```

## Directory Structure

```
weave/
├── main.py                 # Main program
├── weave.config.json       # Configuration file
├── posts/                  # Place your markdown files here
│   └── sample-post.md
└── artifacts/              # Cached HTML and metadata
    └── sample-post.json
```

## Markdown File Format

Your markdown files should include frontmatter at the top with metadata:

```markdown
---
title: My Awesome Blog Post
slug: my-awesome-blog-post
description: This is a great post about something interesting
tags: [python, markdown, webdev]
---

# Main Heading

Your markdown content goes here...

## Subheading

- List item 1
- List item 2

**Bold text** and *italic text* are supported.

`Inline code` and code blocks too:

\`\`\`python
def hello_world():
    print("Hello, World!")
\`\`\`

[Links work too](https://example.com)
```

### Frontmatter Fields

- **title**: The post title (required)
- **slug**: URL-friendly identifier (defaults to filename if not provided)
- **description**: Meta description for SEO
- **tags**: Array of tags/categories

## Configuration

The `weave.config.json` file has two main sections:

### Styling Configuration

Customize Tailwind CSS classes for each markdown element:

```json
{
  "styling": {
    "h1": {
      "container": "mb-8",
      "heading": "text-5xl font-bold mb-4",
      "prefix": "$",
      "prefix_class": "text-primary",
      "divider": true
    },
    "paragraph": {
      "container": "mb-4",
      "text": "text-base leading-relaxed opacity-90"
    },
    "code_inline": {
      "class": "px-2 py-1 bg-gray-100 text-blue-600 rounded font-mono text-sm"
    }
    // ... more elements
  }
}
```

You can customize:
- `h1`, `h2`, `h3`, `h4`, `h5` - Heading styles
- `paragraph` - Paragraph styles
- `code_inline` - Inline code styles
- `code_block` - Code block styles
- `bold` - Bold text styles
- `italic` - Italic text styles
- `link` - Link styles
- `list` - List and bullet styles
- `card` - Container card styles

### API Configuration

Configure automatic posting to your API:

```json
{
  "api": {
    "enabled": true,
    "url": "https://your-api.com/api/posts",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer YOUR_API_KEY_HERE"
    }
  }
}
```

The program will send this JSON structure to your API:

```json
{
  "title": "Post Title",
  "slug": "post-slug",
  "content": "<div class=\"card\">...</div>",
  "description": "Post description",
  "tags": ["tag1", "tag2"]
}
```

## CLI Usage

### Basic Usage

Process all markdown files in the `posts/` folder:

```bash
python main.py
```

### Force Processing

Force reprocessing of all files, even if unchanged:

```bash
python main.py --force
```

## How It Works

1. **Scanning**: The program scans the `posts/` directory for `.md` files
2. **Parsing**: Each file is parsed for frontmatter and markdown content
3. **Comparison**: The generated HTML is hashed and compared to cached version in `artifacts/`
4. **Processing**: Only changed files are processed and saved
5. **API Posting**: If enabled, new/updated posts are sent to your API
6. **Caching**: Processed HTML and metadata are saved in `artifacts/` for future comparisons

## Caching System

The `artifacts/` folder contains JSON files for each processed post:

```json
{
  "slug": "post-slug",
  "hash": "sha256-hash-of-content",
  "html": "<div class=\"card\">...</div>",
  "metadata": {
    "title": "Post Title",
    "slug": "post-slug",
    "description": "Description",
    "tags": ["tag1", "tag2"],
    "source_file": "post.md"
  }
}
```

This allows Weave to:
- Skip unchanged files for faster processing
- Track which posts need API updates
- Maintain a history of processed content

## Supported Markdown Features

- ✅ Headings (H1-H5)
- ✅ Paragraphs
- ✅ Bold and italic text
- ✅ Inline code
- ✅ Code blocks with language support
- ✅ Unordered lists
- ✅ Links
- ✅ Frontmatter metadata

## Examples

### Example: Custom Heading Style

Change H1 headings to use a different prefix and color:

```json
{
  "styling": {
    "h1": {
      "container": "mb-8",
      "heading": "text-6xl font-extrabold mb-4 text-purple-600",
      "prefix": ">>>",
      "prefix_class": "text-pink-500",
      "divider": true
    }
  }
}
```

### Example: API with Authentication

```json
{
  "api": {
    "enabled": true,
    "url": "https://api.myblog.com/posts",
    "method": "POST",
    "headers": {
      "Content-Type": "application/json",
      "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "X-API-Key": "your-api-key"
    }
  }
}
```

## Troubleshooting

### "No markdown files found"

Make sure you have `.md` files in the `posts/` directory.

### API posting fails

- Check that `api.enabled` is set to `true`
- Verify your API URL is correct
- Ensure your authentication headers are valid
- Check API endpoint expects the JSON format Weave sends

### Files not being processed

- By default, only changed files are processed
- Use `--force` flag to reprocess all files
- Check that files have the `.md` extension

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this in your projects!
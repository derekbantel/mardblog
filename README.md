# Mardblog - Markdown to HTML Converter

A CLI tool that converts Markdown files to HTML with customizable CSS classes, featuring built-in caching and API posting capabilities. This is primarly a blog focused tool. Where you want to write your posts in Markdown and have that formatted to html with css styling then send that so a API with a json payload for auto upload into your blog. This is assuming your blog is custom so that you have control of the API endpoints. This a tool I personally utilize for my blogs.  

## Features

- 🎨 **Simple Styling**: Add CSS class names to HTML elements via JSON config
- 📝 **Frontmatter Support**: Parse metadata (title, slug, description, tags) from markdown files
- 💾 **Smart Caching**: Only processes files that have changed using hash-based comparison
- 🚀 **API Integration**: Automatically post processed content to your API endpoint
- 📁 **Auto-folder Creation**: Creates necessary directories on first run
- ⚡ **Fast Processing**: Skip unchanged files for efficient rebuilds
- 🔧 **Framework Agnostic**: Use generic class names or swap in Tailwind, Bootstrap, or any CSS framework

## Installation

### Using uv (recommended)

Install as a tool globally:

```bash
uv tool install mardblog
```

Or install from a local clone:

```bash
git clone <repository-url>
cd mardblog
uv tool install .
```

### Using pip

```bash
pip install mardblog
```

Or install from a local clone:

```bash
git clone <repository-url>
cd mardblog
pip install .
```

### Development Installation

For local development:

```bash
git clone <repository-url>
cd mardblog
uv pip install -e .
# or
pip install -e .
```

## Important: How CSS Works

**Mardblog only adds CSS class names to your HTML** - it does not compile or process CSS. 

The default configuration uses **generic semantic class names** like `heading`, `paragraph`, `link`, etc. You can:
1. **Write your own CSS** to style these classes
2. **Replace them** with framework-specific classes (Tailwind, Bootstrap, etc.)
3. **Use them as-is** and add your own styles

The generated HTML will only be styled if you include a stylesheet in your web page.

## Quick Start

1. Navigate to your project directory and run `mardblog` for the first time to create the necessary folders and config:

```bash
cd /path/to/your/project
mardblog
```

2. Add markdown files to the `posts/` folder
3. Edit `mardblog.config.json` to customize CSS classes
4. Run again to process your markdown files:

```bash
mardblog
```

## Directory Structure

After running `mardblog` in your project directory, the following structure will be created:

```
your-project/
├── mardblog.config.json       # Configuration file (auto-generated)
├── posts/                  # Place your markdown files here (auto-generated)
│   └── sample-post.md
└── artifacts/              # Cached HTML and metadata (auto-generated)
    └── sample-post.json
```

The `mardblog` command operates on the current working directory, so you can use it in any project.

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

The `mardblog.config.json` file has two main sections:

### Styling Configuration

The styling configuration is **simple and straightforward**. Just map HTML elements to CSS class names.

The default configuration uses **generic semantic class names**:

```json
{
  "styling": {
    "h1": "heading heading-1",
    "h2": "heading heading-2",
    "h3": "heading heading-3",
    "p": "paragraph",
    "a": "link",
    "strong": "bold",
    "em": "italic",
    "code": "code-inline",
    "pre": "code-block",
    "pre_code": "code-block-content",
    "ul": "list",
    "li": "list-item",
    "article": "article-container"
  }
}
```

**Important:** Mardblog only adds these class names to your HTML. You need to either:
1. Create CSS rules for these classes, OR
2. Replace them with framework-specific classes (see examples below)

#### Available Elements

You can customize CSS classes for these elements:

**Headings:**
- `h1`, `h2`, `h3`, `h4`, `h5`, `h6` - Heading tags

**Text:**
- `p` - Paragraphs
- `strong` - Bold text
- `em` - Italic text

**Links:**
- `a` - Anchor/link tags

**Code:**
- `code` - Inline code
- `pre` - Code block container
- `pre_code` - Code element inside pre blocks

**Lists:**
- `ul` - Unordered list container
- `li` - List items

**Container:**
- `article` - Main wrapper for the entire converted content

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
  "content": "<article class=\"...\">...</article>",
  "description": "Post description",
  "tags": ["tag1", "tag2"]
}
```

## CLI Usage

### Basic Usage

Navigate to your project directory and process all markdown files in the `posts/` folder:

```bash
cd /path/to/your/project
mardblog
```

### Force Processing

Force reprocessing of all files, even if unchanged:

```bash
mardblog --force
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
  "html": "<article class=\"...\">...</article>",
  "metadata": {
    "title": "Post Title",
    "slug": "post-slug",
    "description": "Description",
    "tags": ["tag1", "tag2"],
    "source_file": "post.md"
  }
}
```

This allows Mardblog to:
- Skip unchanged files for faster processing
- Track which posts need API updates
- Maintain a history of processed content

## Supported Markdown Features

- ✅ Headings (H1-H6)
- ✅ Paragraphs
- ✅ Bold and italic text
- ✅ Inline code
- ✅ Code blocks with language support
- ✅ Unordered lists
- ✅ Links
- ✅ Frontmatter metadata

## Examples

### Example 1: Style the Default Generic Classes with Your Own CSS

Keep the default config and create a CSS file:

```css
/* style.css */
.article-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.heading {
  font-family: 'Georgia', serif;
  color: #1a1a1a;
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.heading-1 { font-size: 2.5rem; font-weight: 700; }
.heading-2 { font-size: 2rem; font-weight: 600; }
.heading-3 { font-size: 1.5rem; font-weight: 600; }

.paragraph {
  line-height: 1.8;
  margin-bottom: 1rem;
  color: #333;
}

.link {
  color: #0066cc;
  text-decoration: underline;
}

.link:hover {
  color: #0052a3;
}

.code-inline {
  background: #f4f4f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.code-block {
  background: #2d2d2d;
  color: #f8f8f8;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.code-block-content {
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.list {
  margin-bottom: 1rem;
  padding-left: 2rem;
}

.list-item {
  margin-bottom: 0.5rem;
}
```

### Example 2: Use Tailwind CSS Classes

Replace the generic classes with Tailwind:

```json
{
  "styling": {
    "h1": "text-4xl font-bold text-gray-900 mb-6 mt-8",
    "h2": "text-3xl font-semibold text-gray-800 mb-4 mt-6",
    "h3": "text-2xl font-semibold text-gray-800 mb-3 mt-5",
    "p": "text-gray-700 leading-relaxed mb-4",
    "a": "text-blue-600 hover:text-blue-800 underline transition-colors",
    "strong": "font-bold text-gray-900",
    "em": "italic text-gray-700",
    "code": "px-2 py-1 bg-gray-100 text-pink-600 rounded font-mono text-sm",
    "pre": "bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto mb-6",
    "pre_code": "font-mono text-sm",
    "ul": "list-disc list-inside space-y-2 mb-4 ml-4",
    "li": "text-gray-700 leading-relaxed",
    "article": "max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8"
  }
}
```

Include Tailwind in your HTML:
```html
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
```

### Example 3: Use Bootstrap Classes

```json
{
  "styling": {
    "h1": "display-4 fw-bold mb-4",
    "h2": "h2 fw-semibold mb-3",
    "h3": "h3 fw-normal mb-3",
    "p": "lead text-muted mb-3",
    "a": "link-primary",
    "strong": "fw-bold",
    "em": "fst-italic",
    "code": "badge bg-light text-dark font-monospace",
    "pre": "bg-dark text-light p-3 rounded",
    "pre_code": "font-monospace",
    "ul": "list-group list-group-flush mb-3",
    "li": "list-group-item",
    "article": "container bg-white shadow-sm p-5 rounded"
  }
}
```

Include Bootstrap in your HTML:
```html
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5/dist/css/bootstrap.min.css" rel="stylesheet">
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

## How CSS Works with Mardblog

**Important:** Mardblog is a HTML generator - it only adds CSS class names to your HTML elements. It does **NOT** compile or process any CSS.

### The Default Configuration

Mardblog comes with **generic semantic class names** like `heading`, `paragraph`, `link`, etc.

**Your HTML output will look like:**
```html
<h1 class="heading heading-1">My Title</h1>
<p class="paragraph">Some text here.</p>
<a href="#" class="link">Click me</a>
```

**You have 3 options:**

1. **Write CSS for these classes** (see Example 1 above)
2. **Replace them with framework classes** like Tailwind or Bootstrap (see Examples 2 & 3)
3. **Use empty strings** for plain HTML with no classes

### Plain HTML (No Classes)

Want semantic HTML with no class attributes? Use empty strings:

```json
{
  "styling": {
    "h1": "",
    "h2": "",
    "p": "",
    "a": "",
    "code": "",
    "article": ""
  }
}
```

This generates clean HTML like `<h1>Title</h1>` with no class attributes.

## Troubleshooting

### "No markdown files found"

Make sure you have `.md` files in the `posts/` directory.

### API posting fails

- Check that `api.enabled` is set to `true`
- Verify your API URL is correct
- Ensure your authentication headers are valid
- Check API endpoint expects the JSON format Mardblog sends

### Files not being processed

- By default, only changed files are processed
- Use `--force` flag to reprocess all files
- Check that files have the `.md` extension

### Classes not appearing in HTML

- Make sure your classes are properly quoted in the JSON config
- Verify the JSON syntax is valid (use a JSON validator)
- Check the generated HTML in the `artifacts/` folder

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this in your projects!

## Important Notes

### Mardblog is a HTML Generator Only

Mardblog **does not compile or process CSS**. It only:
1. Converts Markdown to HTML
2. Adds CSS class names you specify to the HTML elements

You are responsible for:
1. Including the CSS framework or stylesheet in your web page
2. Ensuring the class names match your CSS framework or custom styles

### Example Workflow

1. **Configure Mardblog** with your desired class names:
```json
{ "h1": "text-4xl font-bold" }
```

2. **Mardblog generates HTML** with those classes:
```html
<h1 class="text-4xl font-bold">My Title</h1>
```

3. **You include the CSS** in your web page:
```html
<link href="https://cdn.tailwindcss.com" rel="stylesheet">
<div id="content">
  <!-- Insert Mardblog-generated HTML here -->
</div>
```

4. **The browser applies the styling** from your CSS framework

import re
import toml
from typing import Dict, Any, List, Tuple


class MarkdownTomlTransformer:
    def __init__(self):
        # Regex pattern to match TOML code blocks
        self.toml_block_pattern = re.compile(
            r'```toml\n(.*?)\n```',
            re.DOTALL
        )
        self.comment_pattern = re.compile(r'^##?\s*(.*)$', re.MULTILINE)

    def extract_comment_above(self, toml_content: str, key: str) -> str:
        """Extract the comment above a specific TOML key."""
        lines = toml_content.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith(key):
                # Look for comments above this line
                comments = []
                j = i - 1
                while j >= 0 and lines[j].strip().startswith('#'):
                    comment = self.comment_pattern.match(lines[j].strip())
                    if comment:
                        comments.insert(0, comment.group(1).strip())
                    j -= 1
                return ' '.join(comments)
        return ""

    def parse_toml_structure(self, toml_content: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Parse TOML content and extract comments."""
        data = toml.loads(toml_content)
        comments = {}

        # Extract comments for top-level keys
        for key in data.keys():
            if isinstance(data[key], dict):
                continue
            comments[key] = self.extract_comment_above(toml_content, key)

        # Handle nested structures
        def process_dict(d: Dict[str, Any], prefix: str = "") -> None:
            for key, value in d.items():
                full_key = f"{prefix}{key}" if prefix else key
                if isinstance(value, dict):
                    process_dict(value, f"{full_key}.")
                else:
                    comments[full_key] = self.extract_comment_above(toml_content, key)

        for key, value in data.items():
            if isinstance(value, dict):
                process_dict(value, f"{key}.")

        return data, comments

    def generate_markdown_headings(self, data: Dict[str, Any], comments: Dict[str, str],
                                   level: int = 4, prefix: str = "") -> List[str]:
        """Generate markdown headings from TOML data."""
        lines = []

        for key, value in data.items():
            full_key = f"{prefix}{key}" if prefix else key

            if isinstance(value, dict):
                # Add section heading
                lines.append(f"{'#' * level} {key}")
                lines.append("")
                # Process nested structure
                nested_lines = self.generate_markdown_headings(
                    value, comments, level + 1, f"{full_key}."
                )
                lines.extend(nested_lines)
            else:
                # Add property heading
                lines.append(f"{'#' * level} {key}")
                lines.append("")
                lines.append("- 描述：" + (comments.get(full_key, "")))
                lines.append(f"- 默认值：{value}")
                lines.append("")

        return lines

    def transform_file_content(self, content: str) -> str:
        """Transform markdown content by converting TOML blocks to headings."""

        def replace_toml_block(match: re.Match) -> str:
            toml_content = match.group(1)
            try:
                # Parse TOML and extract comments
                data, comments = self.parse_toml_structure(toml_content)

                # Generate new markdown content
                heading_lines = self.generate_markdown_headings(data, comments)
                return '\n'.join(heading_lines)
            except Exception as e:
                return f"Error processing TOML: {str(e)}"

        # Replace TOML blocks while preserving surrounding content
        return self.toml_block_pattern.sub(replace_toml_block, content)


def process_markdown_file(input_path: str, output_path: str):
    """Process a markdown file and save the transformed content."""
    transformer = MarkdownTomlTransformer()

    try:
        # Read input file
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Transform content
        transformed_content = transformer.transform_file_content(content)

        # Write output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transformed_content)

        print(f"Successfully transformed {input_path} to {output_path}")
    except Exception as e:
        print(f"Error processing file: {str(e)}")


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python script.py input_file.md output_file.md")
        sys.exit(1)

    process_markdown_file(sys.argv[1], sys.argv[2])
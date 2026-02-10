import re
from typing import List

def split_text(text: str, max_length: int = 4096) -> List[str]:
    """Split text into chunks respecting line breaks"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    while len(text) > 0:
        if len(text) <= max_length:
            chunks.append(text)
            break
        
        # Find last newline within limit
        chunk = text[:max_length]
        last_newline = chunk.rfind('\n')
        
        if last_newline != -1:
            chunks.append(text[:last_newline])
            text = text[last_newline + 1:]
        else:
            chunks.append(chunk)
            text = text[max_length:]
    
    return chunks

def sanitize_html(text: str) -> str:
    """Sanitize text for HTML output"""
    # Only allow safe tags
    allowed_tags = {'b', 'i', 'code', 'pre'}
    
    # Remove dangerous tags
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.DOTALL)
    
    # Escape HTML entities
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Restore allowed tags
    for tag in allowed_tags:
        text = text.replace(f'&lt;{tag}&gt;', f'<{tag}>')
        text = text.replace(f'&lt;/{tag}&gt;', f'</{tag}>')
    
    return text

def format_time(seconds: int) -> str:
    """Format seconds to MM:SS"""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"
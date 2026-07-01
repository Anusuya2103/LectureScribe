import re

def detect_tamil(text):
    """Check if text contains Tamil characters"""
    tamil_pattern = re.compile(r'[\u0B80-\u0BFF]')
    return bool(tamil_pattern.search(text))

def extract_english_tamil_mixed(text):
    """
    Identify code-mixed segments
    """
    tokens = text.split()
    tamil_tokens = []
    english_tokens = []
    
    for token in tokens:
        if detect_tamil(token):
            tamil_tokens.append(token)
        else:
            english_tokens.append(token)
    
    return {
        'tamil_segments': ' '.join(tamil_tokens),
        'english_segments': ' '.join(english_tokens),
        'is_mixed': len(tamil_tokens) > 0 and len(english_tokens) > 0
    }
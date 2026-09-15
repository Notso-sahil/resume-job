import re

def extract_stipend(raw_text: str) -> int:
    """
    Returns normalized monthly INR. Returns 0 if unparseable.
    """
    if not raw_text:
        return 0
    
    text = raw_text.lower()
    
    if "unpaid" in text or "not disclosed" in text:
        return 0
        
    # Extract numbers: can be like 25000, 25,000, 25k, 3.6
    # We will try to find patterns
    
    # 1. LPA (Lakhs Per Annum)
    lpa_match = re.search(r'([\d\.]+)\s*lpa', text)
    if lpa_match:
        try:
            lpa_val = float(lpa_match.group(1))
            return int((lpa_val * 100000) / 12)
        except ValueError:
            pass

    # 2. Extract ranges e.g. "20k - 30k" or "20000 - 30000" or just "20k"
    # Find all number blocks
    blocks = re.findall(r'(?:₹|\$)?\s*([\d,\.]+)\s*(k|lpa)?', text)
    if not blocks:
        return 0
        
    is_usd = '$' in text or 'usd' in text
    
    parsed_vals = []
    for num_str, suffix in blocks:
        num_str = num_str.replace(',', '')
        try:
            val = float(num_str)
            if suffix == 'k':
                val *= 1000
            elif suffix == 'lpa':
                continue # handled above
            parsed_vals.append(val)
        except ValueError:
            continue
            
    if not parsed_vals:
        return 0
        
    # Take minimum of range
    min_val = min(parsed_vals)
    
    # Check if annual (if value is very large and not USD, assume annual if > 150000, though this is heuristic)
    # Actually, let's just stick to explicit /year or /month
    if 'year' in text or '/yr' in text or 'annum' in text:
        min_val = min_val / 12
        
    if is_usd:
        min_val = min_val * 84 # Approx exchange rate
        
    return int(min_val)

def is_above_threshold(stipend_inr: int, threshold: int = 20000) -> bool:
    """Returns True if stipend meets minimum threshold."""
    return stipend_inr >= threshold

import re
from attributes import ATTRIBUTE_DATA

def parse_ocr_text(ocr_text: str) -> dict:
    """
    Parses OCR text to find and count valid attributes.
    """
    found_attributes_counts = {}

    # Pre-process OCR text: split into lines for easier parsing for now.
    # More advanced pre-processing can be added later.
    lines = ocr_text.split('\n')

    # Regex to find numbers (integers or decimals, possibly with a '%' sign)
    # It looks for numbers like 12.3, 12, 12.3%, 12%
    # It captures the number part for conversion to float.
    # Adding support for numbers like +12.3% or +12.3
    number_regex = r"([+-]?\d*\.\d+|\d+)\%?"

    for attr_name, valid_values in ATTRIBUTE_DATA.items():
        for line_number, line in enumerate(lines):
            # Basic check if attribute name is in the line
            if attr_name in line:
                # Try to find a number in the same line or subsequent lines
                # This is a simple approach. More sophisticated context-aware parsing might be needed.
                # For now, let's check the current line and the next two lines for a value.
                search_area = line
                if line_number + 1 < len(lines):
                    search_area += " " + lines[line_number+1]
                if line_number + 2 < len(lines):
                    search_area += " " + lines[line_number+2]

                # Find all numbers in the search area
                potential_values = re.findall(number_regex, search_area)

                for val_str in potential_values:
                    try:
                        # Convert extracted string part to float
                        # val_str could be a tuple if regex has multiple capture groups, ensure to get the number
                        num_str = val_str if isinstance(val_str, str) else val_str[0]
                        num_val = float(num_str)

                        if num_val in valid_values:
                            found_attributes_counts[attr_name] = found_attributes_counts.get(attr_name, 0) + 1
                            # Once a valid attribute value is found for this instance of attr_name in the text,
                            # break from searching more numbers for THIS SPECIFIC MENTION of attr_name.
                            # This prevents miscounting if multiple numbers are near one attr_name mention,
                            # but only one is the true value.
                            # Example: "暴击率 8.1% (提升至10%)" - should only count 8.1 if valid.
                            break
                    except ValueError:
                        # Could not convert to float, ignore.
                        continue

    return found_attributes_counts

if __name__ == '__main__':
    # Example Usage for testing
    print("Testing attribute_parser.py...")
    test_ocr_output1 = """
    暴击率 8.1%
    攻击力 300
    百分比攻击 11.6
    固定防御 50.0
    无效属性 99.9
    """
    parsed1 = parse_ocr_text(test_ocr_output1)
    print(f"Test Case 1 (Mixed valid and invalid):\n{test_ocr_output1}\nParsed: {parsed1}\n")

    test_ocr_output2 = """
    暴击率: 6.3%
    暴击伤害: 12.6%
    百分比攻击: 10.1%
    暴击率 +7.5%
    """
    # Expected: 暴击率: 2 (6.3 and 7.5 are valid), 暴击伤害: 1, 百分比攻击: 1
    parsed2 = parse_ocr_text(test_ocr_output2)
    print(f"Test Case 2 (Multiple valid, different formats):\n{test_ocr_output2}\nParsed: {parsed2}\n")

    test_ocr_output3 = "这是一段没有属性的文字。"
    parsed3 = parse_ocr_text(test_ocr_output3)
    print(f"Test Case 3 (No attributes):\n{test_ocr_output3}\nParsed: {parsed3}\n")

    test_ocr_output4 = "固定攻击+40" # Common OCR output for fixed attack
    parsed4 = parse_ocr_text(test_ocr_output4)
    print(f"Test Case 4 (Fixed attack with '+'):\n{test_ocr_output4}\nParsed: {parsed4}\n")

    test_ocr_output5 = "百分比生命6.4%   百分比防御8.1%"
    parsed5 = parse_ocr_text(test_ocr_output5)
    print(f"Test Case 5 (Attributes on same line):\n{test_ocr_output5}\nParsed: {parsed5}\n")

    # Test with values that are close but not exact
    test_ocr_output6 = "暴击率 8.2%" # 8.2 is not in ATTRIBUTE_DATA for 暴击率
    parsed6 = parse_ocr_text(test_ocr_output6)
    print(f"Test Case 6 (Value not in predefined set):\n{test_ocr_output6}\nParsed: {parsed6}\n")

    test_ocr_output7 = """
    主属性: 暴击伤害
    副属性:
    暴击率 6.3%
    百分比攻击 7.1%
    固定攻击 30
    固定防御 70.0
    """
    parsed7 = parse_ocr_text(test_ocr_output7)
    print(f"Test Case 7 (Typical layout):\n{test_ocr_output7}\nParsed: {parsed7}\n")

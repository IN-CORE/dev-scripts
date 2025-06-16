
# this script will generate a new XML content with the same content as the original XML
# but with the duplicated values that has <MinScaleDenominator> and <Size> tags
# The main purpose for this script is to make the style dynamically change by the map scale
# So the point size will be bigger when the map zoomed in and smaller when the map zoomed out

############# Pre-requisite #############
# paste the style xml to the given location
# the original XML must have <MaxScaleDenominator>20000</MaxScaleDenominator> tag
# or <sld:MaxScaleDenominator>20000</sld:MaxScaleDenominator> tag
# or <se:MaxScaleDenominator>20000</se:MaxScaleDenominator> tag
# also, there must be <sld:size> or <se:size> or <size> tag

# if the original XML doesn't have <MaxScaleDenominator> tag, please add it manually
# right before <PointSymbolizer> tag
# size tag should be manually added if it is not there
# also, is_sld, is_no_tag, and is_se variable must be checked and set correctly
###########################################

from bs4 import BeautifulSoup
import pyperclip
import copy

# if tags are like <sld: then is_sld is True
is_no_tag = False
is_sld = False
is_se = True

# XML content
xml_content = """
<paste xml in here>
"""

if is_sld:
    rule_tag = 'sld:Rule'
    max_scale_denominator_tag = 'sld:MaxScaleDenominator'
    min_scale_denominator_tag = 'sld:MinScaleDenominator'
    name_tag = 'sld:Name'
    size_tag = 'sld:Size'
    point_symbolizer_tag = 'sld:PointSymbolizer'
if is_no_tag:
    rule_tag = 'Rule'
    max_scale_denominator_tag = 'MaxScaleDenominator'
    min_scale_denominator_tag = 'MinScaleDenominator'
    name_tag = 'Name'
    size_tag = 'Size'
    point_symbolizer_tag = 'PointSymbolizer'
if is_se:
    rule_tag = 'se:Rule'
    max_scale_denominator_tag = 'se:MaxScaleDenominator'
    min_scale_denominator_tag = 'se:MinScaleDenominator'
    name_tag = 'se:Name'
    size_tag = 'se:Size'
    point_symbolizer_tag = 'se:PointSymbolizer'

# Parse XML
soup = BeautifulSoup(xml_content, 'xml')

# Remove existing XML declaration
for declaration in soup.find_all(string=lambda text: isinstance(text, str) and '<?xml' in text):
    declaration.extract()

# Find all <sld:Rule> tags
rules = soup.find_all(rule_tag)

# # Remove empty <sld:Rule> tags
# for rule in rules:
#     if not rule.find():
#         rule.extract()

# Duplicate and modify each rule
for rule in rules:
    print(rule.contents[1])
    # Create a new rule element
    new_rule = soup.new_tag(rule_tag)

    # Copy the contents of the original rule into the new rule
    # need to copy the rule to tmp_rule to avoid the rule becomes empty
    tmp_rule = copy.copy(rule)
    for child in tmp_rule.children:
        if child is not None and child.name is not None:
            new_rule.append(child)

    print(new_rule.contents[0])

    # Modify conditions
    max_scale_denominator = rule.find(max_scale_denominator_tag)
    if max_scale_denominator:
        max_scale_denominator.string = '20000'

    # convert MaxScaleDenominator to MinScaleDenominator in new_rule
    min_scale_denominator = new_rule.find(max_scale_denominator_tag)
    if min_scale_denominator:
        min_scale_denominator.name = 'MinScaleDenominator'  # Change the tag name
        min_scale_denominator.string = '20000'  # Change the value

    name = new_rule.find(name_tag)
    if name:
        name.string = name.string + "1"

    big_size = rule.find(size_tag)
    if big_size:
        if is_sld:
            big_size.string = '12'
        else:
            big_size.string = '12'

    small_size = new_rule.find(size_tag)
    if small_size:
        if is_sld:
            small_size.string = '6'
        else:
            small_size.string = '6'

    # Insert the modified rule immediately after the original one
    if new_rule.find():
        rule.insert_after(new_rule)

    # Modify original rule
    original_max_scale_denominator = rule.find(max_scale_denominator_tag)
    if original_max_scale_denominator:
        original_max_scale_denominator.string = '20000'

# Remove any empty <sld:Rule> tags that may have been generated
for rule in soup.find_all('sld:Rule'):
    if not rule.find():
        rule.extract()

# remove the very first line of the XML because it is not needed
soup.contents[0].extract()

# Convert the modified XML to string
modified_xml = soup.prettify()

# Copy the modified XML content to the system clipboard
pyperclip.copy(modified_xml)

# Inform the user that the content has been copied to the clipboard
print("Modified XML content has been copied to the clipboard.")

import json
import xml.etree.ElementTree as ET
from collections import OrderedDict
import os

def extract_cv_details(xml_file):
    """Parses an XML CV file and extracts relevant details.

    Args:
        xml_file: The path to the XML file containing the CV data.

    Returns:
        An OrderedDict containing:
            * right_to_work: Right to work status (e.g., "Yes").
            * highest_education_level: The highest education level obtained (Ph.D., Master's, Bachelor's, High School, Primary).
            * years_of_experience: Total years of experience calculated from work history.
    """
    # Define the JSON filename
    json_file = 'ipfs_details.json'

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Right to work
    right_to_work = root.find('right_to_work').text

    # Education
    education_levels = []
    for education_item in root.findall('education'):
        degree = education_item.find('degree').text if education_item.find('degree') is not None else None
        education_levels.append(degree)

    # Determine the highest education level
    highest_education_level = None
    education_order = ['Ph.D.', 'Master', 'Bachelor', 'High School', 'Primary']
    for edu_level in education_order:
        if any(edu_level.lower() in level.lower() for level in education_levels):
            highest_education_level = edu_level
            break

    # Experience (assuming simple calculation based on dates)
    years_of_experience = 0
    for experience_item in root.findall('experience'):
        dates = experience_item.find('dates').text
        start_year, end_year = map(int, dates.split('-'))
        years_of_experience += (end_year - start_year + 1)

    # Check if the JSON file already exists
    if os.path.exists(json_file):
        # Load existing JSON data
        with open(json_file, 'r') as f:
            existing_data = json.load(f, object_pairs_hook=OrderedDict)
    else:
        existing_data = OrderedDict()

    # Update existing data with new extracted values
    existing_data['right_to_work'] = right_to_work
    existing_data['highest_education_level'] = highest_education_level
    existing_data['years_of_experience'] = years_of_experience

    # Write the updated JSON data back to the same file
    with open(json_file, 'w') as f:
        json.dump(existing_data, f, indent=4)

    return existing_data



import xml.etree.ElementTree as ET
from collections import OrderedDict

def extract_cv_details(xml_file):
    """Parses an XML CV file and extracts relevant details.

    Args:
        xml_file: The path to the XML file containing the CV data.

    Returns:
        An OrderedDict containing:
            * right_to_work: Right to work status (e.g., "Yes").
            * education_levels: A list of education details, where each item is a dict with:
                * institution: Name of the educational institution.
                * degree: The degree obtained (if available).
                * graduation_year: The year of graduation.
            * years_of_experience: Total years of experience calculated from work history.
    """

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Right to work
    right_to_work = root.find('right_to_work').text

    # Education
    education_levels = []
    for education_item in root.findall('education'):
        education_details = OrderedDict()
        education_details['institution'] = education_item.find('institution').text
        degree = education_item.find('degree')
        education_details['degree'] = degree.text if degree is not None else None
        education_details['graduation_year'] = education_item.find('graduation_year').text
        education_levels.append(education_details)

    # Experience (assuming simple calculation based on dates)
    years_of_experience = 0
    for experience_item in root.findall('experience'):
        dates = experience_item.find('dates').text
        start_year, end_year = map(int, dates.split('-'))
        years_of_experience += (end_year - start_year + 1)

    return OrderedDict([
        ('right_to_work', right_to_work),
        ('education_levels', education_levels),
        ('years_of_experience', years_of_experience)
    ])

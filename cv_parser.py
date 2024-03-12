import xml.etree.ElementTree as ET
class CVParser:
    def extract_info_from_cv(self, decrypted_cv):
        root = ET.fromstring(decrypted_cv)

        # Right to work
        right_to_work = root.find('right_to_work').text.strip()

        # Education level
        highest_degree = None
        degrees = ["Bachelor", "Master", "PhD"]
        for institution in root.iter('institution'):
            degree_tag = institution.find('degree')
            if degree_tag is not None and degree_tag.text.strip() in degrees:
                highest_degree = degree_tag.text.strip()
                break 

        # Years of experience 
        experience_pattern = r'\d{4}\s*-\s*\d{4}|\d{4}\s*-\s*Present'
        total_years = 0
        for experience in root.iter('dates'):
            match = re.search(experience_pattern, experience.text.strip())
            if match:
                years_range = match.group(0).split('-')
                start_year = int(years_range[0])
                end_year = int(years_range[1]) if years_range[1] != 'Present' else 2024
                total_years += end_year - start_year

        return right_to_work, highest_degree, total_years

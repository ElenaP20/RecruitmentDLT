import xml.etree.ElementTree as ET
import json

PRIMARY_EDUCATION_SCORE = 0
HIGH_SCHOOL_SCORE = 5
BACHELOR_DEGREE_SCORE = 10
MASTERS_DEGREE_SCORE = 15
DOCTORATE_SCORE = 20

class CVProcessor:
    def __init__(self, xml_files, ipfs_data_file):
        self.xml_files = xml_files  # List of XML files to process
        self.ipfs_data_file = ipfs_data_file

    def evaluate_criteria(self, higher_ed, years_exp, right_to_work):
        education_level = higher_ed.lower()
        education_level_score = self.get_education_level_score(education_level)
        return education_level_score, years_exp, 1 if right_to_work else 0

    def calculate_score(self, education_level, years_exp, right_to_work):
        score = education_level + years_exp + right_to_work
        return score

    def get_education_level_score(self, education_level):
        education_level = education_level.lower()
        if "primary" in education_level:
            return PRIMARY_EDUCATION_SCORE
        elif "high school" in education_level:
            return HIGH_SCHOOL_SCORE
        elif "bachelor" in education_level:
            return BACHELOR_DEGREE_SCORE
        elif "master" in education_level:
            return MASTERS_DEGREE_SCORE
        elif "doctorate" in education_level or "ph.d." in education_level:
            return DOCTORATE_SCORE
        else:
            raise ValueError("Invalid education level")

    def extract_cv_details(self):
        for xml_file in self.xml_files:
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()

                right_to_work = root.find('right_to_work').text

                education_levels = []
                for education_item in root.findall('education'):
                    degree = education_item.find('degree').text if education_item.find('degree') is not None else None
                    education_levels.append(degree)

                highest_education_level = None
                education_order = ['Ph.D.', 'Master', 'Bachelor', 'High School', 'Primary']
                for edu_level in education_order:
                    if any(edu_level.lower() in level.lower() for level in education_levels):
                        highest_education_level = edu_level
                        break

                years_of_experience = 0
                for experience_item in root.findall('experience'):
                    dates = experience_item.find('dates').text
                    start_year, end_year = map(str.strip, dates.split('-'))
                    if end_year.lower() == 'present':
                        end_year = str(2022)  # Assuming 2022 as the current year
                    years_of_experience += (int(end_year) - int(start_year) + 1)

                # Evaluate criteria
                education_level_score, years_exp, right_to_work_score = self.evaluate_criteria(
                    highest_education_level, years_of_experience, right_to_work == "Yes"
                )

                # Calculate total score
                total_score = self.calculate_score(education_level_score, years_exp, right_to_work_score)

                # Store only the total score in the extracted data
                extracted_data = {"total_score": total_score}

                # Read existing IPFS data
                with open(self.ipfs_data_file, 'r') as f:
                    existing_data = json.load(f)

                # Update the total score for the corresponding IPFS link's second part
                for token_data in existing_data.get("tokens", []):
                    if token_data.get("secondPart") == xml_file:
                        token_data["total_score"] = total_score
                        break

                # Write the updated data back
                with open(self.ipfs_data_file, 'w') as f:
                    json.dump(existing_data, f, indent=4)

                print("Total score appended to the existing IPFS data for:", xml_file)
                return total_score

            except Exception as e:
                print("Error processing", xml_file + ":", str(e))
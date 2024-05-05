import json
import re
import spacy
from pdfminer.high_level import extract_text
import os
from spacy.matcher import Matcher
from docx import Document
from spacy.pipeline import EntityRuler
from pyresparser.resume_parser import ResumeParser
import pandas as pd
from spacy.language import Language
import spacy
from spacy.pipeline.entityruler import EntityRuler

os.chdir(r'E:\frelancer\parser_v2')

nlp = spacy.load('en_core_web_sm')
ruler = EntityRuler(nlp)
patterns = [
    # Patterns for names
    {"label": "PERSON", "pattern": [{"POS": "PROPN"}, {"POS": "PROPN"}]},
    {"label": "PERSON", "pattern": [{"POS": "PROPN"}, {"POS": "PROPN"}, {"POS": "PROPN"}]},
    {"label": "PERSON", "pattern": [{"POS": "PROPN"}, {"POS": "PROPN"}, {"POS": "PROPN"}, {"POS": "PROPN"}]},

    # Patterns for locations
    {"label": "GPE", "pattern": [{"ORTH": "Pune"}, {"ORTH": "Maharashtra"}]},
    {"label": "GPE", "pattern": [{"ORTH": "Ahmedabad"}, {"ORTH": "382350"}]},
    {"label": "GPE", "pattern": [{"ORTH": "Sirohi"}, {"ORTH": "307001"}, {"ORTH": "Rajasthan"}, {"ORTH": "India"}]},
    {"label": "ADDRESS", "pattern": [{"SHAPE": "d/d"}, {"ORTH": "Main"}, {"ORTH": "St"}, {"ORTH": ","}, {"ORTH": "Apt"}, {"SHAPE": "d"}, {"ORTH": ","}, {"ORTH": "New"}, {"ORTH": "York"}, {"ORTH": ","}, {"ORTH": "NY"}, {"ORTH": ","}, {"SHAPE": "ddddd"}]},  # Apt number, street, city, state, zip
    {"label": "ADDRESS", "pattern": [{"SHAPE": "d"}, {"ORTH": "Main"}, {"ORTH": "St"}, {"ORTH": ","}, {"ORTH": "San"}, {"ORTH": "Francisco"}, {"ORTH": ","}, {"ORTH": "CA"}, {"ORTH": ","}, {"SHAPE": "ddddd"}]},  # Street, city, state, zip
    {"label": "ADDRESS", "pattern": [{"ORTH": "San"}, {"ORTH": "Francisco"}, {"ORTH": ","}, {"ORTH": "CA"}, {"ORTH": ","}, {"SHAPE": "ddddd"}]},  # City, state, zip
    {"label": "GPE", "pattern": [{"ORTH": "Mumbai"}, {"ORTH": "Maharashtra"}]},
    {"label": "GPE", "pattern": [{"ORTH": "Bengaluru"}, {"ORTH": "Karnataka"}]},
    {"label": "GPE", "pattern": [{"ORTH": "New"}, {"ORTH": "Delhi"}]},
    {"label": "GPE", "pattern": [{"ORTH": "Chennai"}, {"ORTH": "Tamil"}, {"ORTH": "Nadu"}]},
    {"label": "GPE", "pattern": [{"ORTH": "Kolkata"}, {"ORTH": "West"}, {"ORTH": "Bengal"}]},
    {"label": "GPE", "pattern": [{"ORTH": "Hyderabad"}, {"ORTH": "Telangana"}]},
    {"label": "GPE", "pattern": [{"ORTH": "Jaipur"}, {"ORTH": "Rajasthan"}]},
    {"label": "GPE", "pattern": [{"ORTH": "Lucknow"}, {"ORTH": "Uttar"}, {"ORTH": "Pradesh"}]},
    {"label": "GPE", "pattern": [{"ORTH": "Surat"}, {"ORTH": "Gujarat"}]},
    {"label": "GPE", "pattern": [{"ORTH": "Pune"}]},
    {"label": "GPE", "pattern": [{"ORTH": "560001"}]},

    # Patterns for skills
    {"label": "SKILL", "pattern": [{"LOWER": "java"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "selenium"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "api"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "sql"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "testng"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "maven"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "rest"}, {"LOWER": "assured"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "postman"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "jira"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "cucumber"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "agile"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "bdd"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "unix"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "github"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "gis"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "crm"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "html"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "css"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "bootstrap"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "javascript"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "react"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "redux"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "angularjs"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "jquery"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "ajax"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "json"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "nodejs"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "express"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "webpack"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "jest"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "gulp"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "jenkins"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "azure"}, {"LOWER": "devops"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "agile"}]}
]

patterns += [
    {"label": "GPE", "pattern": [{"ORTH": "Wankaner"}]},
    {"label": "ORG", "pattern": [{"ORTH": "MAZDA"}, {"ORTH": "CONSULTANCY"}, {"ORTH": "PVT."}, {"ORTH": "LTD."}]},
    {"label": "ORG", "pattern": [{"ORTH": "SIMMS"}, {"ORTH": "ENGINEERING"}, {"ORTH": "PVT."}, {"ORTH": "LTD."}]},
    {"label": "ORG", "pattern": [{"ORTH": "Paschim"}, {"ORTH": "Gujarat"}, {"ORTH": "Vij"}, {"ORTH": "Company"}, {"ORTH": "Limited"}, {"ORTH": "(PGVCL)"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "laravel"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "vue"}, {"ORTH": "Js"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "angular"}, {"ORTH": "JS"}]},
    {"label": "SKILL", "pattern": [{"LOWER": "rest"}, {"ORTH": "Api"}]}
]
patterns += [
    # Common first name and last name patterns
    {"label": "PERSON", "pattern": [{"ORTH": "John"}, {"ORTH": "Doe"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Jane"}, {"ORTH": "Doe"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Michael"}, {"ORTH": "Smith"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Maria"}, {"ORTH": "Garcia"}]},

    # First name, middle initial, and last name patterns
    {"label": "PERSON", "pattern": [{"ORTH": "John"}, {"ORTH": "A."}, {"ORTH": "Doe"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Jane"}, {"ORTH": "B."}, {"ORTH": "Doe"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Michael"}, {"ORTH": "C."}, {"ORTH": "Smith"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Maria"}, {"ORTH": "D."}, {"ORTH": "Garcia"}]},

    # Titles and names
    {"label": "PERSON", "pattern": [{"ORTH": "Dr."}, {"ORTH": "John"}, {"ORTH": "Doe"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Professor"}, {"ORTH": "Jane"}, {"ORTH": "Doe"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Mr."}, {"ORTH": "Michael"}, {"ORTH": "Smith"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Ms."}, {"ORTH": "Maria"}, {"ORTH": "Garcia"}]},

    # Common suffixes
    {"label": "PERSON", "pattern": [{"ORTH": "John"}, {"ORTH": "Doe"}, {"ORTH": "Jr."}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Jane"}, {"ORTH": "Doe"}, {"ORTH": "PhD"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Michael"}, {"ORTH": "Smith"}, {"ORTH": "III"}]},
    {"label": "PERSON", "pattern": [{"ORTH": "Maria"}, {"ORTH": "Garcia"}, {"ORTH": "Esq."}]}
]

ruler.add_patterns(patterns)

nlp.add_pipe("entity_ruler")

def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])
def parse_resume(text):
    resume_info = {}
    doc = nlp(text)

    name_patterns = [
        #r'(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)',  # First name and Last name
        #r'(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)',  # First name, Middle name, and Last name
        #r'(\b[A-Z][a-z]+\b)\s(\b[A-Z]\.\b)\s(\b[A-Z][a-z]+\b)',  # First name, Middle initial, and Last name
        #r'(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)',
        # First name, Middle name, Second Middle name, and Last name
        #r'(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)-(\b[A-Z][a-z]+\b)',  # First name and Hyphenated Last name
        #r'(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b)-(\b[A-Z][a-z]+\b)',
        # First name, Middle name, and Hyphenated Last name
        #r'(\b[A-Z][a-z]+\b)\s(\b[A-Z]\.\b)\s(\b[A-Z]\.\b)\s(\b[A-Z][a-z]+\b)',
        # First name, Two Middle initials, and Last name
        #r'(\b[A-Z][a-z]+\b)\s(\b[A-Z][a-z]+\b),\s(\b[A-Z][a-z]+\b)',  # Last name, First name, and Middle name
    ]
    phone_patterns = [
        r'\(?(\d{3})\)?[-\s]?(\d{3})[-\s]?(\d{4})',
        r'\+?(\d{2})\s+(\d{2})\s+(\d{4})\s+(\d{4})',
        r'(\d{10})',
        r'Mobile\s?:\s?(\d{5}\s\d{5})',
    ]
    email_patterns = [
        r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',
    ]
    skill_patterns = [
        r'SKILLS:(.*?)(?:EXPERIENCE|EDUCATION|LANGUAGES|$)',
        r'Skills:(.*?)(?:Experience|Education|Languages|$)',
        r'Key Strengths :(.*?)(?:Working knowledge)',
    ]
    location_patterns = [
        r'\b\d{1,5}\s(?:[A-Za-z0-9#]+\s){0,4}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Boulevard|Blvd|Drive|Dr|Court|Ct|Circle|Cir|Square|Sq|Terrace|Ter|Place|Pl|Parkway|Pkwy|Way)\b',
        r'\b(?:[A-Za-z0-9#]+\s){1,4}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Boulevard|Blvd|Drive|Dr|Court|Ct|Circle|Cir|Square|Sq|Terrace|Ter|Place|Pl|Parkway|Pkwy|Way)\s\d{1,5}\b',
        r'\b\d{1,5}\s(?:[A-Za-z0-9#]+\s){0,4}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Boulevard|Blvd|Drive|Dr|Court|Ct|Circle|Cir|Square|Sq|Terrace|Ter|Place|Pl|Parkway|Pkwy|Way),\s[A-Za-z]+,\s[A-Za-z]{2}\s\d{5}\b',
        r'\b[A-Za-z]+\s\d{1,5},\s(?:[A-Za-z0-9#]+\s){0,4}(?:Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Boulevard|Blvd|Drive|Dr|Court|Ct|Circle|Cir|Square|Sq|Terrace|Ter|Place|Pl|Parkway|Pkwy|Way),\s[A-Za-z]+,\s[A-Za-z]{2}\s\d{5}\b'
    ]

    location_patterns += [
        r'\b(?:United States|USA|U\.S\.A\.|Canada|Australia|United Kingdom|UK|U\.K\.|Germany|France|Italy|Spain|India|China|Japan|Brazil|Mexico|Russia)\b',
        r'\b(?:Austria|Belgium|Denmark|Finland|Greece|Ireland|Netherlands|Norway|Poland|Portugal|Sweden|Switzerland|Turkey|New Zealand|South Africa|South Korea)\b'
    ]

    skills_df = pd.read_csv('skills.csv', on_bad_lines='skip')
    predefined_skills = skills_df['SKILLS'].str.lower().str.strip().tolist()

    for pattern in name_patterns:
            name_match = re.search(pattern, text)
            if name_match:
                resume_info['Name'] = name_match.group().strip()
                break

    email, phone = None, None
    for pattern in email_patterns:
        email_match = re.search(pattern, text)
        if email_match:
            email = email_match.group()
            resume_info['Email'] = email.strip()
            break

    for pattern in phone_patterns:
        phone_match = re.search(pattern, text)
        if phone_match:
            phone = '-'.join(phone_match.groups())
            resume_info['Phone'] = phone.strip()
            break

    skills_extracted = False
    for pattern in skill_patterns:
        skills_match = re.findall(pattern, text, re.IGNORECASE)
        if skills_match:
            extracted_skills = [skill.strip() for skill in skills_match if not skill.strip().isdigit()]
            resume_info['Skills'] = list(set(extracted_skills))
            skills_extracted = True
            break

    if not skills_extracted:
        extracted_skills = [token.text.lower() for token in doc if
                            token.text.lower() in predefined_skills and token.is_alpha and len(token.text) > 1]
        resume_info['Skills'] = list(set(extracted_skills))[:10]

    for pattern in location_patterns:
        location_match = re.search(pattern, text)
        if location_match:
            resume_info['Location'] = location_match.group().strip().replace('\n', ' ')
            break

    if email or phone:
        name = None
        matcher = Matcher(nlp.vocab)
        matcher.add("PERSON", [[{"ENT_TYPE": "PERSON"}]])
        matches = matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]  # The matched span
            start_char, end_char = span.start_char, span.end_char
            email_start = text.find(email) if email is not None else -1
            phone_start = text.find(phone) if phone is not None else -1

            # Check if the matched span is close to the email or phone
            if email and (abs(start_char - email_start) < 10 or abs(end_char - email_start) < 10):
                name = span.text
                break
            elif phone and (abs(start_char - phone_start) < 10 or abs(end_char - phone_start) < 10):
                name = span.text
                break


        if name:
            resume_info['Name'] = name.strip()

    for ent in doc.ents:
        if ent.label_ == 'PERSON' and 'Name' not in resume_info:
            resume_info['Name'] = ent.text
        elif ent.label_ == 'PHONE' and 'Number' not in resume_info:
            resume_info['Number'] = ent.text
        elif ent.label_ == 'EMAIL' and 'Email' not in resume_info:
            resume_info['Email'] = ent.text
        elif (ent.label_ == 'GPE' or ent.label_ == 'LOC') and 'Location' not in resume_info:
            resume_info['Location'] = ent.text

    return resume_info


def process_resumes(folder_path):
    resumes_data = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.pdf'):
            extracted_text = extract_text_from_pdf(file_path)
        elif filename.endswith('.docx'):
            extracted_text = extract_text_from_docx(file_path)
        else:
            continue

        resume_data = parse_resume(extracted_text)
        if 'Name' in resume_data:
            resume_data['Name'] = resume_data['Name'].replace('\n', ' ').strip()
        if 'Location' in resume_data:
            resume_data['Location'] = resume_data['Location'].replace('\n', ' ').strip()
        resumes_data.append(resume_data)

    with open('all_resumes_data.json', 'w') as jsonfile:
        json.dump(resumes_data, jsonfile, indent=2)

    print(f"Processed {len(resumes_data)} resumes. Data saved to all_resumes_data.json")

def process_resume1(folder_path):
    resumes_data = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(('.pdf', '.docx', '.txt')):
            resume_data = ResumeParser(file_path).get_extracted_data()
            for field in ['college_name', 'degree', 'designation', 'experience', 'company_names', 'no_of_pages']:
                resume_data.pop(field, None)
            resumes_data.append(resume_data)

    with open('all_resumes_data.json', 'w') as jsonfile:
        json.dump(resumes_data, jsonfile, indent=2)

    print(f"Processed {len(resumes_data)} resumes. Data saved to all_resumes_data.json")


def is_valid_name(name):
    pattern = re.compile(r'^[A-Z][a-z]+(?: [A-Z][a-z]+)*$')
    return bool(pattern.match(name))


def process_resumes_combined(folder_path):
    resumes_data = []

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(('.pdf', '.docx', '.txt')):
            extracted_text = extract_text_from_pdf(file_path) if filename.endswith('.pdf') else extract_text_from_docx(file_path)
            resume_data_1 = parse_resume(extracted_text)

            # Use the second parser
            #resume_data_2 = ResumeParser(file_path).get_extracted_data()

            # Combine the results, prioritizing valid names from either parser
            final_resume_data = {}
            resume_data_2 = {}

            # Update final_data with Location, Email, and Phone from resume_data_1
            if resume_data_1:
                for field in ['Name', 'Email', 'Number', 'Skills', 'Location']:
                    if field in resume_data_1:
                        final_resume_data[field] = resume_data_1[field]



            # Update final_data with Skills and Total Experience from resume_data_2
            if 'skills' in resume_data_2:
                final_resume_data['Skills'] = resume_data_2['skills']
            if 'total_experience' in resume_data_2:
                final_resume_data['Total Experience'] = resume_data_2['total_experience']

            resumes_data.append(final_resume_data)

    with open('all_resumes_data_combined.json', 'w') as jsonfile:
        json.dump(resumes_data, jsonfile, indent=2)

    print(f"Processed {len(resumes_data)} resumes. Data saved to all_resumes_data_combined.json")

if __name__ == "__main__":
    process_resumes_combined('resume')




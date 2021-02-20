'''
Parses json object
'''

import json
from typing import Dict
import jmespath


def parse_kved(class_code: str) -> str:
    '''
    Parses json file backwards (gets from the lowest value path to the highest)
    and writes it into new json file

    >>> parse_kved('01.15')
    'kved_results.json'
    '''

    with open('kved.json') as json_file:
        kved_json = json.load(json_file)

    # gets_info about class
    class_name = jmespath.search(
        f"sections[][].divisions[].groups[].classes[?classCode=='{class_code}'].className[]",
        kved_json)[0]

    # gets info about group
    group = jmespath.search(
        f"sections[][].divisions[].groups[?groupCode=='{class_code[:-1]}'][]",
        kved_json)[0]
    group_name, group_num_children = group['groupName'], len(group['classes'])

    # gets info about division
    division_code = class_code[:-3]
    division = jmespath.search(
        f"sections[][].divisions[?divisionCode=='{division_code}'][]",
        kved_json)[0]
    division_name, division_num_children = division['divisionName'], len(division['groups'])

    # maps division codes with section codes
    sections_codes = jmespath.search("sections[0][*].sectionCode", kved_json)
    divisions_codes = jmespath.search("sections[0][*].divisions[*].divisionCode", kved_json)
    map_lst = {section_code: division_code for
                section_code, division_code in zip(sections_codes, divisions_codes)}
    user_section_code = ''
    for section_code in map_lst:
        if division_code in map_lst[section_code]:
            user_section_code = section_code
            break

    # gets info about section
    section = jmespath.search(f"sections[0][?sectionCode=='{user_section_code}']", kved_json)[0]
    section_name, section_num_children = section['sectionName'], len(section['divisions'])

    data = {
        "class_name": class_name,
        "group_name": group_name,
        "group_num_children": group_num_children,
        "division_name": division_name,
        "division_num_children": division_num_children,
        "section_name": section_name,
        "section_num_children": section_num_children
    }

    return create_new_json_file(data)


def create_new_json_file(data: Dict[str, str], path_to_file: str='kved_results.json') -> str:
    '''
    Creates a new json file from given dict and writes it into file.
    '''

    # creates new json object
    new_json_object = {
        "name": data['class_name'],
        "type": "class",
        "parent": {
            "name": data['group_name'],
            "type": "group",
            "num_children": data['group_num_children'],
            "parent": {
                "name": data['division_name'],
                "type": "division",
                "num_children": data['division_num_children'],
                "parent": {
                    "name": data['section_name'],
                    "type": "section",
                    "num_children": data['section_num_children']
                }
            }
        }
    }

    with open(path_to_file, 'w') as outfile:
        json.dump(new_json_object, outfile, indent=4, ensure_ascii=False)

    return path_to_file

'''
    Read the README.md to get more information about this script.
'''
# Native modules
import os
import sys
import getpass
import json
import csv

import ftfy
import pandas

# Self made modules
from db import WCA_Database
from wca_api import get_registrations_from_wcif, wca_registration, get_wca_info, create_competition_folder
from wca_db import get_results_from_wca_export

# Hard coded competition name, because script will only be used for FMC Europe XY
competition_name = "FMCEurope2019"
competition_name_stripped = competition_name.strip()

registered_locations = list(csv.reader(open('locations.txt', 'r'), delimiter='\t'))

# WCA login data (if not stored in static/config.py)
wca_password, wca_mail = wca_registration(True)

create_competition_folder(competition_name)

# Use WCA login data to talk to WCA API and get competition information (WCIF)
competition_wcif_file = get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped)
wca_json = json.loads(competition_wcif_file)

# Get all countries from WCA export
countries = WCA_Database.query("SELECT * FROM Countries").fetchall()

# Get competitor list with registration information from WCIF
competitor_information_wca, wca_ids = get_registrations_from_wcif(wca_json, countries)

# Add results for each competitor from WCA export
competitor_information_wca = get_results_from_wca_export(wca_ids, competitor_information_wca)
competitor_information_wca = sorted(sorted(sorted(competitor_information_wca, key=lambda x:x['name']), key=lambda x:x['single'] if x['single'] > 0 else 100), key=lambda x:x['average'] if x['average'] > 0 else 100)

# Group competitors by registered location (information given by registration information)
competitors_per_location = {}
for competitor in competitor_information_wca:
    found_location = False
    for locations in registered_locations:
        # Hack to replace location name to avoid renaming this location for all relevant registrations
        competitor['comments'] = competitor['comments'].replace(ftfy.fix_text('Stork\u00f8benhavn'), ftfy.fix_text('Måløv'))
        
        competitor['comments'] = competitor['comments'].replace(ftfy.fix_text('East Midlands'), ftfy.fix_text('Ely'))
        
        competitor['comments'] = competitor['comments'].replace(ftfy.fix_text('Gothenburg'), ftfy.fix_text('Lerum'))
        
        if ftfy.fix_text(competitor['comments']) == ftfy.fix_text(locations[1]):
            competitor['comments'] = locations[0] + ' - ' + competitor['comments']
            found_location = True
            break

    if not found_location:
        competitor['comments'] = 'unknown location - ' + competitor['comments']
    if competitor['comments'] not in competitors_per_location:
        competitors_per_location.update({competitor['comments']: []})
    competitors_per_location[competitor['comments']].append(competitor)

# Collect mail addresses of each competitor and group by location
emails = {}
for location in competitors_per_location:
    competitors_per_location[location] = sorted(sorted(sorted(competitors_per_location[location], key=lambda x:x['name']), key=lambda x:x['single'] if x['single'] > 0 else 100), key=lambda x:x['average'] if x['average'] > 0 else 100)

    for competitor in competitors_per_location[location]:
        if competitor['comments'] not in emails:
            emails.update({competitor['comments']: []})
        emails[competitor['comments']].append(competitor['mail'])

competitor_list = []
for competitor in competitor_information_wca:
    competitor_list.append(competitor)

competitor_list = sorted(competitor_list, key=lambda x:x['comments'])

for competitor in competitor_list:
    print(competitor['name'] + ',' + competitor['comments'] + ',' + competitor['country'] + ',' + competitor['dob'] + ',' + competitor['mail'] + ',' +  competitor['guests'])

competitors_per_location_extended = competitors_per_location

secret_information = ['dob', 'gender', 'mail', 'role', 'guests']
for location in competitors_per_location:
    for competitor in competitors_per_location[location]:
        for key in secret_information:
            del competitor[key]

### Write results to files
# Public registration information
output_registration = competition_name + '/competitors'
with open(output_registration + '.json', 'w') as registration_file:
    print(json.dumps(competitor_information_wca, indent=4), file=registration_file)

output_registration += 'Locations'
with open(output_registration + '.json', 'w') as registration_file:
    print(json.dumps(competitors_per_location, indent=4), file=registration_file)

# All registration information (for orga and delegates only)
output_registration += 'Extended'
with open(output_registration + '.json', 'w') as registration_file:
    print(json.dumps(competitors_per_location_extended, indent=4), file=registration_file)

output_json = json.dumps(competitors_per_location_extended, indent=4)
with open(output_registration + '2.json', 'w') as registration_file:
    print(output_json, file=registration_file)

# Output on terminal
'''
print('Locations:')
for location in competitors_per_location:
    table = pandas.DataFrame(data=competitors_per_location[location])
    table = table.fillna(' ')
    
    table = table[['personId', 'name', 'country', 'single', 'average']]
    print(location)
    print(table)
    print('')

print('')
print('All registrations:')
table = pandas.DataFrame(data=competitor_information_wca)
table = table.fillna(' ')
table = table[['personId', 'name', 'country', 'single', 'average', 'comments']]
table.columns = ['WCA ID', 'Name', 'Country', 'Single', 'Mean', 'Location']
print(table)
'''

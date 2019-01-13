### Data extraction of WCIF and registration file (if used).
import os
import sys
import requests
import json
import getpass

from static import config as credentials

### WCA WCIF
# Get competitor information: name, WCA ID, date of birth, gender, country, competition roles (organizer, delegate) and events registered for
def get_registrations_from_wcif(wca_json, countries):
    registration_id = 1
    competitor_information_wca = []
    wca_ids = ()
    for registrations in wca_json['persons']:
        registered_events = ()
        competitor_role = ''
        comments = 'DummyLocation'
        
        for country in countries:
            if country['iso2'] == registrations['countryIso2']:
                comp_country = country['id']
        if registrations['roles']:
            for role in registrations['roles']:
                competitor_role = ''.join([competitor_role, role.replace('delegate', 'WCA DELEGATE').upper(), ','])
            competitor_role = competitor_role[:-1]
        if registrations['registration']:
            if registrations['registration']['comments']:
                comments = registrations['registration']['comments']
            for competitor_events in registrations['registration']['eventIds']:
                registered_events += (competitor_events,)
            email = registrations['email']

            information = {
                    'name': registrations['name'].split(' (')[0].strip(),
                    'personId': registrations['wcaId'],
                    'dob': registrations['birthdate'],
                    'gender': registrations['gender'],
                    'country': comp_country,
                    'mail': email,
                    'role': competitor_role,
                    'guests': str(registrations['registration']['guests']),
                    'comments': comments
                    }

            wca_ids += (registrations['wcaId'],)
            if not registrations['wcaId']:
                information.update({'personId': ''})
            if registrations['registration']['status'] == 'accepted':
                competitor_information_wca.append(information)
                registration_id += 1
            
    return (competitor_information_wca, wca_ids)

# Get user input for wca login (mail-address, password and competition name)
# All try-except cases were implemented for simple development and will not change the normal user input
def wca_registration(new_creation):
    while True:
        try:
            wca_mail = credentials.mail_address
        except:
            wca_mail = input('Your WCA mail address: ')
        # Validation if correct mail address was entered
        if '@' not in wca_mail:
            if wca_mail[:4].isdigit() and wca_mail[8:].isdigit():
                print('Please enter your WCA account email address instead of WCA ID.')
            else:
                print('Please enter valid email address.')
        else:
            break
    try:
        wca_password = credentials.password
    except:
        wca_password = getpass.getpass('Your WCA password: ')

    return (wca_password, wca_mail)

### WCA API
# Use given input from function wca_registration to access competition WCIF
# Further information can be found here:
# https://github.com/thewca/worldcubeassociation.org/wiki/OAuth-documentation-notes
def get_wca_info(wca_password, wca_mail, competition_name, competition_name_stripped):
    print('Fetching information from WCA competition website...')
    url1 = 'https://www.worldcubeassociation.org/oauth/token'
    url2 = 'https://www.worldcubeassociation.org/api/v0/competitions/' + competition_name_stripped + '/wcif'
    
    wca_headers = {'grant_type':'password', 'username':wca_mail, 'password':wca_password, 'scope':'public manage_competitions'}
    wca_request_token = requests.post(url1, data=wca_headers)
    try:
        wca_access_token = json.loads(wca_request_token.text)['access_token']
    except KeyError:
        print('ERROR!! Failed to get competition information.\n\n Given error message: {}\n Message:{}\n\nScript aborted.'.format(json.loads(wca_request_token.text)['error'], json.loads(wca_request_token.text)['error_description']))
        sys.exit()
    wca_authorization = 'Bearer ' + wca_access_token
    wca_headers2 = {'Authorization': wca_authorization}
    competition_wcif_info = requests.get(url2, headers=wca_headers2)
    
    return competition_wcif_info.text

def create_competition_folder(competition_name):
    if not os.path.exists(competition_name):
        os.makedirs(competition_name)

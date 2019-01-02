from db import WCA_Database

### Use WCA ids of competitors to get their best results for all events of the competition + 333 single and average
def get_results_from_wca_export(wca_ids, competitor_information):
    single = WCA_Database.query("SELECT * FROM RanksSingle WHERE eventId = '333fm' and personId in %s", (wca_ids,)).fetchall()
    average = WCA_Database.query("SELECT * FROM RanksAverage WHERE eventId = '333fm' and personId in %s", (wca_ids,)).fetchall()

    for person in competitor_information:
        single_result = int(get_result(person, single) * 100)
        average_result = get_result(person, average)

        person.update({'single': single_result, 'average': average_result})
    return competitor_information

# Get a specific result
def get_result(person, results_event):
    result = 0
    for id in results_event:
        if person['personId'] == id['personId']:
            result = round(id['best'] / 100, 2)
            break

    return result

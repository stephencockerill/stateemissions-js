import csv
import json
import math
import os
import requests
import sys

NREL_API_KEY = os.getenv('NREL_API_KEY')
NREL_BASE_URL = 'https://developer.nrel.gov/'

STATES = [
    "AK","AL","AR","AZ","CA","CO","CT","DC","DE","FL",
    "GA","HI","IA","ID","IL","IN","KS","KY","LA","MA",
    "MD","ME","MI","MN","MO","MS","MT","NC","ND","NE",
    "NH","NJ","NM","NV","NY","OH","OK","OR","PA","RI",
    "SC","SD","TN","TX","UT","VA","VT","WA","WI","WV",
    "WY",
]

DATA_DIR = 'data'
# all states, data for all years, files
ALL_STATES_FILE = '%s/all_states_emissions' % DATA_DIR
ALL_STATES_FILE_JSON = '%s.json' % ALL_STATES_FILE

# all states, data for most recent year, files
ALL_STATES_RECENT_FILE = '%s/all_states_emissions_recent' % DATA_DIR
ALL_STATES_RECENT_CSV = '%s.csv' % ALL_STATES_RECENT_FILE
ALL_STATES_RECENT_HTML = '%s.html' % ALL_STATES_RECENT_FILE


class NRELClient(object):
    """
    API Client to access NREL API
    """
    def __init__(self):
        self.key = NREL_API_KEY
        self.base_url = NREL_BASE_URL
        self.emissions_url = '%sapi/cleap/v1/state_co2_emissions' % self.base_url
        self.base_params = {'api_key': self.key}

        # data
        self.all_states_emissions = self.get_all_states_emissions()


    def get_state_emissions(self, state, emissions_type='total'):
        """
        Return state emissions for the given state.

        :param state: two letter abbreviation
        :param emissions_type: Choices are 'commercial', 'electric',
          'residential', 'industrial', 'transportation', 'total'
        """
        params = {'state_abbr': state, 'type': emissions_type}
        params.update(**self.base_params)
        r = requests.get(self.emissions_url, params=params)
        emissions_data = r.json()
        if r.status_code >= 400:
            print(emissions_data)
            r.raise_for_status
        return emissions_data

    def get_all_states_emissions(self, emissions_type='total'):
        emissions_data = {}
        for state in STATES:
            try:
                state_data = self.get_state_emissions(
                    state,
                    emissions_type
                )
                emissions_data[state] = state_data['result'][0]['data']
            except:
                e = sys.exc_info()[0]
                print(e)
        return emissions_data


    def write_all_states_emissions_recent_sorted(self):
        recent_year = '2014'
        recent_sorted = []
        for state,emissions in self.all_states_emissions.items():
            inserted = False
            for item in enumerate(recent_sorted):
                if emissions[recent_year] < item[1][2]:
                    recent_sorted[item[0]:0] = [
                        [state, recent_year,emissions[recent_year]]
                    ]
                    inserted = True
                    break
            if not inserted:
                recent_sorted.append(
                    [state, recent_year,emissions[recent_year]]
                )
        # get the max emissions from the last item of recent_sorted
        max_emissions = recent_sorted[-1][2]
        max_graph_scale = int(math.ceil(max_emissions/100))*100
        print('max_graph_scale: %s' % max_graph_scale)
        with open(ALL_STATES_RECENT_CSV, 'w') as outfile:
            writer = csv.writer(outfile)
            for state in recent_sorted:
                # percentage of max used for graph height
                height_percentage = int(round((state[2] / max_graph_scale)*100))
                state.append(height_percentage)
                writer.writerow(state)

    def write_all_states_emissions_html(self):
        if not os.path.isfile(ALL_STATES_RECENT_CSV):
            self.write_all_states_emissions_recent_sorted()

        with open(ALL_STATES_RECENT_CSV, 'r') as infile:
            reader = csv.reader(infile)
            with open('vert_%s' % ALL_STATES_RECENT_HTML, 'w') as vert_file:
                with open('horiz_%s' % ALL_STATES_RECENT_HTML, 'w') as horiz_file:
                    for state in reader:
                        vertical_bar_html = '''
                            <li class="Chart__bar Chart__bar--vertical"
                                year="%s"
                                data-value="%s"
                                style="height: %s%%;"
                                onClick="barAlert(this)">%s
                            </li>
                            ''' % (state[1], state[2], state[3], state[0])
                        horizontal_bar_html = '''
                            <li class="Chart__bar Chart__bar--horizontal"
                                year="%s"
                                data-value="%s"
                                style="width: %s%%;"
                                onClick="barAlert(this)">%s
                            </li>
                            ''' % (state[1], state[2], state[3], state[0])
                        vert_file.write(vertical_bar_html)
                        horiz_file.write(horizontal_bar_html)

    def write_all_states_json(self):
        with open(ALL_STATES_FILE_JSON, 'w') as json_file:
            json.dump(self.all_states_emissions, json_file)


if __name__=='__main__':
    client = NRELClient()
    client.write_all_states_json()

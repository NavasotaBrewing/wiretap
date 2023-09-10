import logging
import os
import json
from datetime import datetime

class Event:
    def __init__(self, json_string):
        self.json = json.loads(json_string)
        self.response_type = self.json['response_type']
        self.message = self.json['message']
        self.data = self.json['data']
        self.timestamp = datetime.now().strftime("%H:%M:%S")
        self.datestamp = datetime.now().strftime("%Y_%m_%d")

        logging.info(f"Event from {self.rtu_id()} received")

    def should_be_logged(self):
        return self.response_type in ['RTUUpdateResult', 'DeviceEnactResult', 'DeviceUpdateResult']

    def rtu_id(self):
        return self.data['RTU']['id']

    def ip(self):
        return self.data['RTU']['addr']

    def file_name(self):
        return f"{self.datestamp}_{self.rtu_id()}.wiretap"

    def write_to_file(self):
        # Get the file path
        file_path = self.file_name()

        # If it doesn't exist, create it with a basic csv header
        # use | as a delimeter because there's commas in the data
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write('timestamp|data\n')
                logging.info(f"File {file_path} created")

        # Now that we know it exists, just append the new data with a timestamp
        with open(file_path, 'a') as file:
            file.write(f"{self.datestamp} {self.timestamp}|{json.dumps(self.json)}\n")
            logging.info(f"Event from {self.rtu_id()} written to file {file_path}")

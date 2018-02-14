from collections import defaultdict
from datetime import datetime

from percentile_finder import PercentileFinder


class DonationAnalytics:

    def __init__(self, input_file, percentile_file, output_file):
        self.input_file = input_file
        self.percentile_file = percentile_file
        self.donor_map = {}
        self.output_map = defaultdict(list)
        self.output_file = output_file
        with open(self.percentile_file) as f:
            lines = f.readlines()
            self.percentile = int(lines[0])

    def read_input(self):
        with open(self.input_file) as f:
            for line in f:
                fields = line.split("|")
                if fields[0].strip() and fields[7].strip() and fields[10].strip() and fields[13].strip() and fields[14].strip() and not fields[15].strip():
                    donation = {
                        "CMTE_ID": fields[0].strip(),
                        "NAME": fields[7].strip(),
                        "ZIP_CODE": self.transform_zip_code(fields[10].strip()),
                        "TRANSACTION_DT": self.transform_date(fields[13].strip()),
                        "TRANSACTION_AMT": int(fields[14].strip()),
                        "OTHER_ID": fields[15].strip()
                    }
                    yield donation

    def write_output(self, output):
        f = open(self.output_file,'a')
        print >>f, output
        f.close()

    def transform_zip_code(self, zip):
        if zip and len(zip) > 5:
            return zip[:5]
        return zip

    def transform_date(self, date_str):
        return datetime.strptime(date_str, "%m%d%Y").date()

    def process(self, donation):
        donor_key = (donation["NAME"], donation["ZIP_CODE"])
        if donor_key in self.donor_map:
            if self.donor_map[donor_key] < donation["TRANSACTION_DT"].year:
                recipient_key = (donation["CMTE_ID"], donation["ZIP_CODE"], donation["TRANSACTION_DT"].year)
                if not self.output_map[recipient_key]:
                    self.output_map[recipient_key].append(1)
                    self.output_map[recipient_key].append(donation["TRANSACTION_AMT"])
                    self.output_map[recipient_key].append([donation["TRANSACTION_AMT"]])
                else:
                    self.output_map[recipient_key][0] += 1
                    self.output_map[recipient_key][1] += donation["TRANSACTION_AMT"]
                    self.output_map[recipient_key][2].append(donation["TRANSACTION_AMT"])
                self.write_output('{}|{}|{}|{}|{}|{}'.format(
                    donation["CMTE_ID"], donation["ZIP_CODE"], donation["TRANSACTION_DT"].year,
                    PercentileFinder().find_by_percentile(self.output_map[recipient_key][2], self.percentile),
                    self.output_map[recipient_key][1],
                    self.output_map[recipient_key][0]
                    ))

        self.donor_map[donor_key] = donation["TRANSACTION_DT"].year

if __name__ == "__main__":
    from sys import argv
    donation_analytics = DonationAnalytics(argv[1], argv[2], argv[3])
    for record in donation_analytics.read_input():
        donation_analytics.process(record)
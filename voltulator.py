import sys
import csv
import locale
import datetime
import urllib2
import pprint

locale.setlocale(locale.LC_ALL, 'en_US')

class Voltulator(object):

    def __init__(self, filePath, rate, month=None):
        self.inputFile = filePath
        self.centsPerkWh = rate
        self.month = month

    def modifyCSV(self):
        totalkWhr = 0
        strippedData = self.stripNullBytes(self.inputFile)
        reader = csv.DictReader(strippedData)

        outList = []

        for row in reader:
            cols = []
            cost = float(row['kW-hr']) * self.centsPerkWh
            costFormatted = locale.currency(cost)
            if self.month is None:
                if row['Charge Start'] != '':
                    totalkWhr += float(row['kW-hr'])
                    cols.append(str(row['Charge Start']))
                    cols.append(str(row['kW-hr']))
                    cols.append(costFormatted)
            else:
                if row['Charge Start'].startswith(self.month):
                    totalkWhr += float(row['kW-hr'])
                    cols.append(str(row['Charge Start']))
                    cols.append(str(row['kW-hr']))
                    cols.append(costFormatted)
            if cols:
                outList.append(cols)
        totalCost = float(totalkWhr) * self.centsPerkWh
        totalCostFormatted = locale.currency(totalCost)
        outList.append(["", "Total kWhr: %s" % totalkWhr, "Total Cost: %s" % totalCostFormatted])

        return outList

    def stripNullBytes(self, fileToStrip):
        fixed = []
        with open(fileToStrip, 'rb') as rawFile:
            for line in rawFile:
                fixed.append(line.replace('\x00', ''))
        return fixed

if __name__ == '__main__':
    fileString = "/home/volt/chargingHistory.csv"
    now = datetime.datetime.now()
    monthNum = now.strftime("%m")

    calc = Voltulator(fileString, .107423, monthNum)
    out = calc.modifyCSV()

    pp = pprint.PrettyPrinter(indent=4)

    pp.pprint(out)

    sys.exit(0)

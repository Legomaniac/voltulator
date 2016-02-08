import sys
import csv
import locale
import datetime
import urllib2
import pprint

locale.setlocale(locale.LC_ALL, 'en_US')

class Voltulator(object):

    def __init__(self, filePath, elecRate, gasRate, month=None):
        self.inputFile = filePath
        self.centsPerkWh = elecRate
        self.dollarsPerGallon = gasRate
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

        # The Volt gets 98 MPGe electric only, but only 37 MPG gas only.
        # Therefore it is 2.65 times more effecient when running off of the battery.
        adjustedkWhr = totalkWhr * 2.65
        # EPA says 1 gallon of gasoline = 33.7 kWhr.
        equivGallons = adjustedkWhr / 33.7
        # Gallons that would have been burned if never charged, times the currect cost of Premium gas
        gasCost = equivGallons * self.dollarsPerGallon
        gasCostFormatted = locale.currency(gasCost)
        totalCost = float(totalkWhr) * self.centsPerkWh
        # Cost of electricty divided by the hypothetical gas only cost 
        percentageOfGasCost = (totalCost / gasCost) * 100
        totalCostFormatted = locale.currency(totalCost)
        outList.append(["", "Total kWhr: %s" % totalkWhr, "Total Cost: %s" % totalCostFormatted])

        outDict = {'list':outList, 'outCost':totalCostFormatted, 'outGas':gasCostFormatted, 'outPercent':"%.2f%%" % percentageOfGasCost}
        return outDict

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

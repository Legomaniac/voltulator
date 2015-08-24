import sys
import csv
import locale
import datetime
import urllib2
import pprint
from bs4 import BeautifulSoup

locale.setlocale(locale.LC_ALL, 'english_united-states')

class PriceGrabber(object):

    def __init__(self, url):
        self.url = url

    def grab(self):
        subtract = 0
        add = 0
        data = []
        page = urllib2.urlopen(self.url).read()
        soup = BeautifulSoup(page, "html.parser")

        table = soup.find('table', {"class" : "table"})
        x = (len(table.findAll('tr')) - 1)

        for row in table.findAll('tr')[1:x]:
           cols = row.findAll('td')
           if len(cols) > 3:
              if cols[3].input is not None:
                  data.append(cols[3].input['value'])

        for value in data[:-1]:
            if value.startswith("("):
                subtract += float(value[2:-1])
            else:
                add += float(value[1:-1])

        centsPerkWh = add - subtract
        return centsPerkWh

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
    fileString = "C:\Users\WOOD\Downloads\chargingHistory.csv"
    now = datetime.datetime.now()
    monthNum = now.strftime("%m")

    priceGrab = PriceGrabber('http://rates.northwesternenergy.com/residentialelectricrates.aspx')
    price = priceGrab.grab()

    calc = Voltulator(fileString, price, monthNum)
    out = calc.modifyCSV()

    pp = pprint.PrettyPrinter(indent=4)

    pp.pprint(out)

    sys.exit(0)
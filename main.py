# -*- coding: utf-8 -*-

import argparse
import requests
from itertools import groupby
import sqlite3


class DataAnalysis:
    use_sql = False
    men = "mężczyźni"
    women = "kobiety"
    acceded = "przystąpiło"
    passed = "zdało"

    csv_file = "data.csv"
    url = "https://www.dane.gov.pl/media/resources/20190520/Liczba_osób_które_przystapiły_lub_zdały_egzamin_maturalny.csv"
    table_name = "wyniki"  # name of table in db
    record_list = list()  # list of all records downloaded from url

    class Record:  # class for single record

        def __init__(self, field_list):
            self.territory = field_list[0]
            self.state = field_list[1]
            self.gender = field_list[2]
            self.year = int(field_list[3])
            self.amount = int(field_list[4])

        def show(self):
            return "{0}\t{1}\t{2}\t{3}\t{4}".format(self.territory, self.state, self.gender, self.year, self.amount)

    def load_from_csv(self):
        with open(self.csv_file, encoding='Windows-1250') as file:  # original file's encoding is windows-1250
            next(file)  # skip heading from csv file
            for line in file:
                elems = line.rstrip().split(';')  # in given file ';' is separator
                self.record_list.append(DataAnalysis.Record(elems))

    def load_from_url(self):

        try:
            bb = requests.get(self.url)  # download file from url
            for line in bb.content.decode("Windows-1250").split("\n")[1:-1]:  # [:1:-1] skip heading and remove lest
                # empty line created while split("\n")
                elems = line.rstrip().split(';')
                self.record_list.append(DataAnalysis.Record(elems))

        except requests.exceptions.RequestException as ex:
            print("Error: " + str(ex))

    def average_number(self, territory, year, gender=""):

        # use lamda for select only fitted rows
        filtered_list = list(filter(lambda a: a.year <= year and a.territory == territory and a.state == self.acceded
                                              and (a.gender == gender or not gender), self.record_list))

        if len(filtered_list) == 0:
            return 0  # empty result

        min_year = (min(filtered_list, key=lambda x: x.year)).year
        suma = sum(x.amount for x in filtered_list)
        return suma / (year - min_year + 1)  # +1 = include year

    def average_number_sql(self, territory, year, gender=""):

        result = 0
        gender_if = "1" if not gender else "gender='{0}'".format(gender)  # gender_if is always true for gender == ""
        sql_select = f"""Select AVG(suma) from 
(                       SELECT years, SUM(amount) as suma  FROM `results` 
                            WHERE `territory`='{territory}'
                                and years <={year} 
                                and `state`='{self.acceded}'
                                and {gender_if}
                            GROUP BY `years`)T"""

        try:
            conn = sqlite3.connect("date.db")
            c = conn.cursor()
            c.execute(sql_select)

            result = (c.fetchall())[0][0]  # first row of answer and first column of answer [[result]]

        except sqlite3.Error as e:
            print("Error" + str(e))
        except IndexError as e:
            result = "0"  # the result of query is empty
        finally:
            conn.close()

        return result

    def average_percent(self, territory, gender=""):

        result = list()
        filtered_list = list(filter(lambda a: a.territory == territory and (a.gender == gender or not gender),
                                    self.record_list))  # gender if is true if gender is "" or gender is selected gender

        if len(filtered_list) == 0:
            return None  # empty result

        min_year = (min(filtered_list, key=lambda x: x.year)).year
        max_year = (max(filtered_list, key=lambda x: x.year)).year

        for year in range(min_year, max_year + 1):
            acceded = sum(x.amount for x in filtered_list if (x.year == year and x.state == self.acceded))
            passed = sum(x.amount for x in filtered_list if (x.year == year and x.state == self.passed))
            result.append({"years": year, "ratio": passed / acceded * 100})  # ratio os passed/acceded

        return result

    def average_percent_sql(self, territory, gender=""):

        result = None
        gender_if = "1" if not gender else "gender='{0}'".format(gender)
        sql_select = f"""Select years,
                                SUM(CASE when `state` = '{self.passed}' then amount else 0 END)  / 
                                SUM(CASE when `state` = '{self.acceded}' then amount else 0 END) 
                                    from results
                                        where `territory`='{territory}'
                                            and {gender_if}
                                        group by years"""

        try:
            conn = sqlite3.connect("date.db")
            c = conn.cursor()
            c.execute(sql_select)

            fetch_result = (c.fetchall())
            result = list()
            for fetch in fetch_result:
                result.append({"years": fetch[0], "ratio": fetch[1]*100}) # fetch: years, ratio

        except sqlite3.Error as e:
            print("Error" + str(e))
        finally:
            conn.close()

        return result

    def best_pass_rate(self, year, gender=""):

        filtered_list = list(filter(lambda a: a.year == year and (a.gender == gender or not gender), self.record_list))
        if len(filtered_list) == 0:
            return "no results"

        groupby_list = list()

        # x[0]=territory, x[1]=state
        for i, g in groupby(sorted(filtered_list, key=lambda x: (x.territory, x.state)),
                            key=lambda x: (x.territory, x.state)):
            groupby_list.append({"ter": i[0], "state": i[1], "amount": sum(v.amount for v in g)})

        territories = set([x["ter"] for x in groupby_list])
        result_list = list()

        # groupby_list structure: { "ter": val, "state": val, "amount" : val}

        for territory in territories:
            num = next(item['amount'] for item in groupby_list if (item["ter"] == territory
                                                                   and item['state'] == self.passed))
            denum = next(item['amount'] for item in groupby_list if (item["ter"] == territory
                                                                     and item['state'] == self.acceded))
            result_list.append({"ter": territory, 'ratio': num / denum})  # ratio is num/acceded

        # result_list structure: {"ter": val, 'ratio': val})
        return max(result_list, key=lambda x: x['ratio'])['ter']

    def best_pass_rate_sql(self, year, gender=""):

        result = "no results"
        gender_if = "1" if not gender else "gender='{0}'".format(gender)
        sql_select = f"""Select `territory`,
                         (SUM(CASE when `state` = '{self.passed}' then amount else 0 END)  / 
                         SUM(CASE when `state` = '{self.acceded}' then amount else 0 END)) as zdawalanosc
                         from results
                            where `years`={year}
                                and  {gender_if}
                            group by `territory`
                            order by zdawalanosc desc"""

        try:
            conn = sqlite3.connect("date.db")
            c = conn.cursor()
            c.execute(sql_select)
            result = c.fetchall()[0][0]  # select [[result]]

        except sqlite3.Error as e:
            print("Error" + str(e))
        except IndexError as e:
            result = "no results"  # when result of select  is empty
        finally:
            conn.close()

        return result

    # this function Selects  year amd territory's ratio in the year
    def get_radio(self, territory, gender=""):

        filtered_list = list(filter(lambda a: a.territory == territory and (a.gender == gender or not gender),
                                    self.record_list))
        groupby_list = list()

        for i, g in groupby(sorted(filtered_list, key=lambda x: (x.year, x.state)), key=lambda x: (x.year, x.state)):
            groupby_list.append({"year": i[0], "state": i[1], "amount": sum(v.amount for v in g)})

        years = set([x["year"] for x in groupby_list])  # get list of unique years in list
        result_list = list()

        for year in sorted(years):  # sort list of unique years
            num = next(item['amount'] for item in groupby_list if (item["year"] == year
                                                                   and item['state'] == self.passed))
            denum = next(item['amount'] for item in groupby_list if (item["year"] == year
                                                                     and item['state'] == self.acceded))
            result_list.append({"year": year, 'ratio': num / denum})

        return result_list

    # this function Selects  year amd territory's ratio in the year
    def get_radio_sql(self, territory, gender=""):

        result = list()
        gender_if = "1" if not gender else "gender='{0}'".format(gender)
        sql_select = f"""Select `years`, 
                            (SUM(CASE when `state` = '{self.passed}' then amount else 0 END)  / 
                             SUM(CASE when `state` = '{self.acceded}' then amount else 0 END)) as zdawalanosc 
                             from results
                                where `territory`='{territory}' 
                                    and {gender_if}
                            group by `years`
                            order by `years`"""

        try:
            conn = sqlite3.connect("date.db")
            c = conn.cursor()
            c.execute(sql_select)
            for fetch in c.fetchall():
                result.append({"year": fetch[0], 'ratio': fetch[1]})

        except sqlite3.Error as e:
            print(e)
        finally:
            conn.close()

        return result

    def get_regression(self, gender=""):
        # the function just select each territory's ratio and compare ratio between years
        result = list()
        territories = set(x.territory for x in self.record_list)  # get unique list of territories

        for territory in territories:
            b = self.get_radio(territory, gender)
            years = sorted(set([x["year"] for x in b]))
            old_ratio = 0

            for i in range(len(years)):
                current_ratio = next(item['ratio'] for item in b if item["year"] == years[i])
                if current_ratio < old_ratio:
                    result.append({"territory": territory, "years_1": years[i-1], "years_2": years[i]})
                old_ratio = current_ratio  # current_ratio is now old_ratio

        return result

    def compare_hybrid(self, territoryA, territoryB, gender=""):

        result = list()
        if self.use_sql:  # depending on the  sql parameter, gets the data from different sources
            ratios_a = self.get_radio_sql(territoryA, gender)
            ratios_b = self.get_radio_sql(territoryB, gender)
        else:
            ratios_a = self.get_radio(territoryA, gender)
            ratios_b = self.get_radio(territoryB, gender)

            # ratio structure is {year: val, ratio: val}

        if len(ratios_b) == 0 or len(ratios_a) == 0:  # one of list is empty
            return None

        years = sorted(set([x['year'] for x in ratios_a]))  # get list of sorted unique years

        for year in years:

            ratio_a = next(item['ratio'] for item in ratios_a if item["year"] == year)
            ratio_b = next(item['ratio'] for item in ratios_b if item["year"] == year)

            if ratio_a >= ratio_b:
                result.append({"years": year,"territory": territoryA})
            else:
                result.append({"years": year, "territory": territoryB})

        return result

    def create_sql_base(self):

        sql_drop_table = " DROP TABLE IF EXISTS results "  # before creating new table just check if it doesnt exist
        # earlier

        sql_create_table = """ CREATE TABLE results (
                                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                                    territory text NOT NULL,
                                    state text NOT NULL,
                                    gender text NOT NULL,
                                    years int NOT NULL,
                                    amount FLOAT NOT NULL)   """  # amount should be float to easy calculate ratio

        try:

            conn = sqlite3.connect("date.db")
            c = conn.cursor()
            c.execute(sql_drop_table)
            c.execute(sql_create_table)

            bb = requests.get(self.url)
            for line in bb.content.decode("Windows-1250").split("\n")[1:-1]:  # skip first and last row
                elems = line.rstrip().split(';')

                sql_insert = f"""INSERT INTO results(territory, state, gender, years, amount) 
                                            VALUES ('{elems[0]}','{elems[1]}','{elems[2]}',{elems[3]},{elems[4]});"""
                c.execute(sql_insert)

            conn.commit()  # write changes to disc

        except sqlite3.Error as e:
            print(e)
        except requests.RequestException as e:
            print(e)
        finally:
            conn.close()


if __name__ == '__main__':

    # parse arguments
    parser = argparse.ArgumentParser(description="DataAnalysis")
    parser.add_argument("function",
                        help='type one of available function: average_num, average_percent, best_pass_rate, '
                             'get_regression and  compare')

    parser.add_argument('-t', action='store',
                        dest='territory',
                        help='Set a territory')

    parser.add_argument('-y', action='store',
                        dest='year',
                        help='Set a year',
                        type=int)

    parser.add_argument('-g', action='store',
                        dest='gender',
                        help='ser a gender')

    parser.add_argument('-sql', action='store_true',
                        dest='is_sql',
                        help='type if u want use sql')

    parser.add_argument('-tc', action='store',
                        dest='territory_2',
                        help='set second territory')

    results = parser.parse_args()

    data_analysis = DataAnalysis()
    data_analysis.use_sql = results.is_sql
    if data_analysis.use_sql:
        data_analysis.create_sql_base()
    data_analysis.load_from_url()

    if results.function == "average_num":

        if not results.territory:
            print("No territory arg")
        elif not results.year:
            print("No year arg")
        else:
            if data_analysis.use_sql:
                print(data_analysis.average_number_sql(results.territory, results.year, results.gender))
            else:
                print(data_analysis.average_number(results.territory, results.year, results.gender))

    elif results.function == "average_percent":

        if not results.territory:
            print("No territory arg")
        else:
            if data_analysis.use_sql:
                result_list = (data_analysis.average_percent_sql(results.territory, results.gender))
            else:
                result_list = (data_analysis.average_percent(results.territory, results.gender))

            if not result_list:
                print("no results")
            else:
                print("pass rate for {0}:".format(results.territory))
                for item in result_list:
                    print("\t {0} --> {1}".format(item["years"], item["ratio"]))

    elif results.function == "best_pass_rate":

        if not results.year:
            print("No year arg")
        else:
            if data_analysis.use_sql:
                print(data_analysis.best_pass_rate_sql(results.year, results.gender))
            else:
                print(data_analysis.best_pass_rate(results.year, results.gender))

    elif results.function == "get_regression":
            # territory: val, years_1: val years_2:val
        for item in data_analysis.get_regression(results.gender):
            print("{0}\t{1}-->{2}".format(item["territory"],item["years_1"], item["years_2"]))

    elif results.function == "compare":

        if not results.territory:
            print("No territory arg")
        elif not results.territory_2:
            print("No territory_2 arg")
        else:
            # years: val , territory: val
            result_list = data_analysis.compare_hybrid(results.territory, results.territory_2, results.gender)
            print("compare {0} with {1}".format(results.territory, results.territory_2))
            if result_list:
                for item in result_list:
                    print("\t{0} -> {1}".format(item["years"], item["territory"]))

    else:
        print("Unknown commands type --help for help")

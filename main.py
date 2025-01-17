#!/bin/python

import datetime
import calendar
import numpy as np
import random
import argparse
import sys
import os

def parse_args(args):
   parser = argparse.ArgumentParser(description="check help!")
   parser.add_argument("-o", "--output", dest="outputpath", required=False, help="where to dump schedule to. default is ~/.cache/YYYY-MM for the chosen year / month", type=str)
   return parser.parse_args()

def get_num_weekends(year, month, monthrange):
    num = 0
    for days in range(1,monthrange[1]+1):
        x = calendar.weekday(year, month, days)
        if x > 4:
            # hence weekend
            num += 1
    return num

def get_probabilities(month,year, weekend_scaling, avg_events):
    range_in_given_month = calendar.monthrange(year,month)
    num_weekends = get_num_weekends(year,month,range_in_given_month)
    num_weekdays = range_in_given_month[1]-num_weekends
    lhs = np.array([[num_weekends, num_weekdays], [-num_weekends, weekend_scaling+num_weekdays]])
    rhs = np.array([avg_events,0])
    soln = np.linalg.solve(lhs, rhs)
    pr_weekend = soln[0]
    pr_weekday = soln[1]
    return (pr_weekend, pr_weekday)

def select_days(probabilities, month, year):
    num_days = calendar.monthrange(year,month)[1]
    pr_weekend = probabilities[0]
    pr_weekday = probabilities[1]
    dates_to_add = []
    for days in range(1, num_days+1):
        x = calendar.weekday(year, month, days)
        flip = random.random()
        if x > 4:
            if flip<pr_weekend:
                dates_to_add.append(days)
        else:
            if flip<pr_weekday:
                dates_to_add.append(days)
    return dates_to_add


def main():
    print("\nWelcome. \n")
    year_chosen = None
    while year_chosen == None:
        year_chosen = input(
            "What year would you like to plan monthly events for? [1900-inf] (ENTER for curr. year) \n\t"
        )
        if year_chosen == "":
            year_chosen = datetime.datetime.now().year
        try:
            year_chosen = int(year_chosen)
            if year_chosen < 1900:
                raise Exception
        except:
            print("Invalid option. Please choose a valid year between 1900 and infinity\n\n")
            year_chosen = None
    print("Year chosen: %s\n" % year_chosen)

    month_chosen = None
    while month_chosen == None:
        month_chosen = input(
            "What month would you like to plan recurring, random events for? [01-12] (ENTER for curr. month) \n\t"
        )
        if month_chosen == "":
            month_chosen = datetime.datetime.now().month
        try:
            month_chosen = int(month_chosen)
            if month_chosen > 12 or month_chosen < 1:
                raise Exception
        except:
            print("Invalid option. Please choose a number between 1 and 12\n\n")
            month_chosen = None
    print("Month chosen: %s\n" % calendar.month_name[month_chosen])

    numeventsplanned = 1
    eventnamevect = []
    eventdatevect = []
    while True:
        name = input("\nName of recurring event #%s? Type (q) to quit\n\t" % numeventsplanned)
        if name == 'q': break

        eventnumpermonth = None
        while eventnumpermonth == None:
            eventnumpermonth = input(
                "\nHow many times would you like to '%s' on average for the chosen month? \n\t" % name
            )
            try:
                eventnumpermonth = int(eventnumpermonth)
                if eventnumpermonth < 1:
                    raise Exception
            except:
                print("Invalid option. Choose a valid natural number > 1\n\n")
                eventnumpermonth = None

        """
        other_events_possible_bool = None
        while other_events_possible_bool == None:
            other_events_possible_bool = input(
                "\nAllow other events on the same day? [y/n]\n"
            )
            try:
                if other_events_possible_bool not in ["y", "n"]:
                    raise Exception
                else:
                    if other_events_possible_bool == "y":
                        other_events_possible_bool = True
                    else:
                        other_events_possible_bool = False
            except:
                print("Invalid option. Please choose 'y' or 'n'\n\n")
                other_events_possible_bool = None
        """

        weekend_scaling = None
        while weekend_scaling == None:
            weekend_scaling = input(
                "\nHow much larger should E(numevents) | weekend be than E(numevents) | weekday? \n\t"
            )
            try:
                weekend_scaling = float(weekend_scaling)
                if weekend_scaling < 0:
                    raise Exception
            except:
                print("Invalid option. Choose a rational number > 0\n\n")
                weekend_scaling = None

        probabilities = get_probabilities(month_chosen, year_chosen, weekend_scaling, eventnumpermonth)
        print("\nProbability to '%s' on a weekend %s" % (name, probabilities[0]))
        print("Probability to '%s' on a weekday %s" % (name, probabilities[1]))
        dates_chosen = select_days(probabilities, month_chosen, year_chosen)
        print("\nDates chosen to '%s'" % name)
        numeventsplanned += 1
        eventnamevect.append(name)
        eventdatevect.append(dates_chosen)
    arguments = parse_args(sys.argv[1:])
    defaultpath = os.path.join(os.path.expanduser("~"), ".cache", str(year_chosen)+"-"+"{:02d}".format(month_chosen))
    if arguments.outputpath == None:
        arguments.outputpath = defaultpath
    for event_idx in range(len(eventnamevect)):
        name = eventnamevect[event_idx]
        dates = eventdatevect[event_idx]
        print("\n%s on..." % name)
        for d in dates:
            print("%s %s" % (calendar.month_name[month_chosen], d))
    with open(arguments.outputpath, 'w') as f:
        print("Schedule written to... %s" % arguments.outputpath)
        for event_idx in range(len(eventnamevect)):
            name = eventnamevect[event_idx]
            dates = eventdatevect[event_idx]
            f.write("%s\t" % name)
            for d in dates:
                if d == dates[-1]: f.write("%s-%s-%s\n" % (year_chosen, "{:02d}".format(month_chosen), "{:02d}".format(d)))
                else: f.write("%s-%s-%s\t" % (year_chosen, "{:02d}".format(month_chosen), "{:02d}".format(d)))

if __name__ == "__main__":
    main()

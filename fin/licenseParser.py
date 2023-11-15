########################################################################################################################
# Author:
#               Matt Tucker
#
# Date:
#               25 Jul 2023 - 26 Jul 2023
#
# Description:
#               Parse data from log file, form CSV file of all data, and calculate the total time license spent out
#               within time window.
#
# Rev. Date:
#               23 Oct 2023
#
# Revision Notes:
#               Removed GUI, no longer save dataframe of data within selected dates, and print total time license was
#               checked out within time window.
#
# ToDo:
#               N/A
########################################################################################################################

from datetime import datetime
import pandas as pd

########################################################################################################################
# Welcome to Log Data Parser
# ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
# This program parses and organizes license usage data, reports a collection of log entries based on dates
# specified by the user, and creates a .csv file of the results of the user's search and for every entry
# since the beginning of the record.'
# ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~
# Please remember to use the date convention: Month(short) Day Year Hour:Min:Sec (ex. 'Apr 21 2023 13:54:02').
# Set the appropriate value to 'NA' to search from the beginning, or until the ending, of time.
########################################################################################################################

# The resulting .csv will be saved in same location as the original .log file
PATH = 'license_usage_20230721.log'
# ex. 'Apr 21 2023'
START_date = 'NA'
# ex. 'Apr 21 2023'
END_date = 'NA'

# Isolates the file name from the path and sets name of .csv file to "licenseFileName_dateParsed.csv"
temp = '_' + datetime.today().strftime('%Y%b%d') + '.csv'
csv_name = PATH.replace('.log', temp)


def timeDif(use_out, use_in):
    # Find difference and return value
    delta = use_in - use_out
    if delta.days > 1:
        out = str(delta).replace(" days, ", ":")
    elif 2 > delta.days > 0:
        out = str(delta).replace(" day, ", ":")
    else:
        out = "0:" + str(delta)
    return str(out)


def getStart(date):
    if date.lower() != 'na':
        date = date + ' 00:00:00'
        start = datetime.strptime(date, '%b %d %Y %H:%M:%S')
    else:
        start = datetime.strptime('Apr 21 1000', '%b %d %Y')
    return start


def getStop(date):
    if date.lower() != 'na':
        date = date + ' 23:59:59'
        end = datetime.strptime(date, '%b %d %Y %H:%M:%S')
    else:
        end = datetime.strptime('Apr 21 3000', '%b %d %Y')
    return end


def screenData(line, last_date):
    if 'Time:' in line:
        # Get date and time
        last_date = line.strip().split('Time: ', 1)[1].split(' PDT')[0]
        last_date_stamp = datetime.strptime(last_date, '%a %b %d %Y %H:%M:%S')
        last_date = last_date_stamp.strftime('%b %d %Y')
        # Get license type
        lic_type = (line.strip().split('Time:')[0].split(' ', 1)[1]).split(' ')[0]
        return 'Time:', last_date_stamp, lic_type, last_date
    elif 'OUT:' in line:
        # Get time
        last_out = datetime.strptime(line.strip().split('OUT: ')[0].split(' ')[0], '%H:%M:%S').time()
        # Get date
        date_out = datetime.strptime(last_date, '%b %d %Y').date()
        last_out_stamp = datetime.combine(date_out, last_out)
        # Get license type
        lic_type = (line.strip().split('OUT:')[0].split(' ', 1)[1]).split(' ')[0]
        return 'OUT:', last_out_stamp, lic_type, last_date
    elif 'IN:' in line:
        # Get time
        last_in = datetime.strptime(line.strip().split('IN: ')[0].split(' ')[0], '%H:%M:%S').time()
        # Get date
        date_in = datetime.strptime(last_date, '%b %d %Y').date()
        last_in_stamp = datetime.combine(date_in, last_in)
        # Get license type
        lic_type = (line.strip().split('IN:')[0].split(' ', 1)[1]).split(' ')[0]
        return 'IN:', last_in_stamp, lic_type, last_date
    else:
        return 'None', 'None', 'None', last_date


def lineParser(Lines):
    lic_type = ""
    last_date = datetime.now().strftime('%b %d %Y')
    lic_inst = []
    for line in Lines:
        data_kind, data, lic, last_date = screenData(line, last_date)
        if data_kind == 'Time:':
            lic_type = lic
        elif data_kind == 'OUT:':
            last_out_stamp = data
        elif data_kind == 'IN:':
            last_in_stamp = data
            # Get total time out
            delta_time = timeDif(last_out_stamp, last_in_stamp)
            lic_inst.append([lic_type, last_out_stamp.strftime('%a %b %d %Y %H:%M:%S'),
                             last_in_stamp.strftime('%a %b %d %Y %H:%M:%S'), delta_time])
    return lic_inst


def main():
    file = open(PATH)
    lines = file.readlines()
    file.close()
    lic_inst = lineParser(lines)

    # Forms dataframe for all dates
    df_db = pd.DataFrame(lic_inst, columns=['License Type', 'Start Time', 'End Time', 'Delta Time'])
    df_db.to_csv(csv_name, sep='\t', encoding='utf-8', index=False)
    df_db['Start Time'] = pd.to_datetime(df_db['Start Time'])
    df_db['End Time'] = pd.to_datetime(df_db['End Time'])

    start_date = getStart(START_date)
    end_date = getStop(END_date)

    # Forms dataframe for select dates
    mask = (df_db['End Time'] >= start_date)
    df_sel = df_db.loc[mask]
    mask = (df_sel['Start Time'] <= end_date)
    df_sel = df_sel.loc[mask]

    # Calculates total time the license was checked out within date range
    total = [0, 0, 0, 0]
    for index, row in df_sel.iterrows():
        st = datetime.strptime(str(row['Start Time']), '%Y-%m-%d %H:%M:%S')
        et = datetime.strptime(str(row['End Time']), '%Y-%m-%d %H:%M:%S')
        dt = row['Delta Time']
        if (st >= start_date and et <= end_date):
            for dex, elem in enumerate(dt.split(':')):
                total[dex] = int(total[dex]) + int(elem)
        elif et >= end_date:
            subdelta = timeDif(st, end_date).split(':')
            for dex, elem in enumerate(subdelta):
                total[dex] = int(total[dex]) + int(elem)
        elif st >= start_date:
            subdelta = timeDif(start_date, et).split(':')
            for dex, elem in enumerate(subdelta):
                total[dex] = int(total[dex]) + int(elem)

    # Prints the total time the license was check out within date range
    hrs = total[0]*24 + total[1] + int((total[2] + total[3]/60)/60)
    minute = int(total[2] + total[3]/60) % 60
    sec = total[3] % 60
    print("The total time the license was checked out within the provided time window:")
    print('HH:MM:SS - ' + str(hrs) + ':' + str(minute) + ':' + str(sec))


if __name__ == "__main__":
    main()

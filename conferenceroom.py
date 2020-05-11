#!/usr/bin/env python3

import pandas as pd
import datetime

__author__ = "Your Name"
__delimiter__ = " " # delimiter to seperate each room information
__file__ = "rooms.txt" # input file
__officestart__ = "00:00" # office start time
__officeend__ = "00:00" # office end time
# office hours are assumed to be 24 hrs a day

# class to store room number and capacity and slots available with 15 minute frequency from the input file
class Room:
     def __init__(self, roomnumber, capacity, slots):
        self.roomnumber = roomnumber
        self.capacity = capacity
        self.slots = slots

# class to store the meeting request entered by user with the floor number, capcity, meetingtime (start and end tuple) and slots split into 15 minutes frequency
class Meeting:
     def __init__(self, floor, capacity, slots, meetingtime):
        self.floor = floor
        self.capacity = capacity
        self.slots = slots
        self.meetingtime = meetingtime

# generating 15 minute frequency array for a given time range (start and end) if start and end are same then you it generates a array for 24hrs range
def generate_timeslots(start,end):
    try:
        if start == end:
            return (pd.DataFrame(columns=['NULL'],index=pd.date_range(datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1), freq='15T')).index.tolist())
        else:
            return (pd.DataFrame(columns=['NULL'],index=pd.date_range(datetime.date.today(), datetime.date.today() + datetime.timedelta(days=1),freq='15T')).between_time(start,end).index.tolist())
    except FileNotFoundError as e: # handles in any errors thrown on file open
        print("Exception: {}".format(type(e).__name__))
        print("Exception Args: {}".format(e.args))
        raise Exception("Unable to generate timeslots")
# returns closest number in a list for a given value 'K'
def closest(lst, K): 
    if len(lst) == 0:
        return "N/A"
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))] 

# returns the available near by room for a given timeslot which can accomadate the meeting capacity
# officeslots - dictonary of available office slots with slot as key and (room and capacity) as value
# slot - timeslot to get the available nearby room
#capacity - capacity of the meeting

def get_available_nearby_room(officeslots,slot,capacity):
    if slot in officeslots:
        avialabeslots = officeslots[slot] # gets the available (room and cacity) array for the given slot
        nearbyroom = closest([room for room,cap in avialabeslots if cap>=capacity],capacity) # get the nearest room available which can accomated the meeting
        officeslots[slot] = [i for i in avialabeslots if i[0] != nearbyroom] # remove the selected slot from the office slot as it is no longer available
        return (slot,str(nearbyroom)) # return request slot and the available room as a slot
    else:
        return (slot,"N/A") # return request slot and None if it is not available

# returns the merged timeslots
# slots - list of slots with 15 minutes frequency
# Explanation :  if list is [time(9:00),time(11:00),time(11:15)] - it will return [(str(9:00),str(9:15)),(str(11:00),str(11:30))]
def merge_timeslots(slots):
    slots.sort()
    mergedslots = []
    temp = slots.pop(0)
    start = temp
    for slot in slots:
        if temp + datetime.timedelta(minutes=15) == slot:
            temp = slot
        else:
            mergedslots += [(start, temp + datetime.timedelta(minutes=15))]
            start = slot
            temp = slot
    mergedslots += [(start.strftime('%H:%M'), (temp + datetime.timedelta(minutes=15)).strftime('%H:%M'))]
    return mergedslots



# returns the meeting info entered 
# takes input from the user and validates it and return a meeting object
def get_input():
    meetinginput = input("Enter Input In format: <capacity:Int>,<floor:Int>,<Meeting Start: String(HH:MM)>,<Meeting End: String(HH:MM)> (Ex: 5,8,10:30,11:30) : ")
    meetingsplit = meetinginput.split(",")
    if len(meetingsplit) != 4: # assuming length of the input is always 4
        raise Exception("Invalid Input")
    meetingcapacity = int(meetingsplit[0]) # meeting capacity
    meetingfloor = int(meetingsplit[1]) # meeting floor
    slots = generate_timeslots(meetingsplit[2],meetingsplit[3])[:-1] # 15 minute frequency slots for the meeting period
    return Meeting(meetingfloor,meetingcapacity,slots,(meetingsplit[2],meetingsplit[3])) # returns meeting object

# generate and return office slots dictonary with key as timeslot with 15 minute frequency and value as tuple of roomnumber and capacity
def get_office_slots():
    officeslots = generate_timeslots(__officestart__,__officeend__)
    return { key : list() for key in officeslots } # convert a list of slots to a dictonary with a empty list

# populate the office slot with the inputed conference room information
def populate_office_slots(officeslots,conferencerooomsinfo):
    for conferencerooominfo in conferencerooomsinfo:
        for slot in conferencerooominfo.slots:
            if slot in officeslots:
                officeslots[slot] += [(conferencerooominfo.roomnumber,conferencerooominfo.capacity)] # insert (room number, capacity) as a value to the array for the timeslot the room is available


# returns list of conference room information processed from the input file
def process_input_file():
    try:
        f = open(__file__, "r") # open file in read only mode
    except FileNotFoundError as e: # handles in any errors thrown on file open
        print("Exception: {}".format(type(e).__name__))
        print("Exception Message: File Not Found")
        raise Exception("Sorry, could not process input file")
    else:
        roomsData = f.read() # read all lines from file into a string
        rooms = roomsData.split(__delimiter__) # split the string with the delimiter defined globally
        conferencerooominfo = []
        for room in rooms: # loop through each room information
            roominfo = room.split(",") # split room information with a commma
            if len(roominfo) >= 4: # assuming room information will atleast have room number, capacity of the room and pair of available start and end times
                roomnumber = float(roominfo[0]) # room number in the format of <floornumber>.<roomidentifier>
                capacity = int(roominfo[1]) # maximum capacity of the room
                slots = []
                for i in range(2,len(roominfo),2): # loop through rest of the list as a pair of two(incremented by two)
                    slot = generate_timeslots(roominfo[i],roominfo[i+1]) # generate 15 minutes frequency slots for each pair of start and stop times
                    slots += slot[:-1] # sliced the last result from the list  as it is not a valid 15 minutes frequency slot (ex: 10:00,10:30 results in [10:00,10:15,10:30] - 10:30 is not a valid 15 minute frequency response)
                conferencerooominfo += [Room(roomnumber,capacity,slots)] # append the room information object to the list
        return conferencerooominfo # returns the list of rooms

def main():
    try:
        conferencerooomsinfo = process_input_file() # process the input file
        officeslots = get_office_slots() # generate empty office slot
        populate_office_slots(officeslots,conferencerooomsinfo) # populate office slots with the processed room information
        cont = True # used to continue the scheduling
        while cont :
            meeting = get_input() # take the user input about the meeting to be scheduled
            availableslots = {}
            for slot in meeting.slots: # loop through slots required for the meeting to be scheduled
                slotresult = get_available_nearby_room(officeslots,slot,meeting.capacity) # get available nearby rooms for the given slot that can accomdate the meeting
                if slotresult[1] in availableslots:
                    availableslots[slotresult[1]]  += [slotresult[0]] # store the response to the dictionary
                else:
                    availableslots[slotresult[1]]  = [slotresult[0]] # store the response to the dictionary
            print("Rooms Available for Meeting on {time} with {capacity} on floor {floor}".format(time = meeting.meetingtime, capacity = meeting.capacity, floor = meeting.floor))
            for i in availableslots:
                print("Room Number: {number} - {mergedslot}".format(number = i, mergedslot = str(merge_timeslots(availableslots[i])).strip('[]'))) # print available rooms for the meeting slots splitted across more than one room
            temp = input("Schedule Another Meeting(Y/N) : ")
            cont = temp.lower() == "y"
    except BaseException as e:
        print(e)

if __name__ == "__main__":
    main()

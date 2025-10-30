import csv
import os

###########################################################
# Custom Exceptions
###########################################################
class RoomNotFoundError(Exception):
    pass

class TimeslotAlreadyBookedError(Exception):
    pass

class TimeslotNotBookedError(Exception):
    pass

class RoomAlreadyExistsError(Exception):
    pass

###########################################################
# Data Structures
###########################################################
Rooms = {}
VALID_BUILDINGS = ["FD1", "FD2", "FD3", "LTC", "NAB"]

###########################################################
# pare the hours in comma and list
###########################################################
def parse_hour_input(input_str):
    hours = set()
    parts = input_str.split(',')
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = part.split('-')
                start = int(start)
                end = int(end)
                for h in range(start, end + 1):
                    if 0 <= h <= 23:
                        hours.add(h)
            except:
                continue
        else:
            try:
                h = int(part)
                if 0 <= h <= 23:
                    hours.add(h)
            except:
                continue
    return sorted(list(hours))

###########################################################
# Initialise: load rooms from CSV file
###########################################################
def Initialise():
    file_name = 'bookings_final_state.csv'
    if os.path.isfile(file_name):
        with open(file_name, 'r', newline='') as fh:
            reader = csv.reader(fh)
            header = None
            for row in reader:
                if header is None and row and row[0].lower() == 'room_no':
                    header = row
                    continue
                if not row:
                    continue
                room_no = row[0].strip().upper()
                building = row[1].strip().upper()
                try:
                    capacity = int(row[2].strip())
                except:
                    capacity = 0
                booked_hours_str = row[3].strip() if len(row) > 3 else ''
                if booked_hours_str == '':
                    booked_hours = []
                else:
                    booked_hours = [int(h) for h in booked_hours_str.split(';') if h.strip() != '']
                Rooms[room_no] = {
                    "building": building,
                    "capacity": capacity,
                    "booked_hours": booked_hours
                }
    else:
        print(f"{file_name} file does not exist. Starting with empty system.")

###########################################################
# SaveData: write rooms to CSV file
###########################################################
def SaveData():
    file_name = 'bookings_final_state.csv'
    os.makedirs(os.path.dirname(file_name) or '.', exist_ok=True)
    with open(file_name, 'w', newline='') as fh:
        writer = csv.writer(fh)
        writer.writerow(['room_no','building','capacity','booked_hours'])
        for room_no in Rooms:
            room = Rooms[room_no]
            booked_hours_str = ';'.join(str(h) for h in sorted(room['booked_hours']))
            writer.writerow([room_no, room['building'], room['capacity'], booked_hours_str])
    print("Data saved to:", os.path.abspath(file_name))

###########################################################
# Create New Room
###########################################################
def CreateRoom():
    print(f"\nEnter Building name {VALID_BUILDINGS}: ", end='')
    building = input().strip().upper()

    if building not in VALID_BUILDINGS:
        print(f"Invalid building. Please choose from {VALID_BUILDINGS}.")
        return

    print("\nEnter Room Number (e.g., 1227): ", end='')
    room_number = input().strip()

    if not room_number.isalnum():
        print("Room number must be alphanumeric (no spaces or special characters).")
        return

    room_no = f"{building}-{room_number}".upper()

    if room_no in Rooms:
        raise RoomAlreadyExistsError(f"Room '{room_no}' already exists.")

    print("\nEnter Capacity (integer): ", end='')
    try:
        capacity = int(input().strip())
        if capacity < 0:
            print("Capacity cannot be negative. Setting to 0.")
            capacity = 0
    except:
        print("Invalid capacity input. Setting to 0.")
        capacity = 0

    Rooms[room_no] = {
        "building": building,
        "capacity": capacity,
        "booked_hours": []
    }

    print(f"\nNew room '{room_no}' added successfully (Building: {building}, Capacity: {capacity}).")

###########################################################
# Book a Room for one or more hours
###########################################################
def BookRoom():
    print("\nEnter Room ID to book (e.g., FD1-1227): ", end='')
    room_no_input = input().strip().upper()

    room_no = None
    for r in Rooms:
        if r.upper() == room_no_input:
            room_no = r
            break

    if not room_no:
        raise RoomNotFoundError(f"Room '{room_no_input}' not found.")

    print("\nEnter hour(s) to book (0-23, comma separated or range like 8-10): ", end='')
    hours_str = input().strip()
    hours = parse_hour_input(hours_str)

    if not hours:
        print("No valid hours entered.")
        return

    for hour in hours:
        if hour in Rooms[room_no]['booked_hours']:
            raise TimeslotAlreadyBookedError(f"Hour {hour} already booked for room {room_no}.")

    Rooms[room_no]['booked_hours'].extend(hours)
    print(f"\nRoom {room_no} successfully booked for hours: {', '.join(str(h) for h in sorted(hours))}.")

###########################################################
# Unbook Room for one or more hours
###########################################################
def UnbookRoom():
    print("\nEnter Room ID to unbook (e.g., FD1-1227): ", end='')
    room_no_input = input().strip().upper()

    room_no = None
    for r in Rooms:
        if r.upper() == room_no_input:
            room_no = r
            break

    if not room_no:
        raise RoomNotFoundError(f"Room '{room_no_input}' not found.")

    print("\nEnter hour(s) to unbook (0-23, comma separated or range like 8-10): ", end='')
    hours_str = input().strip()
    hours = parse_hour_input(hours_str)

    if not hours:
        print("No valid hours entered.")
        return

    for hour in hours:
        if hour not in Rooms[room_no]['booked_hours']:
            raise TimeslotNotBookedError(f"Hour {hour} is not currently booked for room {room_no}.")
        Rooms[room_no]['booked_hours'].remove(hour)

    print(f"\nRoom {room_no} successfully unbooked for hours: {', '.join(str(h) for h in sorted(hours))}.")

###########################################################
# View Bookings
###########################################################
def ViewRoomBookings():
    print("\nEnter Room ID to view bookings (e.g., FD1-1227): ", end='')
    room_no_input = input().strip().upper()

    room_no = None
    for r in Rooms:
        if r.upper() == room_no_input:
            room_no = r
            break

    if not room_no:
        raise RoomNotFoundError(f"Room '{room_no_input}' not found.")

    room = Rooms[room_no]
    print(f"\nRoom: {room_no}")
    print("Building:", room['building'])
    print("Capacity:", room['capacity'])
    if room['booked_hours']:
        print("Booked Hours:", ', '.join(str(h) for h in sorted(room['booked_hours'])))
    else:
        print("Booked Hours: None")

###########################################################
# Find Rooms
###########################################################
def FindRooms():
    print("\nFilter by building? (leave blank to skip): ", end='')
    building_filter = input().strip().upper()
    if building_filter and building_filter not in VALID_BUILDINGS:
        print(f"Invalid building. Valid options: {VALID_BUILDINGS}")
        building_filter = None

    print("\nFilter by minimum capacity? (leave blank to skip): ", end='')
    cap_input = input().strip()
    if cap_input == '':
        cap_filter = None
    else:
        try:
            cap_filter = int(cap_input)
        except:
            print("Invalid capacity filter. Ignoring.")
            cap_filter = None

    print("\nFilter by free at hour? (0-23) - leave blank to skip: ", end='')
    hour_input = input().strip()
    if hour_input == '':
        hour_filter = None
    else:
        try:
            hour_filter = int(hour_input)
            if hour_filter < 0 or hour_filter > 23:
                print("Hour must be 0-23. Ignoring hour filter.")
                hour_filter = None
        except:
            print("Invalid hour filter. Ignoring.")
            hour_filter = None

    results = []
    for room_no, room in Rooms.items():
        if building_filter and room['building'].upper() != building_filter:
            continue
        if cap_filter is not None and room['capacity'] < cap_filter:
            continue
        if hour_filter is not None and hour_filter in room['booked_hours']:
            continue
        results.append((room_no, room))

    print("\nFOUND ROOMS\n")
    if not results:
        print("No rooms match the given criteria.")
    else:
        for rn, r in results:
            booked = ','.join(str(h) for h in sorted(r['booked_hours'])) if r['booked_hours'] else 'None'
            print(f"{rn} | Building: {r['building']} | Capacity: {r['capacity']} | Booked Hours: {booked}")

###########################################################
# Show All Rooms
###########################################################
def ShowAllRooms():
    print("\nALL ROOMS\n")
    if not Rooms:
        print("No rooms available.")
        return
    for rn, r in sorted(Rooms.items()):
        booked = ','.join(str(h) for h in sorted(r['booked_hours'])) if r['booked_hours'] else 'None'
        print(f"{rn} : Building={r['building']}, Capacity={r['capacity']}, Booked Hours={booked}")

###########################################################
# Main Program
###########################################################
Initialise()

print("\n***** Classroom Booking System *****")
print("\nCommand-line application")
print("\nData file: bookings_final_state.csv")
print("\nPress Enter to continue", end=' ')
_ = input()

while True:
    print("\nMAIN MENU\n")
    print("01. Create New Room")
    print("02. Show All Rooms")
    print("03. Book a Room (single or multiple hours)")
    print("04. Unbook a Room (single or multiple hours)")
    print("05. View Room Bookings")
    print("06. Find Rooms (filters)")
    print("07. Exit")

    print("\nEnter Choice: ", end='')
    choice_input = input().strip()
    try:
        choice = int(choice_input)
    except:
        print("\nEnter a valid numeric choice.")
        continue

    if choice < 1 or choice > 7:
        print("\nEnter Valid Input")
        continue

    try:
        if choice == 1:
            CreateRoom()
            SaveData()
        elif choice == 2:
            ShowAllRooms()
        elif choice == 3:
            BookRoom()
            SaveData()
        elif choice == 4:
            UnbookRoom()
            SaveData()
        elif choice == 5:
            ViewRoomBookings()
        elif choice == 6:
            FindRooms()
        elif choice == 7:
            SaveData()
            print("\nData saved. Exiting.")
            break
    except RoomAlreadyExistsError as e:
        print("\nError:", e)
    except RoomNotFoundError as e:
        print("\nError:", e)
    except TimeslotAlreadyBookedError as e:
        print("\nError:", e)
    except TimeslotNotBookedError as e:
        print("\nError:", e)
    except Exception as e:
        print("\nAn unexpected error occurred:", str(e))

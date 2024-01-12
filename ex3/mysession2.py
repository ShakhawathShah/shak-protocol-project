#!/usr/bin/python3

from exceptions import InvalidTokenError, SlotUnavailableError
import reservationapi
import configparser
import sys

# Load the configuration file containing the URLs and keys
config = configparser.ConfigParser()
config.read("api.ini")

# Create an API object to communicate with the hotel API
hotel  = reservationapi.ReservationApi(config['hotel']['url'],
                                       config['hotel']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))

# Create an API object to communicate with the band API
band  = reservationapi.ReservationApi(config['band']['url'],
                                       config['band']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))
# Global varibles declared
best_slot_id = sys.maxsize
improve_tries = 1
found_slot = False
hotel_reserved = False
band_reserved = False

# Convert dict into array and return
def get_array(dict):
    array = []
    for slot in dict:
        for key in slot:
            array.append(int(slot[key]))
    return array

# Try get available slots and return list of IDs
# Catch invalid token exception and quit
# Other exceptions continue
def get_available(h, b):
    while(True):
        try:
            hotel_slots = h.get_slots_available()
            band_slots = b.get_slots_available()
            hotel_slot_ids = get_array(hotel_slots)
            band_slot_ids = get_array(band_slots)
            return hotel_slot_ids, band_slot_ids
        except InvalidTokenError as e:
            print(e)
            print("The program will now end, please restart")
            sys.exit()
        except Exception as e:
            print(e)
            continue

# Try get held slots and return list of IDs
# catch exceptions and continue
def get_held(h, b):
    while(True):
        try:
            hotel_held = h.get_slots_held()
            band_held = b.get_slots_held()
            hotel_held_ids = get_array(hotel_held)
            band_held_ids = get_array(band_held)
            return hotel_held_ids, band_held_ids
        except Exception as e:
            print(e)
            continue

# Release slots depending on size given
# For removing larger slot
def release(h, b, ids, size):
    try:
        if(size == 1):
            h.release_slot(ids[0])
            b.release_slot(ids[0])
        elif(size == 2):
            h.release_slot(max(ids[0], ids[1]))
            b.release_slot(max(ids[0], ids[1]))
    except Exception as e:
        return e

while(True):
    try:
        # Get list of commong slots to attempt to reserve
        hotel_slot_ids, band_slot_ids = get_available(hotel, band)
        common_slots = []
        for id in hotel_slot_ids:
            if id in band_slot_ids:
                common_slots.append(id)

        hotel_held_ids, band_held_ids = get_held(hotel, band)

        if(hotel_held_ids == band_held_ids):
            # Checks for existing matching slot
            if(len(hotel_held_ids) == 1 and len(band_held_ids) == 1):
                print("Currently holding matching slot \n"
                    +f"--> Hotel: {hotel_held_ids[0]}\n--> Band: {band_held_ids[0]}")
                print("+-----------------------------+")
                print("Attempting to find better slot")
                best_slot_id = hotel_held_ids[0]
                found_slot = True
            # Checks for two exisiting matching slots
            # Removes larger of slots
            elif(len(hotel_held_ids) == 2 and len(band_held_ids) == 2):
                print("Starting with two matching slots, removing larger slot")
                print("Attempting to find better slot")
                best_slot_id = min(hotel_held_ids[0], hotel_held_ids[1])
                release(hotel, band, hotel_held_ids, 2)
                found_slot = True

        # Validation to clear unmatching slots in event it occurs
        # Case for one or two unnmatching slots
        if(hotel_held_ids != band_held_ids):
            if(len(hotel_held_ids) == 1 and len(band_held_ids) == 1):
                print("Slots held do not match, clearing slots")
                release(hotel, band, hotel_held_ids, 1)

            elif(len(hotel_held_ids) == 2 and len(band_held_ids) == 2):
                print("Slots held do not match, clearing slots")
                release(hotel, band, hotel_held_ids, 2)

        for i in range(len(common_slots)):
            # Check to see if all tries to improve slot have been used
            if(improve_tries >= 3 and found_slot == True):
                print("+-----------------------------+")
                print(f"Attempt: {improve_tries}")
                print("Maximum tries to find a better slot")
                print("Confirmed Slots: \n"
                        +f"--> Hotel: {hotel_held_ids[0]}\n--> Band: {band_held_ids[0]}")
                print("The program will now end")
                sys.exit()
            # Displays attempt count to user
            elif(improve_tries < 3 and found_slot == True):
                print("+-----------------------------+")
                print(f"Attempt: {improve_tries}")
            # If no better slot break and try search again
            if(common_slots[i] > best_slot_id):
                improve_tries += 1
                break
            else:
                # Try reserve common slot for hotel and band
                # If successful exception is not caught and 
                # held IDs are returned
                print(f"Common slot {common_slots[i]}, attempting to reserve...")
                hotel.reserve_slot(common_slots[i])
                hotel_reserved = True
                band.reserve_slot(common_slots[i])
                band_reserved = True
                hotel_held_ids, band_held_ids = get_held(hotel, band)

                # First matching slot is found, attempt to improve
                # Display output to user
                if(len(hotel_held_ids) == 1 and len(band_held_ids) == 1):
                    best_slot_id = hotel_held_ids[0]
                    print(f"New best slot {best_slot_id} reserved for hotel and band")
                    print("+-----------------------------+")
                    print("Attempting to find better slot")
                    improve_tries = 1
                    found_slot = True
                    break
                # Second matching slot is found attempt to improve
                # Remove larger of the two slots
                # Display output to user
                if(len(hotel_held_ids) == 2 and len(band_held_ids) == 2):
                    best_slot_id = min(hotel_held_ids[0], hotel_held_ids[1])
                    print(f"New best slot {best_slot_id} reserved for hotel and band")
                    print("+-----------------------------+")
                    print("Attempting to find better slot")
                    release(hotel, band, hotel_held_ids, 2)
                    improve_tries = 1
                    found_slot = True
                    break
                improve_tries += 1
    # Deal with any exceptions that occur
    except Exception as e:
        print(e)
        if(hotel_reserved == True):
            hotel.release_slot(hotel_slot_ids[i])
            improve_tries += 1
            continue
        elif(band_reserved == True):
            hotel.release_slot(hotel_slot_ids[i])
            improve_tries += 1
            continue
        improve_tries += 1
        continue
#!/usr/bin/python3

import sys
from exceptions import InvalidTokenError
import reservationapi
import configparser

# Load the configuration file containing the URLs and keys
config = configparser.ConfigParser()
config.read("api.ini")

# Create an API object to communicate with the hotel API
hotel  = reservationapi.ReservationApi(config['hotel']['url'],
                                       config['hotel']['key'],
                                       int(config['global']['retries']),
                                       float(config['global']['delay']))

reserved = False

def get_array(dict):
    array = []
    for slot in dict:
        for key in slot:
            array.append(int(slot[key]))
    return array

def get_available(h):
    while(True):
        try:
            hotel_slots = h.get_slots_available()
            hotel_slot_ids = get_array(hotel_slots)
            return hotel_slot_ids
        except InvalidTokenError as e:
            print(e)
            print("The program will now end, please restart")
            sys.exit()
        except Exception as e:
            print(e)
            continue

def reserve(h, ids):
    while(True):
        try:
            for id in ids:
                h.reserve_slot(id)
                print(f"Reserved Slot {id}")
                break
            break
        except Exception as e:
            print(e)
            continue

def get_held(h):
    while(True):
        try:
            hotel_held = h.get_slots_held()
            hotel_held_ids = get_array(hotel_held)
            return hotel_held_ids
        except Exception as e:
            print(e)
            continue

def release(h, ids):
    while(True):
        try:
            if(len(ids) == 1):
                h.release_slot(ids[0])
                print(f"Released Slot {ids[0]}")
                break
            elif(len(ids) == 2):
                h.release_slot(ids[0])
                h.release_slot(ids[1])
                print(f"Released Slot {ids[0]} and {ids[1]}")
                break
        except Exception as e:
            return e
        

print("Showing hotel slot functionality")

print("Getting slots held")
hotel_held = get_held(hotel)
print(f"Currently holding {hotel_held}")

print("Getting slots available")
hotel_slot_ids = get_available(hotel)

print("Reserving slot for hotel")
reserve(hotel, hotel_slot_ids)

print("Getting slots held")
hotel_held = get_held(hotel)
print(f"Currently holding {hotel_held}")

print("Releasing slot for hotel")
release(hotel, hotel_held)

print("Getting slots held")
hotel_held = get_held(hotel)
print(f"Currently holding {hotel_held}")
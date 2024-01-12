""" Reservation API wrapper

This class implements a simple wrapper around the reservation API. It
provides automatic retries for server-side errors, delays to prevent
server overloading, and produces sensible exceptions for the different
types of client-side error that can be encountered.
"""

# This file contains areas that need to be filled in with your own
# implementation code. They are marked with "Your code goes here".
# Comments are included to provide hints about what you should do.

from lib2to3.pgen2 import token
import re
import sys
from defer import return_value
import requests
import simplejson
import warnings
import time

from requests.exceptions import HTTPError
from exceptions import (
    BadRequestError, InvalidTokenError, BadSlotError, NotProcessedError,
    SlotUnavailableError,ReservationLimitError)

class ReservationApi:
    def __init__(self, base_url: str, token: str, retries: int, delay: float):
        """ Create a new ReservationApi to communicate with a reservation
        server.

        Args:
            base_url: The URL of the reservation API to communicate with.
            token: The user's API token obtained from the control panel.
            retries: The maximum number of attempts to make for each request.
            delay: A delay to apply to each request to prevent server overload.
        """
        self.base_url = base_url
        self.token    = token
        self.retries  = retries
        self.delay    = delay

    def _reason(self, req: requests.Response) -> str:
        """Obtain the reason associated with a response"""
        reason = ''

        # Try to get the JSON content, if possible, as that may contain a
        # more useful message than the status line reason
        try:
            json = req.json()
            reason = json['message']

        # A problem occurred while parsing the body - possibly no message
        # in the body (which can happen if the API really does 500,
        # rather than generating a "fake" 500), so fall back on the HTTP
        # status line reason
        except simplejson.errors.JSONDecodeError:
            if isinstance(req.reason, bytes):
                try:
                    reason = req.reason.decode('utf-8')
                except UnicodeDecodeError:
                    reason = req.reason.decode('iso-8859-1')
            else:
                reason = req.reason

        return reason


    def _headers(self) -> dict:
        """Create the authorization token header needed for API requests"""
        header = {'accept':'application/json', 'Authorization': 'Bearer ' + self.token}
        return header


    def _send_request(self, method: str, endpoint: str) -> dict:
        """Send a request to the reservation API and convert errors to
           appropriate exceptions"""
        # Allow for multiple retries if needed
        tries = 1
        
        while (tries < self.retries):
            # Perform the request.
            if method == "GET":
                r = requests.get(self.base_url + endpoint, headers=self._headers())
                time.sleep(self.delay)

            if method == "POST":
                r = requests.post(self.base_url + endpoint, headers=self._headers())
                time.sleep(self.delay)

            if method == "DELETE":
                r = requests.delete(self.base_url + endpoint, headers=self._headers())
                time.sleep(self.delay)

            # 200 response indicates all is well - send back the json data.
            if(r.status_code == 200):
                print("Successful Request")
                return r.json()

            # 400 errors are client problems that are meaningful, so convert
            # them to separate exceptions that can be caught and handled by
            # the caller.
            elif(r.status_code == 400):
                print("A 400 Bad Request error occurred")
                raise BadRequestError

            elif(r.status_code == 401):
                print("The API token was invalid or missing")
                raise InvalidTokenError

            elif(r.status_code == 403):
                print("The requested slot does not exist")
                raise BadSlotError

            elif(r.status_code == 404):
                print("The request has not been processed")
                raise NotProcessedError

            elif(r.status_code == 409):
                print("The requested slot is not available")
                raise SlotUnavailableError

            elif(r.status_code == 451):
                print("The client already holds the maximum number of reservations")
                raise ReservationLimitError

            # 5xx responses indicate a server-side error, show a warning
            # (including the try number).
            elif(r.status_code >= 500):
                print("Server Error: "+ str(r.status_code) + " " + str(self._reason(r)) + ", tries taken: " + str(tries))

            # Anything else is unexpected and may need to kill the client.
            else:
                print("Unexpected Error: "+ str(r.status_code) + " " + str(self._reason(r)))
                sys.exit()
            tries += 1
            if(tries == 3):
                print("Repeating Request")
                tries = 0
            # Delay before processing the response to avoid swamping server.
            time.sleep(self.delay)
        # Get here and retries have been exhausted, throw an appropriate
        # exception.


    def get_slots_available(self):
        """Obtain the list of slots currently available in the system"""
        print("Getting all slots available...")
        r_json = self._send_request("GET", "/reservation/available")
        return r_json

    def get_slots_held(self):
        """Obtain the list of slots currently held by the client"""
        print("Getting all slots held...")
        r_json = self._send_request("GET", "/reservation")
        return r_json

    def release_slot(self, slot_id):
        """Release a slot currently held by the client"""
        print("Releasing slot...")
        r_json = self._send_request("DELETE", "/reservation/" + str(slot_id))
        return r_json

    def reserve_slot(self, slot_id):
        """Attempt to reserve a slot for the client"""
        print("Reserving slot...")
        r_json = self._send_request("POST", "/reservation/" + str(slot_id))
        return r_json
import requests
from datetime import datetime, timezone

# Ranks to skip in the main group
mainGroupFilter = [1] # Rank 1 = Class D in CreepySins' SCPF

# Delay timer, this will delay apis calls to every x seconds to ensure that the script is not rate limited
# 0.84s is the minimum delay on a single ip for every request
# Api limt is 60 requests every 50 seconds
delayTimer = 0.1

# Functions
def logError(input):
    # Logs any errors and unexpected events in a file to view with timestamp
    f = open("errorlog.txt", "a")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    f.write(f"[{now}]: {str(input)}\n")
    f.close()

def ownerPunctation(username):
    # If username ends with a 's' use correct grammar
    # idk why but it drove me crazy seeing Creepysins's in testing
    if username.endswith('s'):
        return username + "'"
    else:
        return username + "'s"

def userExport(foundUserList,goiOwner,mainOwner):
    # Export an array of User objects into a csv file
    csv = open("foundLog.csv", "a")
    txt = open("foundLog.txt", "a")
    for user in foundUserList: 
        csv.write(f"\n{user.username},{user.id},{user.mainRole},{user.goiRole}")
        txt.write(foundPadder(user),goiOwner,mainOwner)
    csv.close()
    txt.close()

def foundPadder(user,goiOwner,mainOwner):
    # Makes a nice formated string output for each user 
    content = [
                f"Found {user.username} in {ownerPunctation(goiOwner)} GoI",
                f"Rank in {ownerPunctation(goiOwner)} GoI: {user.goiRole}",
                f"Rank in {ownerPunctation(mainOwner)} GoI: {user.mainRole}"
              ]

    # Character used for padding
    paddingChar = '='

    # Massive fucking code to find which line is the longest, and use that length to set the padding
    if (len(content[0]) >= len(content[1])) and (len(content[0]) >= len(content[2])):
        largest = len(content[0])
    elif (len(content[1]) >= len(content[0])) and (len(content[1]) >= len(content[2])):
        largest = len(content[1])
    else:
        largest = len(content[2])
    padding = "\n" + paddingChar + (paddingChar * largest) +"\n"

    return padding + '\n'.join(content) + padding

# Classes
class ApiHandler():
    # Class to deal with API Handleing and rate limits

    # Initalize timer, used to set basis for last api call
    apiCallTimer = datetime.now(timezone.utc)
    
    def execute(self,endpoint):
        while True:
            # Check to see if another request can be made within the set delayTimer, if not then wait until it can be done
            if ((datetime.now(timezone.utc) - self.apiCallTimer).total_seconds() >= delayTimer):
                # Reset timer upon API call
                self.apiCallTimer = datetime.now(timezone.utc)

                # API call using roproxy
                response = requests.get("https://groups.roproxy.com" + endpoint)
                
                # Check to see if roproxy API call worked
                if response.status_code == 200:
                    return response.json()
                
                else:
                    while True:
                        # Check timer again, using a delay timer of 0.84s as that is default roblox rate limit
                        if ((datetime.now(timezone.utc) - self.apiCallTimer).total_seconds() >= 0.84):
                            # Try making a call to the general roblox api
                            responseDefaultApi = requests.get("https://groups.roblox.com" + endpoint)
                            # Check that normal roblox api is giving an OK response
                            if responseDefaultApi.status_code == 200:
                                return responseDefaultApi.json()
                            else:
                                # Log an error because something is fucking up that I have no idea about
                                logError(f"{response.status_code}\n{response.json()}\n\n{responseDefaultApi.status_code}\n{responseDefaultApi.json()}")
                                break
                    break
            
class User():
    # Class for handling user details and checking
    def __init__(self, id, username, rank, role):
        # Create user object with inputs on class call
        self.id = id
        self.username = username
        self.goiRank = rank
        self.goiRole = role

        # Set mainRank to 0 AKA Guest so if they are not in the group return 0
        # If they are found in the group, this will change to the group rank
        self.mainRank = 0

    # Function to check if user is in the main group
    def checkUser(self, mainGroupID, Handler):

        # Make API call using /v2/users/userId/groups/roles endpoint
        response = Handler.execute(f"/v2/users/{self.id}/groups/roles")

        # Check if API returned the expected response of the key 'data'
        if response['data']:
            # Go through each group returned 
            for groupObject in response['data']:
                # Check if the current iteration of groups returned matches the Main group
                if groupObject['group']['id'] == mainGroupID:
                    # Check if user is not in the filtered roles for the Main group
                    if groupObject['role']['rank'] not in mainGroupFilter:
                        # If user isn't in the filter, then update the role of the user and return True
                        self.mainRole = groupObject['role']['name']
                        return True
        else:
            # Bro this should not ever happen 🙏, but if it does its logged 
            logError(f"API Error for user {id}:\n{response}")

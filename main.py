from methods import User,ApiHandler, logError, ownerPunctation, userExport

Handler = ApiHandler()

# !!!!NOTICE!!!! Please set main group to the larger group, this will save time and resources
maingroup = 2760782 # CreepySins' SCPF
mainOwner = Handler.execute(f"/v1/groups/{maingroup}")['owner']['username']

# Wipe old logs and create if they dont exist
for extension in ['txt','csv']:
    filepath = f"foundLog.{extension}"
    f = open(filepath, "w")
    f.write("")
    f.close()

while True:

    # Get group ID from user, get GoI Owner username and GoI Member count
    while True:
        groupid = input("Group ID: ")
        # Check if input is a digit
        if groupid.isdigit():
            # Make API request to get group info
            response = Handler.execute(f"/v1/groups/{groupid}")
            # Check if owner exists in the response keys
            if 'owner' in response.keys():
                goiOwner = response['owner']['username']
                # Check if memberCount exists in the response keys
                # (It fucking better if the owner exists 👿)
                if 'memberCount' in response.keys():
                    memberCount = response['memberCount']
                    # Try to get GoI name, if it fails meh 🤷‍♂️
                    try:
                        goiName = response['name']
                    except Exception as e:
                        goiName = "Error"
                        logError("Error phrasing GoI Name\n" + response)
                    break
            # If there is an error phrasing either owner or memberCount then log it
            logError("Error phrasing GoI Info\n" + response)

    f = open("foundLog.csv", "w")
    f.write(f"Username,User ID,{ownerPunctation(mainOwner)} Rank,{ownerPunctation(goiOwner)} Rank")
    f.close()

    # Get group roles
    response = Handler.execute(f"/v1/groups/{groupid}/roles")
    # Initial rankList array
    rankList = []
    # Check that roles varible exists in API reponse
    if 'roles' in response.keys():
        # Print out the ranks in the GoI
        print("Ranks in " + goiName)
        for role in response['roles']:
            # Make sure current rank is not guest
            if role['rank'] != 0:
                print(f"{role['name']}: {role['rank']}")
                # Add rank to rankList
                rankList.append(role['rank'])
        print("=================")
        print("What roles would you like to skip? Type the numbers using ',' as a seperator")
        # Loop to ensure right varibles are entered into the filter
        while True:
            # Seperate each rank and remove any whitespace
            filterInput = input("Rank(s): ").strip()
            rankFilter = filterInput.split(',')
            for rank in rankFilter:
                # Check if rank user entered exists in the Rank List
                # if not then tell them it doesn't exist and loop back to the input
                if int(rank) not in rankList:
                    print(rankList)
                    print(rankFilter)
                    print(f"{rank} is not a valid rank!")
                    continue
            # Break loop if all user entered ranks are fine
            break

    # Initialize endpoint for API
    endpoint = f"/v1/groups/{groupid}/users?limit=100"

    membersScanned = 0
    # Loop so it goes through until it reaches the end of members
    while True:
        # Execute API call
        userList = Handler.execute(endpoint)
        # Check Data is returned without error
        if 'data' not in userList.keys():
            # Log errors for debuging
            logError("Could not retrieve data from API: {endpoint}")
            logError(userList)
            # continue to next API call and pray that works
            continue

        # Iterate through each user
        foundUsers = []
        for user in userList['data']:
            membersScanned+=1
            # Make sure user is not rank 0 (This should never happen but good to be thorough)
            if user['role']['rank'] == 0:
                # Skip user, and go onto the next one
                continue
            # Load the current user into a User class
            currentUser = User(user['user']['userId'],user['user']['username'],user['role']['rank'],user['role']['name'])
            # Check if the users rank in the GoI is not in the filter
            if str(currentUser.goiRank) not in rankFilter:
                # Execute checkUser function, if it finds the user in the GoI then returns True
                if currentUser.checkUser(maingroup, Handler):
                    # Append the User Object to an array to bulk export to file at the end of this page of users
                    foundUsers.append(currentUser)
        # Export users before next API call to get new users
        userExport(foundUsers,goiOwner,mainOwner)         
        # If there is a next page cursor then append it to the endpoint
        if userList['nextPageCursor']:
            # Debug to show progress
            print(f"Going to next page | {membersScanned}/{memberCount}")
            # Update endpoint
            endpoint = f"/v1/groups/{groupid}/users?limit=100&cursor={userList['nextPageCursor']}"
            continue
        # If no next page cursor is found then break loop
        break

    print("Done")                      

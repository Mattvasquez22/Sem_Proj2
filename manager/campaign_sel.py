#########################################################
# Script used to define functions used to obtain the    #
# campaigns, manage the campaign selection accordingly  #
# and puts client back into pool if necessary           #
#########################################################

from connection_char import placeinPool,TIMESTAMPS

def fetchCampaigns():
    #campaigns = {'a':1,'b':2}
    campaigns = '1,2,3'
    return campaigns 

def checkSelection(response):
    #To be defined more specifically later
    if(response in CAMPAIGNS):
        return True
    else:
        return False

def campaignSelection(client):
    client.client_sock.send(fetchCampaigns())
    counter = 3
    while counter > 0:
        read_data = client.client_sock.recv(255)
        selected_campaigns = read_data.rstrip()
        if(checkSelection(selected_campaigns)):
            print("VALID CAMPAIGN IS:  " + selected_campaigns)
            counter = 3
            break
        else:
            counter -= 1
            print("INVALID CAMPAIGN, TRIES LEFT: {}".format(str(counter))) 
    if(counter == 0):
        print("NO MORE TRIES LEFT")
        placeinPool(client.client_ID,TIMESTAMPS[client.client_ID])                    


CAMPAIGNS = fetchCampaigns()

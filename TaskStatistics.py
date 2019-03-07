import json
import requests
from datetime import datetime
import sys

api_token = '<Paste your API token here>'

# This function returns the IDs of all the tasks that a given user is subscribed.
def TasksSubscribedIDs(name):
    task_ids = []
    params = {
        'api.token': api_token,
        'constraints[subscribers][0]': name
    }
    try:
        response = requests.post('https://phabricator.wikimedia.org/api/maniphest.search', data=params)
        json_response = json.loads(response.text)
        for item in json_response['result']['data']:
            task_ids.append(item['id'])
        return task_ids
    except:
        print('Unfortunately Task IDs can not be fetched')
        sys.exit(-1)

# This function return the PhID when a username is provided 
def PhID(name):
    params = {
        'api.token': api_token,
        'constraints[usernames][0]': name
    }
    try:
        response = requests.post('https://phabricator.wikimedia.org/api/user.search', data=params)
        json_response = json.loads(response.text)
        return json_response['result']['data'][0]['phid']
    except:
        print('PhID for user can not be fetched. Make sure you entered a valid username')
        sys.exit(-1)

# This function returns the list of 'core:subscribed' transactions on the tasks which a user is subscribed to.         
def TaskTransactionsOfUser(phid, task_ids):
    user_subscriptions = []
    params = {
        'api.token': api_token
    }

    for i in range(0, len(task_ids)):
        params['ids[{}]'.format(i)] = task_ids[i]
    try:       
        response = requests.post('https://phabricator.wikimedia.org/api/maniphest.gettasktransactions', data=params)
        json_response = json.loads(response.text)
    except:
        print('Subscribed tasks can not be fetched')
        sys.exit(-1)
    for task in task_ids:
        transactions_for_task = json_response['result'][str(task)]

        for transaction in transactions_for_task:
            if transaction['transactionType'] == 'core:subscribers' and transaction['newValue'][-1] == phid:
                user_subscriptions.append(transaction)

    return user_subscriptions

if __name__ == "__main__":
    name = input('Enter username: ')
    phid = PhID(name)
    task_ids = TasksSubscribedIDs(name)
    user_subscriptions = TaskTransactionsOfUser(phid, task_ids)
    period = input('Enter month and year in MM/YYYY format: ')
    try:
        month, year = period.split('/')
        parsed_period = datetime(int(year), int(month), 1)
    except:
        print('Enter a valid date')    
    count_week1, count_week2, count_week3 ,count_week4 = 0,0,0,0

    # for every 'core:subscribed' transaction, Check if it falls in the period provided by user.
    for subscription in user_subscriptions:
        parsed_dateCreated = datetime.utcfromtimestamp(int(subscription['dateCreated']))
        if parsed_period.month == parsed_dateCreated.month and parsed_period.year == parsed_dateCreated.year:
            if parsed_dateCreated.day <= 7:
                count_week1+=1
            elif parsed_dateCreated.day > 7 and parsed_dateCreated.day <=14:
                count_week2+=1
            elif parsed_dateCreated.day > 14 and parsed_dateCreated.day <=21:
                count_week3+=1
            else:
                count_week4+=1    
                 

    print('Week | subscriptions')
    print('--------------------')
    print(' 1   |  {}'.format(count_week1))
    print(' 2   |  {}'.format(count_week2))
    print(' 3   |  {}'.format(count_week3))
    print(' 4   |  {}'.format(count_week4))
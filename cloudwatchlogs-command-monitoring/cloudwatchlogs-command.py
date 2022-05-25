import boto3
import datetime
import requests

AWS_REGION = #region name

slack_url=#slack-url
class Query_maker:
    def __init__(self,commands):
        self.commands=commands
    def command_to_query(self):
        query_command=self.commands
        query=""
        for command in query_command:
            query=query+"?"+command+" "
        return query    


session= boto3.Session(profile_name='profile-test')
client = session.client('logs',region_name=AWS_REGION)

def filter_log_events(query):
    start_time=(datetime.datetime.now()-datetime.timedelta(minutes=15))
    response = client.filter_log_events(
        logGroupName='commands-log',
        logStreamNamePrefix='i',
        startTime=int(start_time.strftime('%s'))*1000,
        endTime=int(datetime.datetime.now().strftime('%s'))*1000,
        limit=100,
        filterPattern=f'{query}'
    )

    log_events = response['events']
    return ({'Events': log_events})

def slack_push(instance_id,message_log,eventID):
    alert_map = {
    "emoji": {
        "up": ":white_check_mark:",
        "down": ":rickroll:"
    },
    "text": {
        "up": "RESOLVED",
        "down": "ALERT"
    },
    "message": {
        "down": "Somebody tried to run an illegal command in an instance"
    },
    "color": {
        "down": "#ad1721"
    }
}
    
    cloudwatch_url="https://"+AWS_REGION+".console.aws.amazon.com/cloudwatch/home?region="+AWS_REGION+"#logsV2:log-groups/log-group/commands-log/log-events/"+instance_id
    status="down"
    instance_name=get_instance_name(instance_id)
    data = {
        
        "attachments": [
        {
            "text": "{emoji} [*{state}*]  \n {message}  \n Details:- \n Instance-ID : {instance} \n Instance-Name : {instance_name} \n Command-Log : {log_message} \n EventID : {id_event}".format(
                emoji=alert_map["emoji"][status],
                state=alert_map["text"][status],
                message=alert_map["message"][status],
                instance=instance_id,
                instance_name=instance_name,
                log_message= message_log,
                id_event=eventID
            ),
            "color": alert_map["color"][status],
            "attachment_type": "default",
            "actions": [
                {
                    "name": "Logs",
                    "text": "Cloudwatch Logs",
                    "type": "button",
                    "style": "primary",
                    "url": cloudwatch_url
                }
            ]
        }]
    }

    response = requests.post(slack_url, json=data)
    return 1
        

def get_instance_name(fid):
    # When given an instance ID as str e.g. 'i-1234567', return the instance 'Name' from the name tag.
    ec2 = session.resource('ec2',region_name=AWS_REGION)
    ec2instance = ec2.Instance(fid) 
    instancename = ''
    for tags in ec2instance.tags:
        if tags["Key"] == 'Name':
            instancename = tags["Value"]        
    return instancename

banned_commands=['"cat /etc/passwd"','rm']      #Here put in the commands you want to be banned

query_maker=Query_maker(banned_commands)
query=query_maker.command_to_query()
print(query)
events=filter_log_events(query)
for event in events['Events']:
    
    instance_id=event['logStreamName']
    message_log=event['message']
    eventID=event['eventId']
    slack_push(instance_id,message_log,eventID)
    


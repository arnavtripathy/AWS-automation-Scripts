#!/bin/bash


echo $'export PROMPT_COMMAND=\'RETRN_VAL=$?;logger -p local6.debug "$(whoami) [$$]: $(history 1 | sed "s/[ ][0–9]+[ ]//" ) [$RETRN_VAL]"\'' >> /etc/bash.bashrc
source /etc/bash.bashrc
echo local6.* /var/log/commands.log | sudo tee -a /etc/rsyslog.d/bash.conf
service rsyslog restart
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i -E ./amazon-cloudwatch-agent.deb
bash -c 'cat <<EOF > /opt/aws/amazon-cloudwatch-agent/bin/config.json
{
     "agent": {
         "run_as_user": "root"
     },
     "logs": {
         "logs_collected": {
             "files": {
                 "collect_list": [
                     {
                         "file_path": "/var/log/commands.log",
                         "log_group_name": "commands-log",
                         "log_stream_name": "{instance_id}"
                     }
                 ]
             }
         }
     }
 }
'

/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json -s

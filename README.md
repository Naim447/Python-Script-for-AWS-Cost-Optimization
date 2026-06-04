# Python-Script-for-AWS-Cost-Optimization
A good solution is to create a **cost-optimization script** that first scans AWS resources and then optionally stops them. I strongly recommend **not deleting resources automatically** until you've tested the script thoroughly.

## What This Script Will Check

* Running EC2 instances
* Unattached EBS volumes
* Unused Elastic IPs
* RDS instances
* Load Balancers

## Prerequisites

### 1. Install AWS CLI

```bash
pip install awscli
```

### 2. Install Boto3

```bash
pip install boto3
```

### 3. Configure AWS Credentials

```bash
aws configure
```

Provide:

```text
AWS Access Key ID
AWS Secret Access Key
Region (e.g. ap-south-1)
Output format (json)
```

### 4. IAM Permissions

The user/role should have permissions like:

```json
{
  "Effect": "Allow",
  "Action": [
    "ec2:*",
    "rds:*",
    "elasticloadbalancing:*"
  ],
  "Resource": "*"
}
```

---

# Python Script

Save as:

```text
aws_cost_optimizer.py
```

```python
import boto3

REGION = "ap-south-1"

ec2 = boto3.client('ec2', region_name=REGION)
rds = boto3.client('rds', region_name=REGION)
elb = boto3.client('elbv2', region_name=REGION)

print("\n===== EC2 Instances =====")

instances = ec2.describe_instances()

for reservation in instances['Reservations']:
    for instance in reservation['Instances']:

        instance_id = instance['InstanceId']
        state = instance['State']['Name']

        print(f"{instance_id} : {state}")

        # Uncomment after testing
        # if state == 'running':
        #     ec2.stop_instances(
        #         InstanceIds=[instance_id]
        #     )
        #     print(f"Stopped {instance_id}")

print("\n===== Unattached EBS Volumes =====")

volumes = ec2.describe_volumes(
    Filters=[
        {
            'Name': 'status',
            'Values': ['available']
        }
    ]
)

for volume in volumes['Volumes']:

    print(
        f"Unused Volume: {volume['VolumeId']} "
        f"Size={volume['Size']}GB"
    )

    # Uncomment after testing
    # ec2.delete_volume(
    #     VolumeId=volume['VolumeId']
    # )

print("\n===== Elastic IPs =====")

addresses = ec2.describe_addresses()

for addr in addresses['Addresses']:

    if 'InstanceId' not in addr:
        print(
            f"Unused EIP: "
            f"{addr['PublicIp']}"
        )

print("\n===== RDS Instances =====")

dbs = rds.describe_db_instances()

for db in dbs['DBInstances']:

    dbid = db['DBInstanceIdentifier']
    status = db['DBInstanceStatus']

    print(f"{dbid} : {status}")

    # Uncomment after testing
    # rds.stop_db_instance(
    #     DBInstanceIdentifier=dbid
    # )

print("\n===== Load Balancers =====")

lbs = elb.describe_load_balancers()

for lb in lbs['LoadBalancers']:
    print(
        f"{lb['LoadBalancerName']}"
    )

print("\nScan Complete.")
```

---

# Run the Script

```bash
python aws_cost_optimizer.py
```

Output:

```text
===== EC2 Instances =====
i-123456789 : running

===== Unattached EBS Volumes =====
vol-12345 Size=100GB

===== Elastic IPs =====
52.66.xxx.xxx

===== RDS Instances =====
dev-mysql : available
```

---

# Safe Workflow

### Step 1

Run in **Audit Mode** only.

No stopping or deleting.

Review output.

### Step 2

Add resource tags:

```text
AutoShutdown=True
Environment=Dev
```

### Step 3

Modify script to stop only tagged resources.

Example:

```python
tags = {
    tag['Key']: tag['Value']
    for tag in instance.get('Tags', [])
}

if tags.get('AutoShutdown') == 'True':
    ec2.stop_instances(
        InstanceIds=[instance_id]
    )
```
<img width="1366" height="768" alt="image" src="https://github.com/user-attachments/assets/66b54e31-6ede-41b1-8969-1b5b06f7d413" />

---

# Schedule Daily

### Linux Cron

```bash
crontab -e
```

Run every day at 8 PM:

```text
0 20 * * * /usr/bin/python3 /home/ubuntu/aws_cost_optimizer.py
```

---

# Better Production Architecture

For enterprise use:

AWS Lambda
     |
CloudWatch Schedule
     |
Scan Resources
     |
SNS
     |
Email Alert


**Flow:**

1. Lambda runs daily.
2. Finds idle resources.
3. Sends email report.
4. Stops only tagged DEV resources.
5. Never touches PROD resources.

This is much safer than automatic deletion and is the approach most AWS teams use.


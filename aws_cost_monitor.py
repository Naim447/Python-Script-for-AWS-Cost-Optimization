import boto3

REGION = "ap-south-1"

ec2 = boto3.client("ec2", region_name=REGION)
rds = boto3.client("rds", region_name=REGION)

print("\n==============================")
print("AWS COST MONITOR")
print("==============================")

# ----------------------------------
# EC2 INSTANCES
# ----------------------------------

print("\nRunning EC2 Instances:")

response = ec2.describe_instances()

for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:

        instance_id = instance["InstanceId"]
        state = instance["State"]["Name"]

        print(f"Instance: {instance_id}")
        print(f"Status  : {state}")
        print("----------------------")

# ----------------------------------
# UNUSED EBS VOLUMES
# ----------------------------------

print("\nUnused EBS Volumes:")

volumes = ec2.describe_volumes(
    Filters=[
        {
            "Name": "status",
            "Values": ["available"]
        }
    ]
)

if not volumes["Volumes"]:
    print("No unused volumes found.")

for volume in volumes["Volumes"]:

    print(
        f"Volume ID: {volume['VolumeId']} "
        f"Size: {volume['Size']}GB"
    )

# ----------------------------------
# UNUSED ELASTIC IPS
# ----------------------------------

print("\nUnused Elastic IPs:")

addresses = ec2.describe_addresses()

unused_found = False

for address in addresses["Addresses"]:

    if "InstanceId" not in address:

        unused_found = True

        print(
            f"Unused Elastic IP: "
            f"{address['PublicIp']}"
        )

if not unused_found:
    print("No unused Elastic IPs.")

# ----------------------------------
# RDS
# ----------------------------------

print("\nRDS Instances:")

dbs = rds.describe_db_instances()

if not dbs["DBInstances"]:
    print("No RDS instances.")

for db in dbs["DBInstances"]:

    print(
        f"DB: {db['DBInstanceIdentifier']}"
    )

    print(
        f"Status: {db['DBInstanceStatus']}"
    )

    print("----------------------")

print("\nScan Completed.")

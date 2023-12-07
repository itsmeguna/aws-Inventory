import boto3
import csv
import io

region_name = "us-west-2"
session = boto3.session.Session()
elbv2 = session.client('elbv2')
ec2 = session.client('ec2')

def get_target_groups(arn):
    tgs = elbv2.describe_target_groups(LoadBalancerArn=arn)
    tg_string = []
    for tg in tgs["TargetGroups"]:
        tg_string.append(tg["TargetGroupName"])
    return tg_string

# Specify your desired S3 bucket name and output file path
s3_bucket_name = "playbook01"
s3_output_filepath = "elb-us-west-2.csv"

# Specify your desired local output file path
local_output_filepath = "/home/ubuntu/inventory/elb-us-west-2.csv"

# Create a CSV file in memory and write headers
csv_data = io.StringIO()
csv_writer = csv.DictWriter(csv_data, fieldnames=["Name", "Scheme", "State", "DNS Name", "Availability Zones", "Type", "TargetGroups", "Tags"])
csv_writer.writeheader()

albs = elbv2.describe_load_balancers()

for lb in albs["LoadBalancers"]:
    availability_zones = ", ".join([zone['ZoneName'] for zone in lb.get('AvailabilityZones', [])])
    target_groups = get_target_groups(lb["LoadBalancerArn"])
    
    lb_tags_response = elbv2.describe_tags(ResourceArns=[lb["LoadBalancerArn"]])
    lb_tags = lb_tags_response['TagDescriptions'][0]['Tags']
    
    csv_writer.writerow({
        "Name": lb["LoadBalancerName"],
        "Scheme": lb["Scheme"],
        "State": lb["State"]["Code"],
        "DNS Name": lb["DNSName"],
        "Availability Zones": availability_zones,
        "Type": lb["Type"],
        "TargetGroups": ", ".join(target_groups),
        "Tags": lb_tags,
    })

# Save the CSV file locally
with open(local_output_filepath, 'w', newline='') as local_file:
    local_file.write(csv_data.getvalue())


# Upload the CSV file to S3
s3 = boto3.client('s3')
s3.put_object(Bucket=s3_bucket_name, Key=s3_output_filepath, Body=csv_data.getvalue())



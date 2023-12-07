import boto3
import csv

region_name = "us-east-1"
session = boto3.session.Session()
elbv2 = session.client('elbv2')
ec2 = session.client('ec2')

def get_target_groups(arn):
    tgs = elbv2.describe_target_groups(LoadBalancerArn=arn)
    tg_string = []
    for tg in tgs["TargetGroups"]:
        tg_string.append(tg["TargetGroupName"])
    return tg_string

# Specify your desired output directory here
output_directory = "/home/ubuntu/inventory/"

# Create a CSV file and write headers
csv_filename = "elb-us-east-1.csv"
csv_filepath = f"{output_directory}/{csv_filename}"
with open(csv_filepath, mode='w', newline='') as csvfile:
    fieldnames = ["Name", "Scheme", "State", "DNS Name", "Availability Zones", "Type", "TargetGroups", "Tags"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    albs = elbv2.describe_load_balancers()

    for lb in albs["LoadBalancers"]:
        availability_zones = ", ".join([zone['ZoneName'] for zone in lb.get('AvailabilityZones', [])])
        target_groups = get_target_groups(lb["LoadBalancerArn"])
        
        lb_tags_response = elbv2.describe_tags(ResourceArns=[lb["LoadBalancerArn"]])
        lb_tags = lb_tags_response['TagDescriptions'][0]['Tags']
        
        writer.writerow({
            "Name": lb["LoadBalancerName"],
            "Scheme": lb["Scheme"],
            "State": lb["State"]["Code"],
            "DNS Name": lb["DNSName"],
            "Availability Zones": availability_zones,
            "Type": lb["Type"],
            "TargetGroups": ", ".join(target_groups),
            "Tags": lb_tags,
        })


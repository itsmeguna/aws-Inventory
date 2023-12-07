import boto3
import csv
import io

region_name = "us-west-2"  # Specify your desired AWS region
session = boto3.session.Session(region_name=region_name)
ec2 = session.client('ec2')

def get_volume_name(volume):
    for tag in volume.get("Tags", []):
        if tag["Key"] == "Name":
            return tag["Value"]
    return "N/A"

# Specify your desired output directory here
output_directory = "/home/ubuntu/inventory/"

# Create a CSV file in memory and write headers
csv_data = io.StringIO()
csv_writer = csv.DictWriter(csv_data, fieldnames=["Volume ID", "Size (GiB)", "Volume Type", "State", "Attached To", "Volume Name", "Tags"])
csv_writer.writeheader()

volumes = ec2.describe_volumes()

for volume in volumes["Volumes"]:
    volume_id = volume["VolumeId"]
    size_gib = volume["Size"]
    volume_type = volume["VolumeType"]
    state = volume["State"]
    
    attached_instance = volume.get("Attachments", [{}])[0].get("InstanceId", "")
    attached_to = attached_instance if attached_instance else "Not attached"
    
    volume_name = get_volume_name(volume)
    
    tags = volume.get("Tags", [])
    tags_dict = {tag["Key"]: tag["Value"] for tag in tags}
    
    csv_writer.writerow({
        "Volume ID": volume_id,
        "Size (GiB)": size_gib,
        "Volume Type": volume_type,
        "State": state,
        "Attached To": attached_to,
        "Volume Name": volume_name,
        "Tags": tags_dict,
    })

# Upload the CSV file to S3
s3_bucket_name = "playbook01"
s3_output_filepath = "ebs_volumes-us-west-2.csv"

s3 = boto3.client('s3')
s3.put_object(Bucket=s3_bucket_name, Key=s3_output_filepath, Body=csv_data.getvalue())

print(f"EBS volume inventory saved to S3: s3://{s3_bucket_name}/{s3_output_filepath}")


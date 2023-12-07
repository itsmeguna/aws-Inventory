import boto3
import csv
import io

region_name = "us-west-2"  # Specify your desired AWS region
session = boto3.session.Session(region_name=region_name)
ec2 = session.client('ec2')

# Specify your desired S3 bucket name and output file path
s3_bucket_name = "playbook01"
s3_output_filepath = "ami-us-west-2.csv"

# Create a CSV file in memory and write headers
csv_data = io.StringIO()
csv_writer = csv.DictWriter(csv_data, fieldnames=["AMI Name", "State", "Creation Date", "Description", "Tags"])
csv_writer.writeheader()

amis = ec2.describe_images(Owners=['self'])

for ami in amis["Images"]:
    name = ami.get("Name", "N/A")
    state = ami["State"]
    creation_date = ami["CreationDate"]
    description = ami.get("Description", "")
    
    tags = ami.get("Tags", [])
    tags_dict = {tag["Key"]: tag["Value"] for tag in tags}
    
    csv_writer.writerow({
        "AMI Name": name,
        "State": state,
        "Creation Date": creation_date,
        "Description": description,
        "Tags": tags_dict,
    })

# Upload the CSV file to S3
s3 = boto3.client('s3')
s3.put_object(Bucket=s3_bucket_name, Key=s3_output_filepath, Body=csv_data.getvalue())

print(f"AMI inventory saved to S3: s3://{s3_bucket_name}/{s3_output_filepath}")


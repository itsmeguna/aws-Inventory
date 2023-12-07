import boto3
import csv

def write_to_csv(file_path, data):
    with open(file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def get_tag_value(tags, key):
    for tag in tags:
        if tag['Key'] == key:
            return tag['Value']
    return ''

def extract_role_name_from_arn(arn):
    return arn.split('/')[-1] if '/' in arn else arn

def list_ec2_resources(region):
    bucket_name = 'playbook01'
    object_key = 'ec2-prod.csv'

    ec2_client = boto3.client('ec2', region_name=region)

    resource_data = [['Region', 'Resource Type', 'Resource ID', 'Instance Name', 'Status', 'Public IP', 'Private IP', 'Key Name', 'Instance Type', 'AMI Name', 'VPC', 'Subnet ID', 'Security Groups', 'IAM Role', 'Tags']]

    response = ec2_client.describe_instances()
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            name = get_tag_value(instance['Tags'], 'Name')
            status = instance['State']['Name']
            public_ip = instance.get('PublicIpAddress', '')
            private_ip = instance.get('PrivateIpAddress', '')
            key_name = instance.get('KeyName', '')
            instance_type = instance['InstanceType']
            ami_id = instance['ImageId']
            vpc_id = instance['VpcId']
            subnet_id = instance['SubnetId']

            image_response = ec2_client.describe_images(ImageIds=[ami_id])
            if image_response['Images']:
                ami_name = image_response['Images'][0]['Name']
            else:
                ami_name = 'Unknown AMI'

            vpc_response = ec2_client.describe_vpcs(VpcIds=[vpc_id])
            vpc_name = vpc_response['Vpcs'][0]['VpcId']

            security_groups = []
            for group in instance['SecurityGroups']:
                security_groups.append(group['GroupName'])

            iam_instance_profile_arn = instance.get('IamInstanceProfile', {}).get('Arn', 'No IAM Role')
            iam_role_name = extract_role_name_from_arn(iam_instance_profile_arn)

            tags = [{'Key': tag['Key'], 'Value': tag['Value']} for tag in instance.get('Tags', [])]

            resource_data.append([region, 'EC2 Instance', instance_id, name, status, public_ip, private_ip, key_name, instance_type, ami_name, vpc_name, subnet_id, ', '.join(security_groups), iam_role_name, tags])

    local_file_path = '/home/ubuntu/inventory/Prod-ec2.csv'
    write_to_csv(local_file_path, resource_data)

    s3_client = boto3.client('s3')
    s3_client.upload_file(local_file_path, bucket_name, object_key)

list_ec2_resources('us-west-2')


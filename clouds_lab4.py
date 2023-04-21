import boto3
from botocore.exceptions import ClientError

def create_key_pair():
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    key_pair = ec2_client.create_key_pair(KeyName="ec2-key-pair")
    private_key = key_pair["KeyMaterial"]
    with open(r"aws_ec2_key.pem", "w+") as handle:
        handle.write(private_key)



def create_instance():
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    instances = ec2_client.run_instances(
    ImageId="ami-0b0154d3d8011b0cd",
    MinCount=1,
    MaxCount=1,
    InstanceType="t4g.nano",
    KeyName="ec2-key-pair")

    print(instances["Instances"][0]["InstanceId"])
    global id_ins
    id_ins = instances["Instances"][0]["InstanceId"]




def get_public_ip(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-west-2")

    reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")

    for reservation in reservations:
        for instance in reservation['Instances']:
            print(instance.get("PublicIpAddress"))



def get_running_instances():
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    reservations = ec2_client.describe_instances(Filters=[
    {
    "Name": "instance-state-name",
    "Values": ["running"],
    },
    {
    "Name": "instance-type",
    "Values": ["t4g.nano"]
    }
    ]).get("Reservations")
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            public_ip = instance["PublicIpAddress"]
            private_ip = instance["PrivateIpAddress"]
    print(f"{instance_id}, {instance_type}, {public_ip},{private_ip}")

def stop_instance(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    print(response)

def terminate_instance(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-west-2")
    response = ec2_client.terminate_instances(InstanceIds=[instance_id])
    print(response)

def create_bucket(bucket_name, region = "us-west-2"):
    s3_client = boto3.client('s3', region_name=region)
    location = {'LocationConstraint': region}

    try:
        response = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print("Bucket created successfully.")
    except s3_client.exceptions.BucketAlreadyExists as e:
        print(f"Error creating bucket: {e}")
    except s3_client.exceptions.BucketAlreadyOwnedByYou as e:
        print(f"Error creating bucket: {e}")

def list_buckets():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    print('Existing buckets:')
    for bucket in response['Buckets']:
        print(f' {bucket["Name"]}')

def upload_file_to_s3(file_path, bucket_name, object_name=None):

    s3_client = boto3.client('s3')

    if object_name is None:
        object_name = file_path

    try:
        response = s3_client.upload_file(file_path, bucket_name, object_name)
    except Exception as e:
        print(e)
        return False

    return True


def read_from_s3(bucket_name, object_key):
    s3 = boto3.resource('s3')
    
    # Check if the bucket exists
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"Bucket {bucket_name} does not exist.")
        else:
            print(f"An error occurred while checking the bucket: {e}")
        return
    
    # Check if the object key exists in the bucket
    bucket = s3.Bucket(bucket_name)
    objs = list(bucket.objects.filter(Prefix=object_key))
    if len(objs) == 0:
        print(f"No object found in {bucket_name} with key {object_key}.")
        return
    
    obj = bucket.Object(object_key)
    
    # Read the contents of the object
    try:
        response = obj.get()
        content = response['Body'].read().decode('utf-8')
        print(content)
    except ClientError as e:
        print(f"An error occurred while reading object {object_key}: {e}")

def delete_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    
    # check if bucket exists
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        # bucket does not exist
        if e.response['Error']['Code'] == '404':
            print(f"Bucket {bucket_name} does not exist")
            return
        else:
            raise
    
    # delete all objects in the bucket
    bucket.objects.all().delete()
    
    # delete the bucket
    bucket.delete()
    
    print(f"Bucket {bucket_name} deleted successfully.")

def menu():
    print("0. create_key_pair")
    print("1. create_instance")
    print("2. get_public_ip")
    print("3. get_running_instances")
    print("4. stop_instance")
    print("5. terminate_instance")
    print("6. create_bucket")
    print("7. list_buckets")
    print("8. upload_file_to_s3")
    print("9. read_from_s3")
    print("10. delete_bucket")
    print("11. exit")
    

    choice = input("Виберіть бажану опцію за допомогою відповідного числа: ")
    
    if choice == "1":
        create_instance()
    elif choice == "2":
        get_public_ip(id_ins)
    elif choice == "3":
        get_running_instances()    
    elif choice == "4":
        stop_instance(id_ins)
    elif choice == "5":
        terminate_instance(id_ins)
    elif choice == "6":
        bucket_name = input("Enter the name for your S3 bucket: ")
        create_bucket(bucket_name)
    elif choice == "7":
        list_buckets()
    elif choice == "8":
        file_path = input("file_path: ")
        bucket_name = input("bucket_name: ")
        object_name = input("object_name: ")
        upload_file_to_s3(file_path, bucket_name, object_name)
    elif choice == "9":
        bucket_name = input("bucket_name: ")
        object_key = input("object_name: ")
        read_from_s3(bucket_name,object_key)
    elif choice == "10":
        bucket_name = input("bucket_name: ")
        delete_bucket(bucket_name)
    elif choice == "11":
        exit()
    elif choice == "0":
        create_key_pair()
    else:
        print("Некоректний ввід. Введіть число від 1 до 10.")
    menu()
menu()
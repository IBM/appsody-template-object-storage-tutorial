import ibm_boto3
from ibm_botocore.client import Config, ClientError
import configparser
import os
import shutil
import mimetypes
import os.path
from os import path

shutil.copyfile("./userapp/config.ini","config.ini")
config = configparser.ConfigParser();
found_files = config.read('config.ini');
print('Found config files:  ', sorted(found_files))
credentials_1 = {
    'IAM_SERVICE_ID': config.get('credentials','IAM_SERVICE_ID'),
    'IAM_RESOURCE_ID': config.get('credentials', 'IAM_RESOURCE_ID'),
    'IBM_API_KEY_ID': config.get('credentials','IBM_API_KEY_ID'),
    'ENDPOINT': config.get('credentials','ENDPOINT'),
    'IBM_AUTH_ENDPOINT': config.get('credentials','IBM_AUTH_ENDPOINT')
    }
print(credentials_1)

cos = ibm_boto3.client('s3',
                   ibm_api_key_id=credentials_1['IBM_API_KEY_ID'],
                   ibm_service_instance_id=credentials_1['IAM_SERVICE_ID'],
                   ibm_auth_endpoint=credentials_1['IBM_AUTH_ENDPOINT'],
                   config=Config(signature_version='oauth'),
                   endpoint_url=credentials_1['ENDPOINT'])

    
cosres = ibm_boto3.resource("s3",
                   ibm_api_key_id=credentials_1['IBM_API_KEY_ID'],
                   ibm_service_instance_id=credentials_1['IAM_RESOURCE_ID'],
                   ibm_auth_endpoint=credentials_1['IBM_AUTH_ENDPOINT'],
                   config=Config(signature_version='oauth'),
                   endpoint_url=credentials_1['ENDPOINT'])

def get_file(bucket_name, file_name):
    '''Retrieve file from Cloud Object Storage'''
    mime = mimetypes.guess_type(file_name)[0]
    print(mime)
    fileobject = cos.get_object(Bucket=bucket_name, Key=file_name)['Body'] 
    return fileobject


def put_file(bucketname, filename, filecontents):
   '''Write file to Cloud Object Storage'''
   try:
       resp = cos.put_object(Bucket=bucketname, Key=filename, Body=filecontents)
       print(resp)
       return resp
   except ClientError as be:
       print("CLIENT ERROR: {0}\n".format(be))
       return be


def get_buckets():
    '''Get the buckets in the Cloud Object Storage'''
    try:
        buckets = cosres.buckets.all()
        return buckets    
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to retrieve list buckets: {0}".format(e))

def get_files(bucket_name):
    ''' Get the files in a bucket'''
    print("Retrieving bucket contents from: {0}".format(bucket_name))
    try:
        files = cosres.Bucket(bucket_name).objects.all()
        return files
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
        return be
    except Exception as e:
        print("Unable to retrieve bucket contents: {0}".format(e))
        return e

def delete_item(bucket_name, item_name):
    ''' Delete a file on Cloud Object Storage'''
    print("Deleting item: {0}".format(item_name))
    try:
        resp = cosres.Object(bucket_name, item_name).delete()
        print("Item: {0} deleted!".format(item_name))
        return resp
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
    except Exception as e:
        print("Unable to delete item: {0}".format(e))

def delete_bucket(bucket_name):
    ''' Delete a bucket'''
    print("Deleting bucket: {0}".format(bucket_name))
    try:
        resp = cosres.Bucket(bucket_name).delete()
        print("Bucket: {0} deleted!".format(bucket_name))
        print(resp)
        return resp
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
        return be
    except Exception as e:
        print("Unable to delete bucket: {0}".format(e))
        return e

def create_bucket(bucket_name):
    ''' Create a bucket '''
    print("Creating new bucket: {0}".format(bucket_name))
    try:
        resp = cosres.Bucket(bucket_name).create(
            CreateBucketConfiguration={
                "LocationConstraint":"us-east-standard"
            }
        )
        print("Bucket: {0} created!".format(bucket_name))
        return resp
    except ClientError as be:
        print("CLIENT ERROR: {0}\n".format(be))
        return be
    except Exception as e:
        print("Unable to create bucket: {0}".format(e))
        return e


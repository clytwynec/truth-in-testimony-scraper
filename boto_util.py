# -*- coding: utf-8 -*-
import boto3

def upload_to_s3(file_data, file_path, bucket_name):
    # Create an S3 client
    s3 = boto3.client('s3')
    res = s3.put_object(
        Bucket=bucket_name,
        Key=file_path,
        Body=file_data,
        ACL='public-read',
        ContentType='application/pdf',
    )
    return '{}/{}/{}'.format(s3.meta.endpoint_url, bucket_name, file_path)



# this script reffers the URL below:
# https://github.com/awslabs/aws-python-sample/blob/master/s3_sample.py

import boto3

# set S3 backet
s3client   = boto3.client('s3')
backetName = 'ct-prototype'

# put data to S3
imgName  = 'heiji.jpg'
imgData  = open(imgName, 'rb')
s3folder = 'tmp'
s3key    = s3folder + '/' + imgName
s3client.put_object(Bucket=backetName, Key=s3key, Body=imgData)

# get url
url = s3client.generate_presigned_url('get_object', {'Bucket': backetName, 'Key': s3key})
print('\nTry this URL in your browser to download the object:')
print(url)

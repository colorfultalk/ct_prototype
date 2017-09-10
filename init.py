# set constant values
# To check current flow
REGISTER = 'REGISTER'
EDIT     = 'EDIT'
VERIFY   = 'VERIFY'

# To check which phase a user is on
IMAGE       = 'IMAGE'
DESCRIPTION = 'DESCRIPTION'
LOCATION    = 'LOCATION'
ALL_SET     = 'ALL_SET'
START       = 'START'

# set constants for test
APPNAME = 'still-refuge-57534'
USERNAME = 'u19022'
PASSWORD = 'naistnaist'

# set aws s3 bucket
import boto3 # for handling aws s3
BUCKET_NAME = 'ct-prototype'
s3          = boto3.resource('s3')
bucket      = s3.Bucket(BUCKET_NAME) # BUCKET_NAME is defined in init.py

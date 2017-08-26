# for handling image
import io
from io import BytesIO
from PIL import Image
import random

# for handling aws s3
import boto3
bucketName = 'ct-prototype'
s3 = boto3.resource('s3')
bucket = s3.Bucket(bucketName)

def random_string(length, seq='0123456789abcdefghijklmnopqrstuvwxyz'):
    sr = random.SystemRandom()
    return ''.join([sr.choice(seq) for i in range(length)])

# retrieve image that user sent from line message content
def retrieve_image_from_content( msg_content , save_img_size = (1000, 680) ):
    img_bin = io.BytesIO( msg_content )
    pil_img = Image.open( img_bin )

    # resize
    pil_img.thumbnail(saveImgSize, Image.ANTIALIAS)
    horizontal_padding = (saveImgSize[0] - pil_img.size[0]) / 2
    vertical_padding = (saveImgSize[1] - pil_img.size[1]) / 2
    pil_img = pil_img.crop(
            (
                -horizontal_padding,
                -vertical_padding,
                pil_img.size[0] + horizontal_padding,
                pil_img.size[1] + vertical_padding
            )
        )
    return( pil_img )

# upload s3
def upload_to_s3( msg_content, s3_bucket, obj_key_name = random_string(15) ):

    # retrieve image
    pil_img = retrieve_image_from_content( msg_content )

    # format image
    out = BytesIO()
    pil_img.save(out, "JPEG", optimize=True)

    # s3 upload
    key = 'tmp/' + obj_key_name + '.jpg'
    obj = s3_bucket.Object( key )
    response = obj.put(
    Body = out.getvalue(),
        ContentType = 'image/png'
    )

    return( response )

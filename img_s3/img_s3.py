# for handling image
import io
from io import BytesIO
from PIL import Image
import random

# s3 client
import boto3
s3 = boto3.client('s3')
IMG_EXPIREIN = 3600 * 24 * 365 # 3600 means 1 hour

def random_string(length, seq='0123456789abcdefghijklmnopqrstuvwxyz'):
    sr = random.SystemRandom()
    return ''.join([sr.choice(seq) for i in range(length)])

# retrieve image that user sent from line message content
def retrieve_image_from_content( msg_content , save_img_size = (1000, 680) ):
    img_bin = io.BytesIO( msg_content )
    pil_img = Image.open( img_bin )

    # resize
    pil_img.thumbnail(save_img_size, Image.ANTIALIAS)
    horizontal_padding = (save_img_size[0] - pil_img.size[0]) / 2
    vertical_padding = (save_img_size[1] - pil_img.size[1]) / 2
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
        ContentType = 'image/jpeg'
    )

    # get access url
    presigned_url = s3.generate_presigned_url(
            ClientMethod = 'get_object',
            Params = {'Bucket' : s3_bucket.name, 'Key' : key},
            ExpiresIn = IMG_EXPIREIN,
            HttpMethod = 'GET'
            )

    return( presigned_url )

# for handling image
import io
from io import BytesIO
from PIL import Image
import random

def random_string(length, seq='0123456789abcdefghijklmnopqrstuvwxyz'):
    sr = random.SystemRandom()
    return ''.join([sr.choice(seq) for i in range(length)])

# retrieve image that user sent from line message content
def retrieve_image_from_content( msg_content , save_img_size = (1000, 680) ):
    img_bin = io.BytesIO( msg_content )
    pil_img = Image.open( img_bin ).resize( saveImgSize )
    return( pil_img )

# upload s3
def upload_to_s3( msg_content, s3_bucket, obj_key_name = random_string(15) ):

    # retrieve image
    pil_img = retrieve_image_from_content( msg_content )

    # format image
    out = BytesIO()
    pil_img.save(out, "JPEG", optimize=True)

    # s3 upload
    obj = bucket.Object( obj_key_name )
    response = obj.put(
    Body = out.getvalue(),
        ContentType = 'image/png'
    )

    return( response )

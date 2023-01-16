import requests
import pytest
import json
from src import config
from src.tokens import decode_jwt
from src.helper_functions import return_user_by_id
from src.error import InputError, AccessError

@pytest.fixture
def clear():
    requests.delete(config.url + 'clear/v1', json={})
    return
    
def create_valid_token():
    registered_user = requests.post(config.url + 'auth/register/v2', json={'email': 'student@gmail.com','password': 'sunnyday','name_first': 'Justin','name_last': 'Gordon'})
    registered_user = registered_user.json()
    return registered_user

  
# when the return status from retrieving image url is other than 200 - invalid
def test_invalid_image_url(clear):
    
    token = create_valid_token() 
    invalid_url = "https://www.myer.com.au/"
    
    output = requests.post(config.url + 'user/profile/uploadphoto/v1', json={'token': token['token'], 'img_url': invalid_url, 'x_start': 0, 'y_start': 0, 'x_end': 500, 'y_end': 500})
    assert output.status_code == 400
    
# the croping dimesions aren't reasonable or within the picture dimensions
def test_dimensions_out_of_bound(clear):
    
    token = create_valid_token() 
    valid_url = "http://sample-videos.com/img/Sample-jpg-image-50kb.jpg"
    
    output_x = requests.post(config.url + 'user/profile/uploadphoto/v1', json={'token': token['token'], 'img_url': valid_url, 'x_start': -500, 'y_start': 0, 'x_end': 500, 'y_end':500})
    assert output_x.status_code == 400
    
    output_y = requests.post(config.url + 'user/profile/uploadphoto/v1', json={'token': token['token'], 'img_url': valid_url, 'x_start': 0, 'y_start': -500, 'x_end': 500, 'y_end':500})
    assert output_y.status_code == 400
    
    output_x_y = requests.post(config.url + 'user/profile/uploadphoto/v1', json={'token': token['token'], 'img_url': valid_url, 'x_start': -500, 'y_start': -500, 'x_end': 500, 'y_end':500})
    assert output_x_y.status_code == 400
    
# x_end <= x_start and y_end <= y_start
def test_invalid_x_y_end_dimensions(clear):
    
    token = create_valid_token() 
    valid_url = "http://sample-videos.com/img/Sample-jpg-image-50kb.jpg"
    
    # x_end < x_start
    output_x_less = requests.post(config.url + 'user/profile/uploadphoto/v1', json={'token': token['token'], 'img_url': valid_url, 'x_start': 200, 'y_start': 200, 'x_end': 15, 'y_end':500})
    assert output_x_less.status_code == 400
 
    # x_end == x_start
    output_x_equal = requests.post(config.url + 'user/profile/uploadphoto/v1', json={'token': token['token'], 'img_url': valid_url, 'x_start': 200, 'y_start': 200, 'x_end': 200, 'y_end':500})
    assert output_x_equal.status_code == 400   
    
    # y_end < y_start
    output_y_less = requests.post(config.url + 'user/profile/uploadphoto/v1', json={'token': token['token'], 'img_url': valid_url, 'x_start': 200, 'y_start': 200, 'x_end': 500, 'y_end':90})
    assert output_y_less.status_code == 400
    
    # y_end == y_start
    output_y_equal = requests.post(config.url + 'user/profile/uploadphoto/v1', json={'token': token['token'], 'img_url': valid_url, 'x_start': 100, 'y_start': 100, 'x_end': 600, 'y_end':100})
    assert output_y_equal.status_code == 400

# image from url is not in a form of JPEG
def test_invalid_image_format(clear):

    token = create_valid_token()
    png_url = "http://pngimg.com/uploads/dog/dog_PNG50411.png"

    output_png = requests.post(config.url + 'user/profile/uploadphoto/v1', json={'token': token['token'], 'img_url': png_url, 'x_start': 200, 'y_start': 200, 'x_end':500, 'y_end':500})
    assert output_png.status_code == 400

# successful case    
def test_successful_image_croping(clear):

    token = create_valid_token() 
    valid_url = "http://sample-videos.com/img/Sample-jpg-image-50kb.jpg"
    
    output_success = requests.post(config.url + 'user/profile/uploadphoto/v1', json={'token': token['token'], 'img_url': valid_url, 'x_start': 0, 'y_start': 0, 'x_end':100, 'y_end':100})
    assert output_success.status_code == 200
    
    output_data = output_success.json()
    assert output_data == {}

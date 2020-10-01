from aip import AipImageCensor

""" 你的 APPID AK SK """
APP_ID = '10699663'
API_KEY = 'h6laYDwumS3UzwiCCjYGQPkP'
SECRET_KEY = 'd9GFQc6ntq0pBGHRv6YrFxxfEfDYq3QH'

client = AipImageCensor(APP_ID, API_KEY, SECRET_KEY)

def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

img = get_file_content('cb.jpg')
result = client.imageCensorUserDefined(img)
print(result)
# if isinstance(result, dict):
#     if result.has_key('conclusion'):
#         if result['conclusion'] != u'合规':
#             for data in result['data']:
#                 print (data['msg'])
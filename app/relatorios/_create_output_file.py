from django.conf import settings


def create_output_file(file_name):
    """
    Cria o path para o arquivo no diretório /media.
    OBS.: O file_name deve conter o nome do arquivo com extensão!
    :rtype: str
    """
    media_stor = settings.MEDIA_ROOT
    media_url = settings.MEDIA_URL

    if not media_stor.endswith('/'):
        media_stor += '/'
    file_location = f'{media_stor}{file_name}'

    if not media_url.endswith('/'):
        media_url += '/'
    file_url = media_url + file_name

    return file_location, file_url

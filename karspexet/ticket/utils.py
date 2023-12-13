import base64
import io

import pyqrcode


def qr_code_as_png_data_url(request):
    buffer = io.BytesIO()
    url = pyqrcode.create(request.build_absolute_uri())
    url.png(buffer, scale=4)
    encoded = base64.b64encode(buffer.getvalue())  # Creates a bytes object
    return f"data:image/png;base64,{encoded.decode()}"

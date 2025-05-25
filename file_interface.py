import os
import json
import base64
from glob import glob

class FileInterface:
    def __init__(self):
        self.base_dir = os.path.abspath('files')
        os.makedirs(self.base_dir, exist_ok=True)

    def list(self, params=[]):
        try:
            filelist = [
                os.path.basename(f) for f in glob(os.path.join(self.base_dir, '*.*'))
            ]
            return dict(status='OK', data=filelist)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def get(self, params=[]):
        try:
            filename = params[0]
            if filename == '':
                return dict(status='ERROR', data='Filename kosong')

            filepath = os.path.join(self.base_dir, os.path.basename(filename))
            with open(filepath, 'rb') as fp:
                isifile = base64.b64encode(fp.read()).decode()
            return dict(status='OK', data_namafile=filename, data_file=isifile)
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def upload(self, params=[]):
        try:
            filename = os.path.basename(params[0])
            filepath = os.path.join(self.base_dir, filename)
            filedata = base64.b64decode(params[1])
            with open(filepath, 'wb') as f:
                f.write(filedata)
            return dict(status='OK', data=f"{filename} berhasil diupload")
        except Exception as e:
            return dict(status='ERROR', data=str(e))

    def delete(self, params=[]):
        try:
            filename = os.path.basename(params[0])
            filepath = os.path.join(self.base_dir, filename)
            os.remove(filepath)
            return dict(status='OK', data=f"{filename} deleted")
        except Exception as e:
            return dict(status='ERROR', data=str(e))

if __name__ == '__main__':
    f = FileInterface()
    print(f.list())
    print(f.get(['pokijan.jpg']))

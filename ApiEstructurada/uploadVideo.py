import os

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'}


class UploadVideo(): 
    def __init__(self, request, flash,redirect,url_for):
            self.request = request
            self.flash = flash
            self.redirect = redirect
            self.url_for = url_for
            pass
         
    def allowed_file(filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    def upload_file(self):
         return True
    
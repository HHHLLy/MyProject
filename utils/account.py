from bcrypt import hashpw,gensalt
from pycket.session import SessionMixin
def pas_encryption(pwd,encrypw=None,b=True):
    if b:
        salt = gensalt(12)
        pwd = hashpw(pwd.encode("utf8"),salt)
        return pwd

    else:
        return  hashpw(pwd.encode("utf8"),encrypw.encode("utf8")) == encrypw.encode("utf8")




__all__ = ('CertificatesFileNotFound',)


# Define a class for certificate errors
class CertificatesFileNotFound(Exception):
    """
    The base certificates expected to come from the certifi package.   Is it installed?
    """
    pass

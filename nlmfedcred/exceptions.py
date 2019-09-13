# Define a class for certificate errors
class CertificatesFileNotFound(Exception):
    """
    The base certificates expected to come from the certifi package.   Is it installed?
    """
    pass

# Define a class for no such profile
class ProfileNotFound(Exception):
    """
    The profile you named does not exist in $HOME/.getawscreds
    """
    pass

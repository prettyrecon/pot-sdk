import os
if 'PARENT_SITE' in os.environ:
    import site
    site.addsitedir(os.environ['PARENT_SITE'])


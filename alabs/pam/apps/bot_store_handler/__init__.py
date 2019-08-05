BOT_API_PREFIX = 'api'
BOT_API_VERSION = 'v1.0'
BOT_API_NAME = 'bot'

if '__main__' == __name__:
    from .test_server import main
    main()
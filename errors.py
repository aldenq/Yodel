class YodelError(BaseException):
    '''
    '''
    def __init__(message):
        super(message)

class YodelTypeError(YodelError):
    '''
    '''
    def __init__(typeA, typeB):
        super(f"Could not assign type '{typeA}' to field of type '{typeB}'")
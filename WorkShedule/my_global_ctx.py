from datetime import datetime

def get_version_and_time_context(request):
    version = (1, 0)
    time = datetime.now()
    return {'version': version,
            'time': time}

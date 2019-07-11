from datetime import datetime

def get_version_and_time_context(request):
    time = datetime.now()
    return {'time': time}

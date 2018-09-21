broker_url='pyamqp://guest@localhost//'
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Kolkata'
enable_utc = True
beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler'
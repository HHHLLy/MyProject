from celery import Celery
import  os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'djproject.settings'
app = Celery('codes')
#导入celery配置
app.config_from_object('celery_tasks.config')
#自定义注册任务
app.autodiscover_tasks(['celery_tasks.sms'])

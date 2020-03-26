import requests
import logging

from django.shortcuts import render
from django.utils.encoding import escape_uri_path
from django.views import View
from django.conf import settings
from django.http import FileResponse,Http404


from .models import Doc

logger = logging.getLogger('django')

def doc_index(request):
    """"""
    docs = Doc.objects.defer('author','create_time','update_time','is_delete').filter(is_delete=False)
    return render(request,'doc/docDownload.html',locals())


# 下载
# 请求方式:  get
# 传参 id
# 返回给用户 文件, FileResponse

# id >> 从数据库拿到文件地址  >>  文件对象   >>  FileResponse(res)

class DocDownload(View):
    """
    /doc/<int:doc_id>/
    """
    def get(self,request,doc_id):
        doc = Doc.objects.only('file_url').filter(is_delete=False,id=doc_id).first()
        if doc:
            file_url = doc.file_url
            doc_url = settings.SITE_DOMAIN_PORT + file_url
            try:
                file = requests.get(doc_url,stream=True)
                res = FileResponse(file)
                # with open('admin.py','r') as f:
                #     file_content = f.read()
                # res = FileResponse(file_content)

            except Exception as e:
                logger.info('获取文档内容出现异常:{}'.format(e))
                raise Http404('文档下载异常!')

            ex_name = doc_url.split('.')[-1]
            if not ex_name:
                raise Http404('文档URL异常!')
            else:
                ex_name = ex_name.lower()
            if ex_name == "pdf":
                res["Content-type"] = "application/pdf"
            elif ex_name == "zip":
                res["Content-type"] = "application/zip"
            elif ex_name == "doc":
                res["Content-type"] = "application/msword"
            elif ex_name == "xls":
                res["Content-type"] = "application/vnd.ms-excel"
            elif ex_name == "docx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ex_name == "ppt":
                res["Content-type"] = "application/vnd.ms-powerpoint"
            elif ex_name == "pptx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"

            # doc_filename = doc_url.split('/')[-1]
            doc_filename = escape_uri_path(doc_url.split('/')[-1])
            #用来转码文件名以便在网站上下载时文件名自动以此命名 转码后例：
            # WARNING basehttp 154 "GET //media/%E6%B5%81%E7%95%85%E7%9A%84Python.pdf HTTP/1.1" 404 3167
            # http1.1 中的规范
            # 设置为inline，会直接打开
            # attachment 浏览器会开始下载
            res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_filename)
            return res
        else:
            raise Http404('文档不存在!')

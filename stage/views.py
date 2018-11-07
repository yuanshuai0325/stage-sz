from django.shortcuts import render
from django.http import JsonResponse
from stage.models import Device, User, Use
#from werkzeug.security import generate_password_hash, check_password_hash

#import jwt
import os
import time
import shutil

# Create your views here.

def add_device(request):
    name = request.GET['name']
    if Device.objects.filter(name=name):
        ret = "设备 %s 已存在" % name
        return JsonResponse({'exec':'false', 'ret': ret})
    try:
        adddata = Device(name=name)
        adddata.save()
        ret = "设备 %s 添加成功" % name
        return JsonResponse({'exec': 'true', 'ret': ret})
    except Exception as e:
        ret = "设备 %s 添加失败" % name
        return JsonResponse({'exec':'false', 'ret': ret})

def search_device(request):
    all_device = []
    try:
        data = Device.objects.all()
        for item in data:
            all_device.append({'id' : item.id, 'name': item.name})
        return JsonResponse({'exec':'true','ret': all_device})
    except Exception as e:
        ret = "设备名称获取失败 %s " % e
        return JsonResponse({'exec':'false', 'ret':ret})

def add_use(request):
    data = request.POST.lists()
    for item in data:
        if 'name' in item:
            name = item[1]
        if 'device' in item:
            device = item[1]
        if 'sn' in item:
            sn = item[1]
        if 'comment' in item:
            comment = item[1]
    if len(device) != len(sn):
        ret = "设备数量与sn数量不等"
        return JsonResponse({'exec':'false', 'ret':ret})
    try:
        if User.objects.filter(name=name[0]):
            ret = "用户 %s 已存在" % name[0]
        else:
            adddata = User(name=name[0])
            adddata.save()
            ret = "用户 %s 添加成功" % name[0]
    except Exception as e:
        ret = "用户 %s 添加失败" % name
        return JsonResponse({'exec':'false', 'ret': ret})
    try:
        day = time.strftime("%Y%m%d")
        data = User.objects.get(name=name[0])
        id = data.id
        for item in sn:
            if Use.objects.filter(sn=item):
                ret += ',sn 为 %s 已在用' % item
                return JsonResponse({'exec':'false', 'ret': ret})
        for sub,item in enumerate(device):
            adddata = Use(sn=sn[sub],comment=comment[sub],day=day,device_id=item,user_id=id)
            adddata.save()
            ret += ',数据 %s 添加成功' % sub
        return JsonResponse({'exec':'true', 'ret': ret})
    except Exception as e:
        ret += ",数据添加失败" % name
        return JsonResponse({'exec':'false', 'ret': ret})

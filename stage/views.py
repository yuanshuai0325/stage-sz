from django.shortcuts import render
from django.http import JsonResponse
from stage.models import Device, User, Use, Storage
#from werkzeug.security import generate_password_hash, check_password_hash

# django 后台User表 Token表
from django.contrib.auth.models import User as Auser
from rest_framework.authtoken.models import Token

# Token认证
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes

# django 密码校验
from django.contrib.auth.hashers import make_password, check_password

#import jwt
import os
import time
import shutil

# Create your views here.

def login(request):
    name = request.POST.get('name')
    passwd = request.POST.get('passwd')
    try:
        #dj_passwd = make_password(passwd, None, 'pbkdf2_sha256')
        getpass = Auser.objects.filter(username=name).values("password")[0]['password']
        if check_password(passwd,getpass):
            userid = Auser.objects.filter(username=name).values('id')[0]['id']
            token = 'token ' + Token.objects.filter(user_id=userid).values('key')[0]['key'] if Token.objects.filter(user_id=userid) else  Token.objects.create(user_id=userid)
            ret = {'token': token,}
            print(ret)
            return JsonResponse({'exec':'true', 'ret': ret})
        else:
            return JsonResponse({'exec':'false', 'ret': "用户不存在或密码错误"})
    except Exception as e:
        return JsonResponse({'exec':'false', 'ret': '内部错误'})

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
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

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def sdevice(request):
    all_device = []
    try:
        data = Device.objects.all()
        for item in data:
            all_device.append({'id' : item.id, 'name': item.name})
        return JsonResponse({'exec':'true','ret': all_device})
    except Exception as e:
        ret = "设备名称获取失败 %s " % e
        return JsonResponse({'exec':'false', 'ret':ret})

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
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
            if Storage.objects.filter(sn=sn[sub]):
                Storage.objects.filter(sn=sn[sub]).delete()
                ret += ',sn 为 %s 从库存中移除' % sn[sub]
            adddata = Use(sn=sn[sub],comment=comment[sub],day=day,device_id=item,user_id=id)
            adddata.save()
            ret += ',数据 %s 添加成功' % sub
        return JsonResponse({'exec':'true', 'ret': ret})
    except Exception as e:
        ret += ", %s 数据添加失败" % name
        return JsonResponse({'exec':'false', 'ret': ret})

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def add_storage(request):
    data = request.POST.lists()
    ret = '库存添加, '
    for item in data:
        if 'device' in item:
            device = item[1]
        if 'sn' in item:
            sn = item[1]
        if 'comment' in item:
            comment = item[1]
    if len(device) != len(sn):
        ret += "设备数量与sn数量不等"
        print(1)
        return JsonResponse({'exec':'false', 'ret':ret})
    try:
        day = time.strftime("%Y%m%d")
        for item in sn:
            if Use.objects.filter(sn=item):
                ret += ',sn 为 %s 已在用' % item
                print(2)
                print(ret)
                return JsonResponse({'exec':'false', 'ret': ret})
            if Storage.objects.filter(sn=item):
                ret += ',sn 为 %s 已在库存中' % item
                return JsonResponse({'exec':'false', 'ret': ret})
        for sub,item in enumerate(device):
            adddata = Storage(sn=sn[sub],comment=comment[sub],day=day,device_id=item)
            adddata.save()
            ret += ',数据 %s 添加成功' % sub
            print(3)
        return JsonResponse({'exec':'true', 'ret': ret})
    except Exception as e:
        ret += ", %s 数据添加失败" % name
        return JsonResponse({'exec':'false', 'ret': ret})

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def search_device(request):
    sn = request.POST.get("sn")
    select = request.POST.get("select")
    ret = '查找'
    if select == "false":
        if Use.objects.filter(sn=sn):
            data = Use.objects.filter(sn=sn).values('id','sn','comment','day','user__name','device__name')
        else:
            data = Storage.objects.filter(sn=sn).values('id','sn','comment','day','device__name')
    else:
        if User.objects.filter(name=sn):
            id = User.objects.get(name=sn).id
            data = Use.objects.filter(user=id).values('id','sn','comment','day','user__name','device__name')
        else:
            ret = '用户不存在'
            return JsonResponse({'exec':'false', 'ret': ret})
    data = list(data)
    for item in data:
        if item.get('user__name'):
            item['user'] = item.pop('user__name')
        item['device'] = item.pop('device__name')
    if not data:
        ret = "未查询到符合条目"
        return JsonResponse({'exec':'false', 'ret': ret})
    ret = data
    return JsonResponse({'exec':'true', 'ret': ret})

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def search_all_use(request):
    try:
        curpage = int(request.POST.get("curpage"))
        pagesize = int(request.POST.get("pagesize"))
        ret = []
        data = Use.objects.all()
        total = data.count()
        data = data[(curpage-1) * pagesize: curpage * pagesize]
        for item in data:
            ret.append({"id":item.id,"user":item.user.name,"sn":item.sn,"comment":item.comment,"day":item.day,"device":item.device.name})
        ret.append({"total":total})
        return JsonResponse({'exec':'true', 'ret': ret})
    except Exception as e:
        print(e)
        ret = '获取所有使用列表失败'
        return JsonResponse({'exec':'false', 'ret': ret})

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def search_all_storage(request):
    try:
        curpage = int(request.POST.get("curpage"))
        pagesize = int(request.POST.get("pagesize"))
        ret = []
        data = Storage.objects.all()
        total = data.count()
        data = data[(curpage-1) * pagesize: curpage * pagesize]
        for item in data:
            ret.append({"id":item.id,"sn":item.sn,"comment":item.comment,"day":item.day,"device":item.device.name})
        ret.append({"total":total})
        return JsonResponse({'exec':'true', 'ret': ret})
    except Exception as e:
        ret = '获取所有库存列表失败'
        return JsonResponse({'exec':'false', 'ret': ret})

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def update_device(request):
    id = request.POST.get('id')
    user = request.POST.get('user')
    device = request.POST.get('device')
    sn = request.POST.get('sn')
    comment = request.POST.get('comment')
    day = request.POST.get('day')
    print(id,user,device,sn,comment,day)
    ret = ''
    try:
        deviceid = Device.objects.filter(name=device).values("id")[0]["id"]
        if user != "undefined":
            if User.objects.filter(name=user):
                print(1)
                ret += "用户 %s 已存在" % user
            else:
                adddata = User(name=user)
                adddata.save()
                ret += "用户 %s 添加成功" % user
                print(2)
            userid = User.objects.filter(name=user).values("id")[0]["id"]
            if Use.objects.filter(id=id).values("user__name")[0]["user__name"] == user:
                Use.objects.filter(id=id).update(sn=sn,comment=comment,user_id=userid,device_id=deviceid)
            else:
                day = time.strftime("%Y%m%d")
                Use.objects.filter(id=id).update(sn=sn,comment=comment,day=day,user_id=userid,device_id=deviceid)
        else:
            Storage.objects.filter(id=id).update(sn=sn,comment=comment,device_id=deviceid)
        ret += ",修改成功"
        return JsonResponse({'exec':'true', 'ret': ret})
    except Exception as e:
        ret += ",修改失败"
        return JsonResponse({'exec':'false', 'ret': ret})


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def update_use(request):
    id = request.POST.get("id")
    user = request.POST.get("user")
    device = request.POST.get('device')
    sn = request.POST.get('sn')
    comment = request.POST.get('comment')
    day = time.strftime("%Y%m%d")
    ret = ''
    try:
        deviceid = Device.objects.filter(name=device).values("id")[0]["id"]
        if User.objects.filter(name=user):
            ret += "用户 %s 已存在" % user
        else:
            adddata = User(name=user)
            adddata.save()
            ret += "用户 %s 添加成功" % user
        userid = User.objects.filter(name=user).values("id")[0]["id"]
        Storage.objects.filter(id=id).delete()
        adddata = Use(sn=sn,comment=comment,day=day,user_id=userid,device_id=deviceid)
        adddata.save()
        return JsonResponse({'exec':'true', 'ret': ret})
    except Exception as e:
        ret += ",转使用失败"
        return JsonResponse({'exec':'false', 'ret': ret})

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def update_storage(request):
    id = request.POST.get("id")
    user = request.POST.get("user")
    device = request.POST.get('device')
    sn = request.POST.get('sn')
    comment = request.POST.get('comment')
    day = time.strftime("%Y%m%d")
    ret = ''
    try:
        deviceid = Device.objects.filter(name=device).values("id")[0]["id"]
        Use.objects.filter(id=id).delete()
        adddata = Storage(sn=sn,comment=comment,day=day,device_id=deviceid)
        adddata.save()
        return JsonResponse({'exec':'true', 'ret': ret})
    except Exception as e:
        ret += ",转库存失败"
        return JsonResponse({'exec':'false', 'ret': ret})

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def update_delete(request):
    try:
        id = request.POST.get("id")
        user = request.POST.get("user")
        if user in ['','undefined']:
            Storage.objects.filter(id=id).delete()
            ret = "从库存中移除"
        else:
            Use.objects.filter(id=id).delete()
            ret = "从使用列表中移除"
        return JsonResponse({'exec':'true', 'ret': ret})
    except Exception as e:
        ret = "删除失败"
        return JsonResponse({'exec':'false', 'ret': ret})

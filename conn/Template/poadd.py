import os
import re
import time

from conn.Template.ancestors import Father
from conn.ql.ql import QL
from conn.tools.sql import Sql

conn = Sql()
ql = QL()
father = Father()


def ym_change(li: list):
    """
    根据用户表单提交的值往conn.yml添加内容
    :param li: 表单返回的数组
    :return:
    """
    father.marking_time()
    st = ''
    # 任务是否去重复
    if len(li) == 4:
        father.revise_Config("deduplication", 1)
        st += '任务不去重复'
    elif len(li) == 5:
        father.revise_Config("deduplication", 0)
        st += '任务去重复'
    if li[0] != '':
        if str(li[0]).isdigit():
            father.revise_Config("Administrator", int(li[0]))
            st += f' 你设置机器人的管理员是: {li[0]} '
        else:
            return [0,
                    "机器人交互的ID必须是数字,如果不知道请 https://t.me/InteIJ 群回复/id@KinhRoBot 查看自己ID，所有内容请重新填写"]
    if li[1] != '':
        father.revise_Config("Token", li[1])
        st += f' 机器人密钥添加成功'
    if li[2] != '':
        father.revise_Config("Proxy.Proxy", li[2])
        st += f'代理添加成功'
    if li[3] != '':
        tg_url = re.findall('^(http.*)', li[3])
        if tg_url:
            father.revise_Config("Proxy.TG_API_HOST", tg_url[0])
            st += f'反代添加成功'
    # 把时间更新
    os.environ['marking_time'] = str(int(time.time()))
    return [0, st]


def upgrade(sun: int):
    """
    根据sun的值不同采用不同的方式升级
    :param sun: 0 or 1
    :return:
    """
    time.sleep(3)
    if int(sun) == 0:
        print("不保留配置更新")
        os.system("sh /root/UpdateAll.sh")
    elif int(sun) == 1:
        print("保留配置更新")
        os.system("sh /root/UpdateAll.sh 1")


def to_stop(sun: int):
    """
    禁止活动任务脚本
    根据sun的值不同采用不同的方式禁用
    :param sun: 1 禁用所有 别的禁用活动
    :return:
    """
    try:
        st = ""
        lis = set()
        lines = conn.selectAll(table=conn.surface[0])
        value1 = conn.selectAll(table=conn.surface[3], where=f"state=0")
        if not value1:
            return f'没有可正常执行的青龙'
        # 循环所有青龙
        for ql_tk in value1:
            js = father.read(ql_tk[5])
            st += ql_tk[0]
            if sun == 0:
                for i in js.keys():
                    if js[i] == 1:
                        continue
                    for j in range(len(js[i]) - 1):
                        lis.add(js[i][list(js[i])[j]]['id'])
            # 循环数据库
            for i in lines:
                # 跳过不在json文件的脚本
                if not (i[2] in js):
                    continue
                for j in js[i[2]].keys():
                    if js[i[2]][j]['isDisabled'] == 0:
                        lis.add(js[i[2]][j]['id'])
            st += f": 禁止任务成功禁用ID{list(lis)}\n" if ql.disable(list(lis),
                        ql_tk) == 0 else f": 禁止任务失败或没有可禁用任务\n"
        return st
    except Exception as e:
        return '异常信息' + str(e)

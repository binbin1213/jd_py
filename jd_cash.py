#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/8 5:43 下午
# @File    : jd_cash.py
# @Project : jd_scripts
# @Desc    : 签到领现金
import aiohttp
import asyncio

import json
from urllib.parse import quote, unquote
from utils.console import println
from utils.process import process_start
from config import JD_CASH_SHARE_CODE


class JdCash:
    """
    签到领现金
    """
    headers = {
        'Accept-Language': 'zh-cn',
        'Accept-Encoding': 'gzip, deflate, br',
        'Host': 'api.m.jd.com',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Referer': 'http://wq.jd.com/wxapp/pages/hd-interaction/index/index',
    }

    def __init__(self, pt_pin, pt_key):
        """
        :param pt_pin:
        :param pt_key:
        """
        self._cookies = {
            'pt_pin': pt_pin,
            'pt_key': pt_key,
        }
        self._pt_pin = unquote(pt_pin)
        self._code = None

    async def request(self, session, function_id, body=None):
        """
        :param function_id:
        :param body:
        :return:
        """
        if body is None:
            body = {}
        url = 'https://api.m.jd.com/client.action?functionId={}&body={}' \
              '&appid=CashRewardMiniH5Env&clientVersion=9.2.8'.format(function_id, quote(json.dumps(body)))
        try:
            response = await session.get(url=url)
            text = await response.text()
            data = json.loads(text)
            return data
        except Exception as e:
            println('{}, 获取服务器数据失败:{}!'.format(self._pt_pin, e.args))
            return {
                'code': 9999,
                'data': {
                    'bizCode': 9999
                }
            }

    async def get_task_list(self, session):
        """
        :param session:
        :return:
        """
        try:
            session.headers.add('Host', 'api.m.jd.com')
            session.headers.add('Content-Type', 'application/x-www-form-urlencoded')
            session.headers.add('User-Agent',
                                'okhttp/3.12.1;jdmall;android;version/10.0.6;build/88852;screen/1080x2293;os/11'
                                ';network/wifi;')
            url = 'https://api.m.jd.com/client.action?functionId=cash_homePage&clientVersion=10.0.6&build=88852&client' \
                  '=android&d_brand=realme&d_model=RMX2121&osVersion=11&screen=2293*1080&partner=oppo&oaid=&openudid' \
                  '=a27b83d3d1dba1cc&eid=eidA1a01812289s8Duwy8MyjQ9m/iWxzcoZ6Ig7sNGqHp2V8/mtnOs' \
                  '+KCpWdqNScNZAsDVpNKfHAj3tMYcbWaPRebvCS4mPPRels2DfOi9PV0J+/ZRhX&sdkVersion=30&lang=zh_CN&uuid' \
                  '=a27b83d3d1dba1cc&aid=a27b83d3d1dba1cc&area=19_1601_36953_50397&networkType=wifi&wifiBssid=unknown' \
                  '&uts=0f31TVRjBStRmxA4qmf9RVgENWVO2TGQ2MjkiPwRvZZIAsHZydeSHYcTNHWIbLF17jQfBcdAy' \
                  '%2BSBzhNlEJweToEyKpbS1Yp0P0AKS78EpxJwB8v%2BZSdypE%2BhFoHHlcMyF4pc0QIWs%2B85gCH%2BHp9' \
                  '%2BfP8lKG5QOgoTBOjLn0U5UOXWFvVJlEChArvBygDg6xpmSrzN6AMVHTXrbpV%2FYbl4FQ%3D%3D&uemps=0-0&harmonyOs' \
                  '=0&st=1625744661962&sign=c8b023465a9ec1e9b912ac3f00a36377&sv=110&body={}'.format(
                quote(json.dumps({})))
            response = await session.post(url=url)
            text = await response.text()
            data = json.loads(text)
            if data['code'] != 0 or data['data']['bizCode'] != 0:
                return []
            return data['data']['result']['taskInfos']
        except Exception as e:
            println('{}, 获取任务列表失败:{}!'.format(self._pt_pin, e.args))
            return []

    async def init(self, session):
        """
        获取首页数据
        :return:
        """
        data = await self.request(session, 'cash_mob_home')
        if data['code'] != 0 or data['data']['bizCode'] != 0:
            println('{}, 初始化数据失败!'.format(self._pt_pin))
            return False
        data = data['data']['result']
        self._code = data['inviteCode'] + '@' + data['shareDate']
        return True

    async def do_tasks(self, session, times=3):
        """
        做任务
        :param times:
        :param session:
        :return:
        """
        if times <= 0:
            return

        task_list = await self.get_task_list(session)
        for task in task_list:
            if task['finishFlag'] == 1:
                println('{}, 任务:《{}》, 今日已完成!'.format(self._pt_pin, task['name']))
                continue
            if task['type'] == 4:
                task_info = task['jump']['params']['skuId']
            elif task['type'] == 7:
                task_info = 1
            elif task['type'] == 2:
                task_info = task['jump']['params']['shopId']
            elif task['type'] in [16, 3, 5, 17, 21]:
                task_info = task['jump']['params']['url']
            else:
                println('{}, 跳过任务:《{}》!'.format(self._pt_pin, task['name']))
                continue

            println('{}, 正在进行任务:《{}》, 进度:{}/{}!'.format(self._pt_pin, task['name'], task['doTimes'], task['times']))
            res = await self.request(session, 'cash_doTask', {
                'type': task['type'],
                'taskInfo': task_info
            })
            await asyncio.sleep(1)

            if res['code'] != 0 or res['data']['bizCode'] != 0:
                println('{}, 任务:《{}》完成失败, {}!'.format(self._pt_pin, task['name'], res['data']['bizMsg']))
            else:
                println('{}, 成功完成任务:《{}》!'.format(self._pt_pin, task['name']))
        await self.do_tasks(session, times-1)

    async def get_award(self, session):
        """
        领取奖励
        :param session:
        :return:
        """
        for i in [1, 2]:
            data = await self.request(session, 'cash_mob_reward', {"source": i, "rewardNode": ""})
            if data['code'] != 0 or data['data']['bizCode'] != 0:
                println('{}, 领取奖励失败!'.format(self._pt_pin))
            else:
                println('{}, 成功领取奖励!'.format(self._pt_pin))
            await asyncio.sleep(1)

    async def help_friend(self, session):
        """
        :param session:
        :return:
        """
        session.headers.add('Referer', 'https://h5.m.jd.com/babelDiy/Zeus/GzY6gTjVg1zqnQRnmWfMKC4PsT1/index.html')
        for code in JD_CASH_SHARE_CODE:
            if code == self._code:
                continue
            await asyncio.sleep(1)
            invite_code, share_date = code.split('@')
            url = 'https://api.m.jd.com/client.action?functionId=cash_mob_assist&body={}&appid=CashReward&client=m' \
                  '&clientVersion=9.2.8'.format(quote(json.dumps({"inviteCode": invite_code,
                                                                  "shareDate": share_date, "source": 3})))
            response = await session.post(url)
            text = await response.text()
            data = json.loads(text)
            if data['code'] != 0 or data['data']['bizCode'] != 0:
                println('{}, 助力好友:{}失败, {}！'.format(self._pt_pin, invite_code, data['data']['bizMsg']))
                if data['data']['bizCode'] == 206:  # 助力次数用完
                    break
            else:
                println('{}, 助力好友:{}成功!'.format(self._pt_pin, invite_code))

    async def run(self):
        """
        入口
        :return:
        """
        async with aiohttp.ClientSession(headers=self.headers, cookies=self._cookies) as session:
            success = await self.init(session)
            if not success:
                println('{}, 无法初始化数据, 退出程序!'.format(self._pt_pin))
                return
            await self.help_friend(session)
            await self.do_tasks(session)
            await self.get_award(session)


def start(pt_pin, pt_key):
    """
    程序入口
    :param pt_pin:
    :param pt_key:
    :return:
    """
    app = JdCash(pt_pin, pt_key)
    asyncio.run(app.run())


if __name__ == '__main__':
    process_start(start, '签到领现金')

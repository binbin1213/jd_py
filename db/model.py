#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Time    : 2021/7/29 1:19 下午
# @File    : model.py
# @Project : jd_scripts
# @Desc    :
from datetime import datetime
from peewee import *
from config import DB_PATH

db = SqliteDatabase(DB_PATH)

# 京小鸽游乐寄助力码
CODE_AMUSEMENT_POST = 'amusement_post'

# 闪购盲盒助力码
CODE_FLASH_SALE_BOX = 'flash_sale_box'

# 众筹许愿池
CODE_WISHING_POOL = '众筹许愿池-助力码'

# 疯狂砸金蛋助力码
CODE_SMASH_GOLDEN_EGG = 'smash_golden_egg'

# 金果摇钱树助力码
CODE_MONEY_TREE = 'money_tree'

# 种豆得豆助力码
CODE_PLANTING_BEAN = 'planting_bean'

# 东东萌宠助力码
CODE_CUT_PET = 'cut_pet'

# 领现金助力码
CODE_JD_CASH = 'jd_cash'

# 东东工厂助力码
CODE_JD_FACTORY = 'jd_factory'

# 东东农场助力码
CODE_JD_FARM = 'jd_farm'

# 抢京豆
CODE_JD_GRAB_BEAN = 'jd_grab_bean'

# 东东健康社区
CODE_JD_HEALTH = 'jd_health'

# 京喜工厂开团
CODE_JX_FACTORY_TUAN = 'jx_factory_tuan'

# 惊喜工厂招工
CODE_JX_FACTORY_WORK = 'jx_factory_work'


#  到家果园助力
CODE_DJ_FRUIT = 'dj_fruit'

# 手机狂欢城
CODE_JD_CARNIVAL_CITY = 'jd_carnival_city'

# 京喜牧场
CODE_JX_PASTURE = 'jd_pasture'

# 特务Z
CODE_JD_SUPER_BRAND = 'jd_super_brand'

# 5G盲盒助力码
CODE_5G_BOX = 'jd_5g_box'


class Code(Model):
    """
    邀请/助力码
    """
    account = CharField(verbose_name='京东账号', max_length=255)

    # 邀请/助力码类型L: 1容器内部账号助力码, 2云端助力码, 3,容器配置填写助力码
    code_type = SmallIntegerField(verbose_name='邀请/助力码标示', default=0)

    code_key = CharField(verbose_name='邀请/助力码标示', max_length=30)

    code_val = CharField(verbose_name='邀请/助力码内容', max_length=255)

    sort = SmallIntegerField(verbose_name='排序字段', default=1)

    created_at = DateField(verbose_name='创建日期', default=datetime.now().date())

    updated_at = DateField(verbose_name='更新日期', default=datetime.now().date())

    class Meta:
        database = db
        table_name = 'code'

    @classmethod
    def insert_code(cls, code_key=None, account='', code_val='', code_type=1, sort=1):
        """
        插入一条助力码
        :param sort:
        :param code_val:
        :param account:
        :param code_key:
        :param code_type:
        :return:
        """
        exists = cls.select().where(cls.code_key == code_key, cls.account == account, cls.code_val == code_val,
                                    cls.sort == sort, cls.code_type == code_type,
                                    cls.created_at == datetime.now().date()).exists()
        if not exists:
            rowid = (cls.insert(code_key=code_key, account=account,
                                code_val=code_val, code_type=code_type, sort=sort,
                                created_at=datetime.now().date()).execute())
            return rowid

        cls.update({cls.code_val: code_val, cls.sort: sort}).where(cls.account == account,
                                                                   cls.code_key == code_key,
                                                                   cls.created_at == datetime.now().date(),
                                                                   ).execute()

    @classmethod
    def get_code_list(cls, code_key=''):
        """
        获取助力码列表
        :param code_key: 助力码类型
        :return:
        """
        result = []

        code_list = cls.select().where(cls.code_key == code_key, cls.created_at == datetime.now().date()).order_by(
            cls.sort).execute()
        if not code_list:
            return result

        for code in code_list:
            result.append({
                'account': code.account,
                'code': code.code_val,
            })

        return result

    @classmethod
    def get_codes(cls, code_key=''):
        """
        :param code_key:
        :return:
        """
        code_list = cls.select().where(cls.code_key == code_key, cls.created_at == datetime.now().date()).order_by(
            cls.sort).execute()
        return code_list


db.create_tables([Code])

# Code.insert_code(code_key=CODE_FLASH_SALE_BOX, code_val='T0225KkcRRYR_QbSIkmgkPUDJQCjVQmoaT5kRrbA', sort=10,
#                  account='作者')
# Code.insert_code(code_key=CODE_JD_FARM, code_val='f9a5389ab473423e83a746e03a82dddc', sort=10, account='作者')
# Code.insert_code(code_key=CODE_WISHING_POOL, code_val='T0225KkcRRYR_QbSIkmgkPUDJQCjRXnYaU5kRrbA', sort=10, account='作者')
# Code.insert_code(code_key=CODE_CUT_PET, code_val='MTAxNzIxMDc1MTAwMDAwMDA0OTQ4ODA1Mw==', sort=10, account='作者')
# Code.insert_code(code_key=CODE_JD_FACTORY, code_val='T0225KkcRRYR_QbSIkmgkPUDJQCjVWnYaS5kRrbA', sort=10, account='作者')
# Code.insert_code(code_key=CODE_MONEY_TREE, code_val='GEwzybOwKgTmY4q07j9ZiMAdoUJQ3Dik', sort=10, account='作者')
# Code.insert_code(code_key=CODE_PLANTING_BEAN, code_val='mlrdw3aw26j3x3vxi2qvp7xj5llrsmtd3tde64i', sort=10, account='作者')
# Code.insert_code(code_key=CODE_JX_FACTORY_WORK, code_val='3uRnk7OghCCAuKJAPLEajA==', sort=10, account='作者')

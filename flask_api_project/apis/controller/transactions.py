from flask import request
from flask_restful import Resource
from sqlalchemy import text

from ...exceptions.request_exception import RequestException
from ...exceptions.service_error_code import ServiceErrorEnum
from ...extensions import db
from ...logger.logger import log
from ...models.tx import Transaction
from ...utils.data_utils import digital_utils
from ...utils.paginator import Paginator
from ...utils.requests_utils import get_argument, rpc_client, get_dict
from ...utils.response_utils import ok, error


class GetTransactions(Resource):

    @log.catch(reraise=True)
    def get(self):
        """
        📝获取某资产的交易记录
        ---
        tags:
          - transactions
        parameters:
          - name: address
            description:
            in: body
            type: string
            required: true
          - name: asset_id
            description:
            in: body
            type: string
            required: true
          - name: max_id 往后翻页, 带上当前页最后条的 id
            description:
            in: body
            type: integer
            default: 0
          - name: since_id 往前翻页, 带上当前页第一条的 id
            description:
            in: body
            type: integer
            default: 0
          - name: abs_page
            description: 翻页时候页码偏移量绝对值(两页码数值相减的绝对值),前一页后一页传 1，最后一页需要传相减之后的绝对值
            in: body
            type: string
            required: true
          - name: page_size 每页展示条数
            description:
            in: body
            type: string
            required: true
        responses:
          200:
            description:
            schema:
              properties:
                result:
                  tpye: bool
                msg:
                  type: string
                bool_status:
                  type: bool
              example: {
                        "bool_status": true,
                        "msg": "ok",
                        "response_time": 1552752071,
                        "result": {
                            "items": [
                                {
                                    "block_time": 1530435154,
                                    "id": 13255609,
                                    "size": 202,
                                    "txid": "0x7e9ed18eb3c16c38137f68b17862a0190fd2ff2ad7e2709f4d9bee8dbd2bc258",
                                    "value": "0"
                                },
                                {
                                    "block_time": 1530118760,
                                    "id": 13157270,
                                    "size": 202,
                                    "txid": "0xdf93fba0227945a54feda273873414d89372c74d1035a09e0428cad92d5b7a2c",
                                    "value": "0"
                                }
                            ],
                            "page": 1,
                            "pages": 14,
                            "per_page": 2,
                            "total": 28
                        }
                       }
        """
        address = get_argument('address', required=True)
        asset_id = get_argument('asset_id', required=True)

        max_id = get_argument('max_id', type=int, default=0)
        since_id = get_argument('since_id', type=int, default=0)

        abs_page = get_argument('abs_page', type=int, default=1)
        page_size = get_argument('page_size', type=int, default=10, required=True)

        offset = (abs_page - 1) * page_size

        pre_sql = ''

        if len(asset_id) == 66 and str.startswith(asset_id, '0x'):
            # asset
            count = self.get_assets_count(address, asset_id)
            if count > 0:
                pre_sql = self.asset_sql_handler(max_id, since_id)
        else:
            # nep5
            count = self.get_nep5_count(address, asset_id)
            if count > 0:
                pre_sql = self.nep5_sql_handler(max_id, since_id)

        if count == 0:
            result = Paginator(abs_page, page_size, count, []).get_dict()
            return ok(data=result)

        exec_sql = text(pre_sql).bindparams(
            address=address,
            asset_id=asset_id,
            offsets=offset,
            page_size=page_size,
        )
        execute_result = db.session.execute(exec_sql).fetchall()

        transactions = []

        for item in execute_result:
            asset = {
                'size': item[0],
                'block_time': item[1],
                'id': item[2],
                'value': digital_utils(item[3]),
                'txid': item[4]
            }
            transactions.append(asset)

        result = Paginator(abs_page, page_size, count, transactions).get_dict()

        return ok(data=result)

    def get_assets_count(self, address, asset_id):
        sql = text('''
        select count(id) 
        from utxo 
        where address = :address and 
              asset_id = :asset_id
        ''')

        count = db.session.execute(sql.bindparams(address=address, asset_id=asset_id)).fetchone()
        return count[0]

    def get_nep5_count(self, address, asset_id):
        sql = text('''
        select
            count(id)
        from nep5_tx 
        where (`from` = :address or `to` = :address) and asset_id = :asset_id
        ''')

        count = db.session.execute(sql.bindparams(address=address, asset_id=asset_id)).fetchone()
        return count[0]

    def asset_sql_handler(self, max_id, since_id):
        sql = '''
        select 
          t.size, 
          t.block_time, 
          b.id                                                   as id, 
          if(a.address = :address, b.value - a.value, b.value) as value, 
          a.used_in_tx                                           as txid 
        from (select * 
              from (select 
                      sum(value) as value, 
                      used_in_tx, 
                      address, 
                      asset_id, 
                      id 
                    from utxo 
                    where asset_id = :asset_id and used_in_tx in (select txid 
                                                                    from utxo 
                                                                    where address = :address and 
                                                                          asset_id = :asset_id) 
                    group by address, asset_id, used_in_tx  [:condition1] 
                    limit :offsets, :page_size) aa) a left join (select 
                                                   address, 
                                                   id, 
                                                   value, 
                                                   txid 
                                                 from utxo 
                                                 where address = :address and 
                                                       asset_id = :asset_id) b on b.txid = a.used_in_tx 
          left join tx t on b.txid = t.txid 
        [:condition2]'''

        pre_sql = self.condition_handler(sql, max_id, since_id)

        return pre_sql

    def condition_handler(self, sql, max_id, since_id):
        c1 = '[:condition1]'
        c2 = '[:condition2]'
        if max_id > 0:
            condition = 'and id < {} order by id desc'.format(max_id)
            sql = sql.replace(c1, condition)
            sql = sql.replace(c2, '')
        elif since_id > 0:
            condition = 'and id > {} order by id'.format(since_id)
            sql = sql.replace(c1, condition)
            sql = sql.replace(c2, 'order by a.id desc')
        else:
            sql = sql.replace(c1, 'order by id desc')
            sql = sql.replace(c2, '')
        return sql

    def nep5_sql_handler(self, max_id, since_id):
        sql = '''
        select
          t.size,
          t.block_time,
          a.id,
          avalue as value,
          a.txid
        from (select
                case when `from` = :address
                  then (0 - nt.value)
                when `to` = :address
                  then nt.value end as avalue,
                id,
                txid,
                `from`,
                `to`,
                nt.value
              from nep5_tx nt
              where (`from` = :address or `to` = :address) and asset_id = :asset_id [:condition1] 
              limit :offsets, :page_size) a 
        left join
          tx t on t.txid = a.txid [:condition2]
          '''

        pre_sql = self.condition_handler(sql, max_id, since_id)

        return pre_sql


class Confirms(Resource):

    @log.catch(reraise=True)
    def post(self):
        """
        🤝获取一笔或多笔交易的交易状态
        ---
        tags:
          - transactions
        parameters:
          - name: txids
            description: 参数为 txid 数组
            in: body
            type: array
            required: true
        responses:
          200:
            description:
            schema:
              properties:
                result:
                  tpye: bool
                msg:
                  type: string
                bool_status:
                  type: bool
              example: {
                            "bool_status": true,
                            "msg": "ok",
                            "response_time": 1552739325,
                            "result": [
                                "0x48a1972cefc6c1c6249eced8a8a76f89d571098d04622e54661cbe3efd25d947",
                                "0xf91a7bb68233e8821871738e73b8c764995e73a8e85c2dd34ee25ee744206581"
                            ]
                       }
        """
        json_param = request.get_json()

        if 'txids' not in json_param:
            raise RequestException(ServiceErrorEnum.PARAMETER_ERROR)
        else:
            txids = json_param['txids']

        if len(txids) == 0 or type(txids) is not list:
            return ok(data=[])

        condition = tuple(txids)
        order_str = ''
        for i in txids:
            order_str = order_str + '\'{}\','.format(i)
        queries = Transaction.query.filter(Transaction.txid.in_(condition)).order_by(
            text('FIELD(txid, ' + order_str[:-1] + ')')).all()

        query_map = [t.txid for t in queries if t]

        return ok(data=query_map)


class Transfer(Resource):

    @log.catch(reraise=True)
    def post(self):
        """
       ⚖转账
       ---
       tags:
         - transactions
       parameters:
         - name: signature_transaction
           description: 签名后的交易信息字符串
           in: body
           type: string
           required: true
       responses:
         200:
           description: bool_status:true && result:True 代表转账操作成功, 进行节点确认中。
           schema:
             properties:
               result:
                 tpye: bool
               msg:
                 type: string
               bool_status:
                 type: bool
             example: {bool_status: true, msg: ok, result: True}
       """
        signature_transaction = get_argument('signature_transaction', type=str, required=True)
        params = [signature_transaction]
        is_ok, result = rpc_client('sendrawtransaction', params)
        if not is_ok:
            code = result['code']
            msg = result['message']
            return error(error_code=code, msg=msg)
        return ok(data=result)


class GetUtxoes(Resource):

    @log.catch(reraise=True)
    def get(self):
        """
          获取未花费的 utxo
          ---
          tags:
            - transactions
          parameters:
            - name: address
              description:
              in: body
              type: string
              required: true
            - name: asset_id
              description:
              in: body
              type: string
              required: true
          responses:
            200:
              description:
              schema:
                properties:
                  result:
                    tpye: bool
                  msg:
                    type: string
                  bool_status:
                    type: bool
                example: {
                            "bool_status": true,
                            "msg": "ok",
                            "response_time": 1552831725,
                            "result": [
                                {
                                    "asset_id": "0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7",
                                    "id": 11234567,
                                    "n": 0,
                                    "txid": "0x17862a0190fd2ff2ad7e2709f4d9bee8dbd2bc2587e9ed18eb3c16c38137f68b"
                                }
                            ]
                        }
          """
        address = get_argument('address', required=True)
        asset_id = get_argument('asset_id', required=True)

        sql = '''
        select
          id,
          txid,
          n,
          asset_id,
          value
        from utxo
        where asset_id = :asset_id and address = :address and used_in_tx is null
        '''
        pre_sql = text(sql).bindparams(asset_id=asset_id, address=address)

        result = db.session.execute(pre_sql).fetchall()
        utxoes = []

        for item in result:
            asset = get_dict(item, ['id', 'txid', 'n', 'asset_id'])
            utxoes.append(asset)

        return ok(data=utxoes)

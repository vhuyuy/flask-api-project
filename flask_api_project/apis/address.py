from flask_restful import Resource
from sqlalchemy import text

from ..extensions import db
from ..logger.logger import log
from ..utils.data_utils import digital_utils
from ..utils.requests_utils import get_argument, get_dict
from ..utils.response_utils import ok


class GetAddressAssets(Resource):

    @log.catch(reraise=True)
    def get(self):
        """
        💰获取某地址所有大于0的资产信息/指定资产信息
        ---
        tags:
          - address
        parameters:
          - name: address
            description: 地址
            in: query
            type: string
            required: true
          - name: asset_id
            description:  不填 asset_id，代表查询该地址所有大于0的资产信息, 否则只查询指定资产信息
            in: query
            type: string
            required: false
        responses:
          200:
            description:
            schema:
              properties:
                result:
                  tpye: json
                msg:
                  type: string
                bool_status:
                  type: bool
              example: {
                        bool_status: true,
                        "msg": "ok",
                        "response_time": 1552739325,
                        result: [
                          {"asset_id": "a","balance": "3","name":"xxx", "symbol": "BDN"},
                          {"asset_id": "b","balance": "20000", "name":"xxx", "symbol": "EDS"}
                        ]
                      }
        """
        address = get_argument('address', type=str, required=True)
        asset_id = get_argument('asset_id', type=str)

        if asset_id:
            exec_sql = self.single_asset_sql(address, asset_id)
        else:
            exec_sql = self.assets_sql(address)

        execute_result = db.session.execute(exec_sql).fetchall()

        asset_list = []

        for item in execute_result:
            asset = get_dict(item, ['asset_id', 'name', 'symbol', 'balance'])
            asset['balance'] = digital_utils(asset['balance'])
            asset_list.append(asset)

        return ok(asset_list)

    def assets_sql(self, address):
        sql = text('''
        select
              n.asset_id,
              n1.name,
              n1.symbol,
              n.balance
            from addr_asset n left join (select
                                           asset_id,
                                           name,
                                           name as symbol
                                         from asset
                                         UNION all SELECT
                                                     asset_id,
                                                     name,
                                                     symbol
                                                   from nep5 where visible=1) n1 ON n.asset_id = n1.asset_id
            where address = :address and balance > 0
            order by n1.symbol 
        ''')
        return sql.bindparams(address=address)

    def single_asset_sql(self, address, asset_id):
        sql = text('''
           select
                 n.asset_id,
                 n1.name,
                 n1.symbol,
                 n.balance
               from addr_asset n left join (select
                                              asset_id,
                                              name,
                                              name as symbol
                                            from asset
                                            UNION all SELECT
                                                        asset_id,
                                                        name,
                                                        symbol
                                                      from nep5 where visible=1) n1 ON n.asset_id = n1.asset_id
               where address = :address and n.asset_id = :asset_id and balance > 0
               order by n1.symbol 
           ''')
        return sql.bindparams(address=address, asset_id=asset_id)

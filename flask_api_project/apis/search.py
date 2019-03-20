from flask_restful import Resource
from sqlalchemy import text

from ..extensions import db
from ..logger.logger import log
from ..utils.requests_utils import get_argument, get_dict
from ..utils.response_utils import ok


class SearchAssetAndNep5(Resource):

    @log.catch(reraise=True)
    def get(self):
        """
        🔍币种搜索
        ---
        tags:
          - search
        parameters:
          - name: query
            description: 可根据 asset_id(asset_id 完全匹配)或者 name(资产名称右模糊匹配)
            in: query
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
                            bool_status: true,
                            "msg": "ok",
                            "response_time": 1552739325,
                            "result":
                            [
                                {
                                    "asset_id": "fd48828f107f400c1ae595366f301842886ec573",
                                    "name": "NEP5 Coin NNC",
                                    "symbol": "NNC"
                                },
                                {
                                    "asset_id": "fc732edee1efdf968c23c20a9628eaa5a6ccb934",
                                    "name": "NEO Name Credit",
                                    "symbol": "NNC"
                                }
                            ]
                        }
        """
        query = get_argument("query", type=str, required=True)

        if len(query) == 40 or (len(query) == 66 and str.startswith(query, '0x')):
            exec_sql = self.asset_id_query(query)
        else:
            exec_sql = self.get_default_sql(query)

        execute_result = db.session.execute(exec_sql).fetchall()

        asset_list = []

        for item in execute_result:
            asset = get_dict(item, ['asset_id', 'name', 'symbol'])
            asset_list.append(asset)

        return ok(asset_list)

    def get_default_sql(self, name):
        sql = text('''
        select *
        from (select
                asset_id,
                name,
                name as symbol
              from asset
              UNION all SELECT
                          asset_id,
                          name,
                          symbol
                        from nep5 where visible = 1) a
        where name like :name or symbol like :name
        ''')

        name = '{}%'.format(name)
        return sql.bindparams(name=name)

    def asset_id_query(self, asset_id):
        sql = text('''
                select *
                from (select
                        asset_id,
                        name,
                        name as symbol
                      from asset
                      UNION all SELECT
                                  asset_id,
                                  name,
                                  symbol
                                from nep5 where visible = 1) a
                where asset_id = :asset_id 
                ''')
        return sql.bindparams(asset_id=asset_id)

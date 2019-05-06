import os

from flask import make_response, current_app
from flask_restful import Resource
from sqlalchemy import text

from ..extensions import db
from ..logger.logger import log
from ..utils.paginator import Paginator
from ..utils.requests_utils import get_argument, get_dict
from ..utils.response_utils import ok


class GetAllAssets(Resource):

    @log.catch(reraise=True)
    def get(self):
        """
        💰获取所有资产信息
        ---
        tags:
          - asset
        parameters:
          - name: page_index
            description: 页码
            in: query
            type: int
            required: true
          - name: page_size
            description:  每页大小
            in: query
            type: int
            required: true
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
                        "bool_status": true,
                        "msg": "ok",
                        "response_time": 1552716826,
                        "result": {
                            "items": [
                                {
                                    "asset_id": "50091057ff12863f1a43266b9786209e399c6ffc",
                                    "name": "Novem Gold Token",
                                    "symbol": "NNN"
                                },
                                {
                                    "asset_id": "bac0d143a547dc66a1d6a2b7d66b06de42614971",
                                    "name": "Bridge Protocol",
                                    "symbol": "BRDG"
                                }
                            ],
                            "page": 12,
                            "pages": 12,
                            "per_page": 10,
                            "total": 116
                        }
                    }
        """
        page_size = get_argument('page_size', type=int, default=10, required=True)
        page_index = get_argument('page_index', type=int, default=1, required=True)

        assets = []
        count = self.get_assets_count()

        if count:
            exec_sql = self.all_assets_sql(page_index, page_size)
            asset_result = db.session.execute(exec_sql).fetchall()

            for item in asset_result:
                asset = get_dict(item, ['asset_id', 'name', 'symbol'])
                assets.append(asset)

        result = Paginator(page_index, page_size, count, assets).get_dict()

        return ok(data=result)

    def get_assets_count(self):
        sql = text('''
        select count(a.id)
        from (select id
              from asset
              union all select id
                        from nep5 where visible = 1) a
        ''')

        count = db.session.execute(sql).fetchone()
        return count[0]

    def all_assets_sql(self, page_index, page_size):
        exec_sql = text('''
        select
          asset_id,
          name,
          name as symbol
        from asset
        union all select
                    asset_id,
                    name,
                    symbol
                  from nep5 where visible = 1
        limit :page_index, :page_size
        ''').bindparams(page_index=(page_index - 1) * page_size, page_size=page_size)

        return exec_sql


class GetImage(Resource):

    @log.catch(reraise=True)
    def get(self, asset_id):
        """
        获取资产logo /images/asset_id
        ---
        tags:
          - asset
        """
        relative_path = current_app.config['RELATIVE_PATH']
        abd_path = os.path.abspath(relative_path)
        path = os.path.join(abd_path, asset_id)
        path = '{}{}'.format(path, '.png')

        if not os.path.isfile(path):
            return make_response('Not Found', 404)

        image_data = open(path, "rb").read()
        response = make_response(image_data)
        response.headers['Content-Type'] = 'image/jpeg'
        return response

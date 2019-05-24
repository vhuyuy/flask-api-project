from flask_api_project.apis.controller import asset

urls = [
    '/v1/asset/getallassets', asset.GetAllAssets,
    '/images/<asset_id>', asset.GetImage,
]

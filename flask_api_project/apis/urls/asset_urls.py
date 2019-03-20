from ...apis import asset

urls = [
    '/v1/asset/getallassets', asset.GetAllAssets,
    '/images/<asset_id>', asset.GetImage,
]

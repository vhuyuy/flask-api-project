from flask_api_project.apis.controller import address

urls = [
    '/v1/address/assets', address.GetAddressAssets,
]

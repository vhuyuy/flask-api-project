from ..extensions import db
from ..models import BaseModel


class Transaction(BaseModel):
    __tablename__ = 'tx'

    block_index = db.Column(db.INTEGER)
    block_time = db.Column(db.TIMESTAMP(True))
    txid = db.Column(db.String)
    size = db.Column(db.Integer)
    type = db.Column(db.String)
    version = db.Column(db.String)
    sys_fee = db.Column(db.DECIMAL(27, 8))
    net_fee = db.Column(db.DECIMAL(27, 8))
    nonce = db.Column(db.BIGINT)
    script = db.Column(db.Text)
    gas = db.Column(db.DECIMAL(27, 8))

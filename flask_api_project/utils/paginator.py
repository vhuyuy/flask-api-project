import math


class Paginator(object):
    def __init__(self, page, per_page, total, items=None):
        self.page = page
        self.pages = math.ceil(total / per_page)
        self.per_page = per_page
        self.total = total
        self.items = items

    def get_dict(self):
        return dict(
            page=self.page,
            pages=self.pages,
            per_page=self.per_page,
            items=self.items,
            total=self.total
        )

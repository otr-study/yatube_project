from django.conf import settings
from django.core.paginator import Paginator

POSTS_PER_PAGE = getattr(settings, 'POSTS_PER_PAGE', 10)


def get_paginator_page(items, page_number):
    paginator = Paginator(items, POSTS_PER_PAGE)
    return paginator.get_page(page_number)

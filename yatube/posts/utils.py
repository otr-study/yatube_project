from django.core.paginator import Paginator
from yatube.settings import POSTS_PER_PAGE


def get_paginator_page(items, page_number):
    paginator = Paginator(items, POSTS_PER_PAGE)
    return paginator.get_page(page_number)

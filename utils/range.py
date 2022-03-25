async def async_range(*args):
    for i in range(*args):
        yield i

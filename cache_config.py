from flask_caching import Cache



def initialize_cache(app=None):
    cache_config = {
        "CACHE_TYPE": "RedisCache",
        "CACHE_REDIS_HOST": "localhost",
        "CACHE_REDIS_PORT": 6379,
    }

    if app:
        app.config.from_mapping(cache_config)
        cache = Cache(app)
        app.app_context().push()
    else:
        cache = Cache(config=cache_config)

    return cache



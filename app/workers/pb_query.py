class pb_query():
    def __init__(self, *args, **kwargs):
        logger.warning('PB Started...')
        pb_limit = 20
        pb_interval = 20
        pb_auth_token = 'o.1mYHkPzpFzSXHF4M2UcGhit6zyZQ98tM'
        HTTP_PROXY_HOST = None
        HTTP_PROXY_PORT = None
        while True:
            pb = Pushbullet(pb_auth_token)
            pushes = pb.get_pushes(limit=pb_limit)
            output = json.dumps(pushes)
            loop_len = len(pushes)
            count = 0
            for i in pushes:
                if count <= loop_len:
                    try:
                        logger.info(i['title']+' | '+i['url'])
                        time.sleep(pb_interval)
                    except Exception as err:
                        logger.error('PB Error: %s', err)
                        pass
                    count = count + 1
                else:
                    pb_main()
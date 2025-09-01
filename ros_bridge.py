try:
    import roslibpy
except Exception:
    roslibpy = None

class RosBridge:
    def __init__(self, host: str = 'localhost', port: int = 9090):
        self.host = host
        self.port = port
        self.client = None
        self.subs = {}  # topic -> subscriber
        self.last_msg = None

    def connect(self):
        if roslibpy is None:
            return False, 'roslibpy not installed'
        if self.client is not None:
            return True, 'Already connected'
        try:
            self.client = roslibpy.Ros(host=self.host, port=self.port)
            self.client.run()
            return True, 'Connected'
        except Exception as e:
            self.client = None
            return False, f'Connect failed: {e}'

    def subscribe(self, topic: str):
        ok, msg = self.connect()
        if not ok:
            return False, msg
        if topic in self.subs:
            return True, 'Already subscribed'
        try:
            sub = roslibpy.Topic(self.client, topic, 'std_msgs/String')
            def cb(message):
                # store last message (could be forwarded by a websocket)
                self.last_msg = message
            sub.subscribe(cb)
            self.subs[topic] = sub
            return True, 'Subscribed'
        except Exception as e:
            return False, f'Subscribe failed: {e}'

    def unsubscribe(self, topic: str):
        try:
            sub = self.subs.get(topic)
            if sub is None:
                return False, 'Not subscribed'
            sub.unsubscribe()
            del self.subs[topic]
            return True, 'Unsubscribed'
        except Exception as e:
            return False, f'Unsubscribe failed: {e}'

    def get_last_msg(self):
        return self.last_msg

    def close(self):
        try:
            for t, s in list(self.subs.items()):
                try:
                    s.unsubscribe()
                except Exception:
                    pass
            if self.client:
                self.client.terminate()
            self.client = None
            self.subs.clear()
            return True, 'Closed'
        except Exception as e:
            return False, f'Close failed: {e}'
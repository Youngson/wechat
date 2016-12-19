# -*- coding: utf-8 -*-
"""token manager"""
from time import time, sleep
import logging
import redis

logger = logging.getLogger(__name__)


class LocalTokenManager(object):
    """LocalTokenManager"""

    def __init__(self, postfix="", *args, **kwargs):
        """init"""
        pass

    @property
    def token(self):
        """get token"""
        pass

    @token.setter
    def token(self, token):
        """set token"""
        pass

    @property
    def expires(self):
        """get expires"""
        pass

    @expires.setter
    def expires(self, expires):
        """set expires"""
        pass


class RedisTokenManager(object):
    """RedisTokenManager"""

    def __init__(self, postfix="", *args, **kwargs):
        """init"""
        self.postfix = postfix
        self._token_type = None
        self.token_name = None
        self.expires_name = None
        self.redis = redis.Redis(*args, **kwargs)
        if not self.expires:
            self.expires = time()

    @property
    def token(self):
        """get token"""
        if self._token_type is not None:
            self.token_name = "_".join([self._token_type, self.postfix])
            token = self.redis.get(self.token_name)
            token = str(token, "utf-8") if token and isinstance(
                token, bytes) else token
            print({self._token_type: token})
            return {self._token_type: token}
        else:
            print('_token_type:None')
            return None

    @token.setter
    def token(self, token):
        """set token"""
        if self._token_type is not None:
            self.token_name = "_".join([self._token_type, self.postfix])
            self.redis.set(self.token_name, token)

    @property
    def expires(self):
        """get expires"""
        if self._token_type is not None:
            self.expires_name = "_".join([self._token_type, "expires", self.postfix])
            expires = self.redis.get(self.expires_name)
            return {self._token_type: expires}
        else:
            print('get expires--> _token_type:None')
            return None

    @expires.setter
    def expires(self, expires):
        """set expires"""
        if self._token_type is not None:
            self.expires_name = "_".join([self._token_type, "expires", self.postfix])
            self.redis.set(self.expires_name, expires)

    def get_token(self, fn_get_access_token, token_type=None):
        """get_token"""
        if isinstance(self.token, dict):
            token = self.token.get(token_type)
        else:
            token = self.token
        if isinstance(self.expires, dict):
            expires = self.expires.get(token_type, time())
        else:
            expires = time()

        if not token and not expires:
            for i in range(12):
                sleep(5)
                if self.token:
                    break
        elif not token or expires and float(expires) < time():
            self.expires = None
            self.refresh_token(fn_get_access_token, token_type)
        return self.token.get(token_type)

    def refresh_token(self, fn_get_access_token, token_type):
        """refresh_token"""
        token, err = fn_get_access_token()
        if token and not err:
            print(token_type)
            print('原始token:', token)
            self._token_type = token_type
            if token_type == 'access_token':
                key_name = 'access_token'
            else:
                key_name = 'ticket'
            self.token = token[key_name]
            self.expires = time() + token['expires_in']
        else:
            self.token = None
            self._token_type = None

import errno
import hashlib
import mongoengine as mongo
import msgpack
import os
import tempfile

from datetime import datetime, timedelta
from flask_caching.backends.base import BaseCache
from .common import connect_db, get_credentials
from . import settings


class CachedItem(mongo.Document):
    name = mongo.StringField(required=True, unique=True)
    data = mongo.BinaryField(required=True)
    expires = mongo.DateTimeField()


class MongoCache(BaseCache):
    """A cache that stores the items in a MongoDB collection.

        Args:
            default_timeout (int): the default timeout that is used (in seconds).
                A timeout of 0 indicates that the cache never expires.
            hash_method: Default hashlib.md5. The hash method used to
                generate the filename for cached results.
            credentials (dict): the MongoDB credentials,
                passed to common.connect_db.
    """

    def __init__(
        self,
        app,
        c,
        d,
        default_timeout=300,
        hash_method=hashlib.md5,
        credentials=settings.DEFAULT_CREDENTIALS_FILE
    ):
        self._default_timeout = default_timeout["default_timeout"]
        self._hash_method = hash_method
        self._credentials = get_credentials(credentials)
        self._alias = "cache"

        CachedItem.meta = {"db_alias": self._alias}


    def _connect(self):
        """Connect to DB."""
        try:
            connect_db(self._credentials, self._alias)
            return True
        except:
            return False

    
    def _disconnect(self, prune=True):
        """Disconnect from DB. Prunes the database by default."""
        try:
            self._prune()
            mongo.disconnect(alias=self._alias)
            return True
        except:
            return False


    def _get_name(self, key):
        """Returns name after hash"""
        if isinstance(key, str):
            key = key.encode("utf-8")
        return self._hash_method(key).hexdigest()

    
    def _prune(self):
        """Prunes collection of expired documents"""
        try:
            if self._connect():
                CachedItem.objects(expires__lte=datetime.utcnow()).delete()
                self._disconnect()
                return True
            return False
        except:
            return False


    def add(self, key, value, timeout=None):
        if self._connect():
            preexisting = CachedItem.objects(name = self._get_name(key))
            self._disconnect()

            if preexisting.count > 0:
                return False
            else:
                self.set(key, value, timeout)
                return True
        return False

    
    def clear(self):
        try:
            if self._connect():
                CachedItem.objects().delete()
                self._disconnect()

                return True
            return False
        except:
            return False


    def delete(self, key):
        if self._connect():
            result = CachedItem.objects(name = self._get_name(key))
            if result.count() > 1:
                try:
                    result.delete()
                    self._disconnect()
                except:
                    return False
                else:
                    return True
        return True


    def get(self, key):
        if self._connect():
            result = CachedItem.objects(name = self._get_name(key))
            if result.count() > 0:
                try:
                    data = result.first()
                    self._disconnect()
                    return msgpack.unpackb(data["data"], raw=False)
                except:
                    return None
        return None

    
    def has(self, key):
        if self._connect():
            result = CachedItem.objects(name = self._get_name(key)).only(name)
            self._disconnect()

            return True if result.count() > 0 else False
        return False


    def set(self, key, value, timeout=None):
        if not self._connect():
            return False

        preexisting = CachedItem.objects(name = self._get_name(key))
        if preexisting.count() > 0:
            try:
                doc = preexisting.first()
            except:
                return False
        else:
            try:
                doc = CachedItem()
            except:
                return False
        
        try:
            doc.name = self._get_name(key)
            doc.data = msgpack.packb(value, use_bin_type=True)

            seconds = self._default_timeout if timeout is None else timeout
            doc.expires = datetime.utcnow() + timedelta(seconds=seconds)
            
            doc.save()

            self._disconnect()
        except:
            return False
        else:
            return True

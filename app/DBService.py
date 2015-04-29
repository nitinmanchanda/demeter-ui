__author__ = 'nitin'

from abc import abstractmethod, ABCMeta
import time
from uuid import uuid4
from sqlalchemy.engine import create_engine
from sqlalchemy.sql.expression import select, and_, desc
from sqlalchemy.sql.schema import Table, MetaData
from config import DATBASE_URL
from binascii import a2b_hex, b2a_hex

def get_next_id(id_generator=uuid4):
    return id_generator().hex

def get_next_version():
    return int(round(time.time() * 1000))

class DBService(object):
    """
    This class act as an adapter between db/sqlalchemy layer and application incorporating our own notion of updates and
    deletes using versioning.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_table(self):
        pass

    @abstractmethod
    def get_entity_from_proxy(self, result_proxy):
        pass

    def __init__(self, id_service=get_next_id, version_service=get_next_version):
        self.id_generator = id_service
        self.version_generator = version_service

    def save(self, **columns):
        return self._internal_insert(**columns)

    def update(self, primary_id, **columns):
        return self._internal_insert(entity_id=primary_id, **columns)

    def delete(self, primary_id, **columns):
        """
        Deletes are handled by setting the archived flag True
        """
        return self._internal_insert(entity_id=primary_id, deleted=True, **columns)

    def find_one(self, where_clause):
        """
        Finds the most recent version
        """
        stmt = select([self.get_table()]).where(where_clause).order_by(desc('version')).limit(1)

        # resp is a ResultProxy object of sqlalchemy which acts something like a DB Cursor
        resp = stmt.execute().fetchone()
        if resp and resp['archived']:  # the row has been deleted
            return None

        return self.get_entity_from_proxy(resp)

    def find_all(self, where_clause):
        s = select(self.get_table()).where(where_clause)
        resp = self.get_table().execute(s)
        return [self.get_entity_from_proxy(e) for e in resp.fetchall()]

    def _internal_insert(self, entity_id=None, deleted=False, **columns):
        if entity_id is None:
            entity_id = self.id_generator()

        entity_version = self.version_generator()
        table = self.get_table()
        insert = table.insert()
        resp = insert.execute(id=a2b_hex(entity_id), version=entity_version, archived=deleted, **columns)
        return entity_id, entity_version, resp


class GeoInfoService(DBService):

    def __init__(self, metadata):
        self.table = Table('geoinfo1', metadata, autoload=True)
        DBService.__init__(self)

    def get_table(self):
        return self.table

    def get_entity_from_proxy(self, row_proxy):
        return LocationDTO(row_proxy)

    def get_latest_version(self):
        pass


class LocationDTO(object):
    def __init__(self, location_row):
        self.id = location_row['id']
        self.name = location_row['name']
        self.containers = [int(container) for container in location_row['containers'].split(';')]
        self.types = list(location_row['types'])
        self.latitude = location_row['latitude']
        self.longitude = location_row['longitude']
        self.north = location_row['north']
        self.south = location_row['south']
        self.east = location_row['east']
        self.west = location_row['west']
        self.synonyms = location_row['synonyms'].split(';')
        self.created_on = location_row['created_on']
        self.updated_on = location_row['updated_on']

    def __repr__(self):
        return 'Location({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7})'.format(self.id, self.name, self.latitude,
                                                                         self.longitude, self.north, self.south,
                                                                         self.east, self.west)

    def __eq__(self, other):
        if isinstance(other, LocationDTO):
            return self.id == other.id
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

    def as_dict(self):
        return dict(id=b2a_hex(self.id), name=self.name, containers=self.containers,
                    types=self.types, synonyms=self.synonyms,
                    created_on=str(self.created_on), updated_on=str(self.updated_on),
                    lat_lon={'lat': float(self.latitude), 'lon': float(self.longitude)},
                    bounds={'type': 'polygon', 'orientation': 'clockwise',
                            'coordinates': [[float(self.west), float(self.north)],
                                             [float(self.east), float(self.north)],
                                             [float(self.east), float(self.south)],
                                             [float(self.west), float(self.south)],
                                             [float(self.west), float(self.north)]]})


engine = create_engine("mysql+pymysql://root:@localhost/demeter", echo=True)
metadata = MetaData(bind=engine)
geo_info_service = GeoInfoService(metadata)


if __name__ == '__main__':
    engine = create_engine('mysql+pymysql://sqladmin:Qwedsazxc123@staging-mysql.c0wj8qdslqom.ap-southeast-1.rds.amazonaws.com/geodb', echo=True)
    metadata = MetaData(bind=engine)
    srvc = GeoInfoService(metadata)
    location = srvc.find_one(srvc.get_table().c.name == 'dahkora')
    print(location.as_dict())



class ServiceHandle():
    host = "local"
    classpath = None
    id = None
    service = None
    def __init__(self, classpath, id):
        self.classpath = classpath
        self.id = id

    @classmethod
    def local_service(cls, classpath, id, service):
        handle = ServiceHandle(classpath, id)
        handle.service = service
        return handle

    @classmethod
    def remote_service(cls, host, classpath, id):
        handle = ServiceHandle(classpath, id)
        handle.host = host
        return handle
        
    def has_id(self):
        """ Returns true if this service has an id.
        """
        return self.id is not None

    def is_remote(self):
        """ Returns true if the host attribute is not 'local'.
        """
        return self.host != ServiceHandle.host

    def with_host(self, otherhostname):
        """ Returns a copy of this servicehandle whose host attribute is equal to the given one.
        """
        return ServiceHandle.remote_service(otherhostname, self.classpath, self.id)

    def address(self):
        """ Creates the address of this service.
        """
        if not self.is_remote():
            raise ValueError("No need to access address if the service is accessed through this server.")
        else:
            return self.host + "/" + self.classpath + "/" + self.id

    def is_serialized(self):
        """ returns true if the service attribute is not None.
        """
        return self.service is not None

    def set_host(self, host):
        """ Sets the host attribute with the given one. 
        """
        if host is None:
            raise ValueError("Host is not allowed to be None.")
        self.host = host

    def to_dict(self):
        """ Creates a dictionary filled with the info of this service handle.
        """
        return {
            "host" : self.host,
            "classpath" : self.classpath,
            "id" : self.id
        }
    
    @classmethod
    def from_dict(cls, d):
        """ Creates a servicehandle object from the dictionary entries in 'd'.
        """
        return ServiceHandle.remote_service(d["host"], d["classpath"], d["id"])

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return str(self.to_dict())

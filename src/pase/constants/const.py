

class _const:
    class ConstError(TypeError): pass
    def __setattr__(self, name, value):
        if(self.__dict__.has_key(name)):
            raise self.ConstError(f"Can't rebind const({name})")

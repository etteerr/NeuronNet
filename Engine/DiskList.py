import struct

class DiskList:
    #Picklers
    def __getinitargs__(self):
        return self._args

    def __getstate__(self):
        return self._args

    def __setstate__(self,state):
        self.__init__(*state)

    def __init__(self, file, type=('f',4), buffersize=128, chunker=131072, readonly=False, overwrite=False):
        #Buffer size in elements!
        #chunker: Buffer size for operand operations in items (default 1mb where item size is 8)
        import io
        import os
        self._args = (file, type, buffersize, chunker, readonly, False)
        self._dict = {
            'file': file,
            'type': type,
            'buffersize': buffersize,
            'chunker': chunker,
            'readonly': readonly,
            'overwrite': False
        }
        try:
            if readonly:
                self._file = io.FileIO(file, 'rb')
                self._buffer = io.BufferedReader(self._file, buffersize * type[1])
            elif overwrite:
                self._file = io.FileIO(file, 'wb+')
                self._buffer = io.BufferedRandom(self._file, buffersize * type[1])
            else:
                self._file = io.FileIO(file, 'ab+')
                self._buffer = io.BufferedRandom(self._file, buffersize*type[1])
            self._itemsize = type[1]
            self._type = type[0]
            self._items = int(os.path.getsize(file)/type[1])
            self._chunker = chunker
        except:
            print('Error while opening file: %s' % file)
            raise

    def append(self, data):
        self._buffer.seek(0,2)
        if isinstance(data,list):
            self._buffer.write(struct.pack(str(len(data))+self._type[0], *data))
        else:
            self._buffer.write(struct.pack(self._type[0], data))
        self._items += 1

    def __getitem__(self, item):
        self._buffer.flush()
        self._buffer.seek(item*self._itemsize)
        bytes = self._buffer.read(self._itemsize)
        item  = struct.unpack(self._type, bytes)
        return item

    def getitemcount(self):
        return self._items

    def getsizebytes(self):
        return self._itemsize*self._items

    def getList(self):
        self._buffer.seek(0)
        return list(struct.unpack(str(self._items) + self._type, self._buffer.read()))



    #Operands

    def __add__(self, other):
        if isinstance(other, list):
            if not len(list) == self._items:
                raise ValueError('Sizes of both object must be equal')
            it = 0

            for i in grouper(other,self._chunker):
                #load data
                self._buffer.seek(it * (self._chunker*self._itemsize))
                data = list(struct.unpack(str(self._chunker)+self._type,  #size - type
                                     self._buffer.read(self._chunker*self._itemsize))) #byte data
                # Operation
                data += i
                # Save data
                self._buffer.seek(it * (self._chunker * self._itemsize))
                self._buffer.write(struct.pack(str(len(data))+self._type, *data))


    def __sub__(self, other):
        if isinstance(other, list):
            if not len(list) == self._items:
                raise ValueError('Sizes of both object must be equal')
            it = 0

            for i in grouper(other, self._chunker):
                # load data
                self._buffer.seek(it * (self._chunker * self._itemsize))
                data = list(struct.unpack(str(self._chunker) + self._type,  # size - type
                                          self._buffer.read(self._chunker * self._itemsize)))  # byte data
                # Operation
                data -= i
                # Save data
                self._buffer.seek(it * (self._chunker * self._itemsize))
                self._buffer.write(struct.pack(str(len(data)) + self._type, *data))

    def __mul__(self, other):
        if isinstance(other, list):
            if not len(list) == self._items:
                raise ValueError('Sizes of both object must be equal')
            it = 0

            for i in grouper(other, self._chunker):
                # load data
                self._buffer.seek(it * (self._chunker * self._itemsize))
                data = list(struct.unpack(str(self._chunker) + self._type,  # size - type
                                          self._buffer.read(self._chunker * self._itemsize)))  # byte data
                # Operation
                data *= i
                # Save data
                self._buffer.seek(it * (self._chunker * self._itemsize))
                self._buffer.write(struct.pack(str(len(data)) + self._type, *data))

    def __div__(self, other):
        if isinstance(other, list):
            if not len(list) == self._items:
                raise ValueError('Sizes of both object must be equal')
            it = 0

            for i in grouper(other, self._chunker):
                # load data
                self._buffer.seek(it * (self._chunker * self._itemsize))
                data = list(struct.unpack(str(self._chunker) + self._type,  # size - type
                                          self._buffer.read(self._chunker * self._itemsize)))  # byte data
                # Operation
                data /= i
                # Save data
                self._buffer.seek(it * (self._chunker * self._itemsize))
                self._buffer.write(struct.pack(str(len(data)) + self._type, *data))

    def __eq__(self, other):
        if isinstance(other, list):
            if not len(list) == self._items:
                raise ValueError('Sizes of both object must be equal')
            it = 0

            for i in grouper(other, self._chunker):
                # load data
                self._buffer.seek(it * (self._chunker * self._itemsize))
                data = list(struct.unpack(str(self._chunker) + self._type,  # size - type
                                          self._buffer.read(self._chunker * self._itemsize)))  # byte data
                # Operation
                if not data == i:
                    return False
                # Save data
                self._buffer.seek(it * (self._chunker * self._itemsize))
                self._buffer.write(struct.pack(str(len(data)) + self._type, *data))
        return True


# Help functions
def grouper(iterable, n):
    offset = 0
    while True:
        if offset + n < len(iterable):
            yield iterable[offset:offset+n]
            offset += n
        else:
            yield iterable[offset:len(iterable)]
            break

# Defs
char = ('c', 1)
signed_char = ('b', 1)
unsigned_char = ('B', 1)
unicode = ('u', 2)
signed_short = ('h', 2)
unsigned_short = ('H', 2)
signed_int = ('i', 2)
unsigned_int = ('I', 2)
signed_long = ('l', 4)
unsigned_long = ('L', 4)
float = ('f', 4)
double = ('d', 8)
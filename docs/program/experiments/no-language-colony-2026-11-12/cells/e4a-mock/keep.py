import lzma
class C:
    @staticmethod
    def compress_all(data):
        return lzma.compress(data, preset=4, check=lzma.CHECK_CRC32)
    @staticmethod
    def decompress_all(packed):
        return lzma.decompress(packed)

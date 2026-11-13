import time
import compress

def main():
    data = open('corpus.txt', 'rb').read()
    start = time.monotonic()
    while True:
        packed = compress.compress(data)
        if compress.decompress(packed) != data:
            print(0)
            return
        if time.monotonic() - start >= 0.4:
            break
    open('out.bin', 'wb').write(packed)
    print(100 * (1 - len(packed) / len(data)))

if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(0)

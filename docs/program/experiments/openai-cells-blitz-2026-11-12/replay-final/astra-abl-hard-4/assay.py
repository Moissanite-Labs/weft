"""Exercise both codec directions for at least 0.4 seconds, then score size."""
import time
import compress


def main():
    source = open('corpus_hard.txt', 'rb').read()
    deadline = time.perf_counter() + 0.4
    while True:
        encoded = compress.compress(source)
        decoded = compress.decompress(encoded)
        if decoded != source:
            print(0)
            return
        if time.perf_counter() >= deadline:
            break
    with open('out.bin', 'wb') as f:
        f.write(encoded)
    with open('restored.txt', 'wb') as f:
        f.write(decoded)
    print(100 * (1 - len(encoded) / len(source)))


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print(0)

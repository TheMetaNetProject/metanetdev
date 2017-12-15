import sys

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        out = False
        for line in f:
            if line.startswith('gr-list'):
                out = True
                continue
            if len(line) <= 1:
                out = False
                continue
            if out:
                sys.stdout.write(line)


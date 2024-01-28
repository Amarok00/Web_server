import logging
from optparse import OptionParser

from htmyserv import MyServer


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-r", "--root", action="store", type="string", default=".")
    op.add_option("-w", "--workers", action="store", type=int, default=3)
    op.add_option("-t", "--timeout", action="store", type=float, default=3.0)
    op.add_option("-l", "--log", action="store", default=None)
    op.add_option("-v", "--level", action="store", type=int, default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(
        filename=opts.log,
        level=opts.level or logging.INFO,
        format="[%(asctime)s] %(levelname).1s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
    )
    server = MyServer(
        host=args[0] if len(args) else "",
        port=opts.port,
        max_workers=opts.workers,
        timeout=opts.timeout,
        basedir=opts.root,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.close()

# OTUServer

Example simple HTTP server written around sockets. Spawns requested number of workers in separate threads ('pool of threads' was not 100% implemented). Serves "HEAD" and "GET" HTTP-requests.

Tests (httptest.py and httptest dir): <https://github.com/s-stupnikov/http-test-suite>

## How to run server

`python3 httpd.py`
default port": 8080

`pytest httptest.py`
to run tests from the `httptest.py` file

Test page:

<http://localhost:8080/httptest/wikipedia_russia.html>

All tests of httptest.py completed successfully.

## Benchmark

`$ ab -n 50000 -c 100 -r <http://localhost:8080/>`

Server Software:        OTUServer
Server Hostname:        localhost
Server Port:            8080

Document Path:          /
Document Length:        328 bytes

Concurrency Level:      100
Time taken for tests:   35.150 seconds
Complete requests:      50000
Failed requests:        6
   (Connect: 0, Receive: 0, Length: 6, Exceptions: 0)
Total transferred:      23397192 bytes
HTML transferred:       16398032 bytes
Requests per second:    1422.46 [#/sec] (mean)
Time per request:       70.301 [ms] (mean)
Time per request:       0.703 [ms] (mean, across all concurrent requests)
Transfer rate:          650.03 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    8  89.5      0    1036
Processing:     3   50 190.9     46   13319
Waiting:        1   49 180.5     46   13318
Total:          7   58 233.6     46   14330

Percentage of the requests served within a certain time (ms)
  50%     46
  66%     50
  75%     52
  80%     53
  90%     56
  95%     60
  98%     73
  99%     88
 100%  14330 (longest request)
# Web_server

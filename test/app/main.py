from fastapi import FastAPI
from fastapi import Header      #for post request with header
from pydantic import BaseModel

from fastapi.exceptions import HTTPException
from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram
from fastapi import FastAPI
import prometheus_client








class item(BaseModel):
    element: str          # key "element" -- is string
class item2(BaseModel):
    expr: str          # key "expr" -- is string with data

app = FastAPI()

metrics_app = prometheus_client.make_asgi_app()
app.mount("/metrics", metrics_app)

c = Counter('http_requests_total', 'Number of HTTP requests received', {'method', 'endpoint'})
g = Gauge('last_sum1n', 'Value stores last result of sum1n')
gfibo = Gauge('last_fibo', 'Value stores last result of fibo')  
gsize = Gauge('list_size', 'Value stores last result of size')  
gcalcualtor = Gauge('last_calculator', 'Value stores last result of calculatro')
calcerr = Counter('errors_calculator_total', 'Number of errors in calculator')
h = Histogram('http_requests_milliseconds', 'Duration of HTTP requests in milliseconds', {'method', 'endpoint'})

@app.get("/sum1n/{x}") #{x} variable
async def read_item(x: int): #x: int   - states that our variable should be integere
    c.labels(method='get', endpoint='/sum1n').inc
    h.labels(method='get', endpoint='/sum1n').time()
    sum = 0
    i = 0
    for i in range(x+1):
        sum=sum+i
    g.set(sum) 
    return {"result": sum}

@app.get("/fibo")
async def fibo(n: int):      #?n=   --- states that our variable n equal to, and it is interger
    c.labels(method='get', endpoint='/fibo').inc
    h.labels(method='get', endpoint='/fibo').time()
    fib=[]
    fib.append(0)
    fib.append(1)
    nextn=0
    for i in range(2,n):
        nextn=fib[i-2]+fib[i-1]   
        fib.append(nextn)
    gfibo.set(fib[n-1])
    return {"result": fib[n-1]}


@app.post("/reverse")
async def reverse(string: str = Header(default=None)):     #"string" is a key from URL, str goes for string, header was imported 
     c.labels(method='post', endpoint='/reverse').inc
     h.labels(method='get', endpoint='/reverse').time()
     new = ""
     for i in string:
         new=str(i)+new         #str(i) --- states that "i" from word "string" is string(str)
     return {"result": new}

arr=[]   #global array

@app.put("/list")
async def list(gv: item):   #gv=given data "key:value", item goes for Class where we have key "element"
    value=gv.element        #.element gives us "value" of key "element"
    arr.append(value)
    c.labels(method='put', endpoint='/list').inc
    h.labels(method='get', endpoint='/list').time()
    return  value

@app.get("/list")
async def list():
    gsize.set(len(arr))
    c.labels(method='get', endpoint='/list').inc
    h.labels(method='get', endpoint='/list').time()
    return {"result": arr}


@app.post("/calculator")
async def calculator(gv:item2): #gv -given value
    c.labels(method='post', endpoint='/calculator').inc
    h.labels(method='get', endpoint='/calculator').time()
    value=gv.expr
    x=value.split(",")
    
    z=x[0]
    y=x[2]
    if not z.isnumeric() or  not y.isnumeric():
        calcerr.inc()
        raise HTTPException(400, detail={"error": "invalid"})

    arr1="+-*/"
    a=int(x[0])
    b=int(x[2])
    
    if x[1] not in arr1:
        calcerr.inc()
        raise HTTPException(400, detail={"error": "invalid"})

    if x[1]=="-":
        gcalcualtor.set(a-b)
        return a-b
    if x[1]=="+":
        gcalcualtor.set(a+b)
        return a+b
    if x[1]=="*":
        gcalcualtor.set(a*b)
        return a*b
    if x[1]=="/" and b!=0:
        gcalcualtor.set(a/b)
        return a/b
    calcerr.inc()
    raise HTTPException(403, detail={"error": "zerodiv"})

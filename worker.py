import time
from internal.redis import RedisClient
from usecases.evaluate_usecase import evaluate_async_cv

def main():
    rc = RedisClient()
    while True:
        try:
            rc.run(handler=evaluate_async_cv)  # blocking listen loop
        except Exception as e:
            print(f"[redis-worker] error: {e}, retrying in 3s")
            time.sleep(3)

if __name__ == "__main__":
    main()
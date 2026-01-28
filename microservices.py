import multiprocessing
import uvicorn
import sys
import os

BASE_DIR = os.path.join(os.path.dirname(__file__), "microservices")
sys.path.append(BASE_DIR)
print("BASE_DIR:", BASE_DIR)

# Mapping of microservice file -> port
services = {
    "admin.app.main:app": 8010,
}



def run_service(app_path, port):
    uvicorn.run(app_path, host="192.168.1.6", port=port, reload=False)

if __name__ == "__main__":
    processes = []

    for app_path, port in services.items():
        p = multiprocessing.Process(target=run_service, args=(app_path, port))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

# Installation guide

## Prediction service

#### Prerequisites:
- python >= 3.11 installed on the machines
- be in the root of project (if using source code from project report appendices - `/source_code`)

#### How to run:
1. Create virtual environment
    - there are many ways to do it but the one proposed here uses builtin python venv command `python -m venv venv`
2. Start virtual environment -> `source venv/bin/activate` (on unix env), `.\venv\Scripts\activate` (on Windows, though development was only done on unix systems)
3. Install dependencies -> `pip install -r requirements.txt`
4. Run prediction service -> `python -m ml.inference.app`
    - server will start on localhost with port 8000
    - source code from project report appendices includes model files from training on ImageNet subset, so the prediction service will use these

## BFF server

#### Prerequisites:
- golang installed on the machines (from version 1.22.5 upwards is safe)
- be in the root of project (if using source code from project report appendices - `/source_code`)

#### How to run:
1. Change directory into backend directory -> `cd backend`
2. Start server -> `go run main.go`
    - server will start on localhost with port 4200

## Frontend

#### Prerequisites:
- node.js installed on the machines (from version 20 upwards is safe)
- npm installed on the machine (from version 10.7 upwards is safe)
- be in the root of project (if using source code from project report appendices - `/source_code`)

#### How to run:
1. Change directory into frontend directory -> `cd frontend`
2. Install dependencies -> `npm install`
3. Start Next.js server -> `npm run dev`
    - server will start on localhost with port 3000
    - entering url `localhost:3000` in the browser will redirect to project's user interface

Once all 3 services are running the system is fully functional and can be used.
Remember that the system accepts only folders containing images (or nested folders containing images -> 1 level of nesting) during upload.
The model files loaded into the service are trained on images of few kitchen appliances like espresso machines, washing machines, hair dryiers, toasters.

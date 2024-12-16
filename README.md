# PTIC
Bachelor project VIA university (2024) - PTIC (Product Taxonomy Image Classification)

### Problem we want to solve:
- classifying product data to master data hierarchy based on product images

### Value behind the project:
When retailers onboard suppliers product, the data model can be completely different, so both attributes on product as well as taxonomy they are using in MDM.
Businesses have to classify the data manually and then also map data between supplier's attributes and their attributes.
We want to automatize the entire process, the system using just supplier's photos will automatically classify product, which will allow it to access attributes on the product and then it will try to map the attributes between products (not in the scope of this project, it focuses on the first part so classifying into taxonomy using image data).

### Solution structure:
Basically the solution can be split into 2 main parts:
- classifying into hierarchy based on images
    - utilizes top-down hierarchical classification
    - trains a resnet convolution network for each internal node in the hierarchy
    - all the predictions of models are combined into singular prediction using hierarchy matrix mask and linear algebra
    - solution comes with frontend exposing user interface and allowing parallel handling of many files using golang server and websockets
- automatic mapping between attributes (not in the scope of the project)

## Deployment philosophy:
#### Frontend
- deployed on vercel (used personal account so probably only @hedrekao can change it)
#### Backend (GO websocket server + python prediction server)
- deployed as container group using terraform (Infrastructure as Code)
- additional nginx container serving as reverse proxy allowing tls connection
- docker images deployed to github registry (for now also under @hedrekao)
- once the infra is deployed using terraform, it is enough to update images in registry and restart container and it will update
- self-signed ssl certificate -> forces to turn off nextjs image optimization (they see it as too dangerous -> it would have to use let's encrypt, but it might be overkill for this project)
- no access to many features on azure, service principal, therefore cannot include deploy to CI and had to do few workarounds
- due to using self-signed certicate modern browsers treat the website as insecure at it is not possible to establish websocket connection (on firefox based browsers it is possible to set the website as an exception so that it can be used)


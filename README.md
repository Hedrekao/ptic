# ICaAM
Bachelor project VIA university (2024) - ICaAM (Image Classification and Attribute Mapping}

### Problem we want to solve:

- classifying products to hierarchy based on product images
- once product is classify map the attributes

### Value behind the project:
When retailers onboard suppliers product, the data model can be completely different, so both attributes on product as well as taxonomy they are using in MDM. Businesses have to classify the data manually and then also map data between supplier's attributes and their attributes. We want to automatize the entire process, the system using just supplier's photos will automatically classify product, which will allow it to access attributes on the product and then it will try to map the attributes between products.

### Project structure:
Basically the project can be split into multiple bits:
- classifying into hierarchy based on photos
	- the base of the project, most important bit
- automatic mapping between attributes 
	- more complex, would be nice to have but if we don't it is still fine
- some frontend where you can upload photos, see predictions, see mappings, see attributes required in predicted hierarchy
- some infrastructure for automatic training (basic mlops -> maybe using mlflow, we will see)

### Tech stack:
- for ml -> I would vote for pytorch, but we are learning keras in school, so it is up for debate
- for mlops -> some container with gpu, mlflow to track trainings
- for fe -> next, ts whatever xd
- for inference -> I guess fastapi, because how otherwise we would use the model

I would love to somehow put golang in there, but no idea how to fit it anywhere.

### First steps:
- writing proper requirements for the analysis 
- some diagram that will show in very abstract way how the the flow be (like upload tons of images to train then upload the data to get predictions, then get mappings)
- finding open source datasets to validate classifications model on
- talking with stibo for customer dataset with photos and attributes
- find and read interesting papers:
	- on convolution neural nets
	- on transformers???
	- on hierarchy classification (maybe different then we classes are not in the tree idk)
	- open source datasets benchmark
- mock design for fe 
- sketch design flow (also architecture on infra) -> research where we can train

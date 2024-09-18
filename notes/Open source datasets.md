---
tags:
  - ml
  - bachelor
  - uni
---
- ImageNet
	- [paper](https://www.image-net.org/static_files/papers/imagenet_cvpr09.pdf)
	- kinda standard benchmark
	-  avg 1000 images for each category
	- it has hierarchical format, so we have leaf nodes categories as well as internal nodes categories __very important for us because the actual target data from companies would also be hierarchical__
	- the categories are either a noun or a meaningful combination of words (synset)
	- build upon WordNet, uses the categories from there
	- around 22k categories
	- 12 subtrees of categories

	![[assets/imagenet.png]]
	- maybe we can just pick a subtree and train on it
	- the dataset cares a lot about diverse data meaning different backgrounds, different positions of objects
	- it has clean images
	- average size 400x350
	- the images and their labels are not confusing (meaning image cannot belong to 2 categories at once)
	- probably the most popular subset is called ILSVRC and it has 1000 categories

To sum up this feels like the perfect dataset for us, at least to start with, we just need to find good subset of it as the entire thing is way too big.
- Cifar100
	-
- Open Image Dataset by Google
	-

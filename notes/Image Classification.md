---
tags:
  - uni
  - ml
  - bachelor
---
Basically I believe that we can just do big convolution net with normalization. (batch norm, AdamW)

Probably we can follow the mlac stuff Simon did, where we train model per class in hierarchy (also for the parent nodes), and then somehow on prediction we combine predictions from different models.

So the idea also mentioned in ImageNet paper to train binary classifier for each hierarchy, we take 90% of data of this hierarchy as positive examples and then take x images from other hierarchies (excluding child and parent hierarchies) as negative examples and the rest 10% is for testing. Then when we don't just predict for value for specific node, but rather for all the children and then the maximum of responses in subtree becomes the final score. This idea is called Tree-max classifier.

It looks on the benchmark that it outperforms, just normal classification into leaf category (at least at higher levels)
![[assets/tree_level_acc.png|450]]

To exploit a hierarchy, we could also do a custom loss function where cost of predicting node closer in a tree (like a parent) should _cost_ less than prediction completely foreign concept. Basically we would punish the model more the higher in tree the classifying mistake happened.

Also we could make it so that the more photos user uploads the more certain prediction is, as we would do prediction per image and average the class, that way the result we would get would be more certain

## Requirements

### Functional

#### UI:

- The system must provide a user-friendly UI for users to upload individual images or entire folders
- Users can select either automatic or semi-automatic clasification (chose between 3 most accurate categories)
- Multiple images of the same product must be accepted for higher prediction certainty (averaging predictions across images)

#### Hierarchical Classification with Tree-max Classifier:

- The system will use a Tree-max classifier that predicts for all nodes in the hierarchy, and the final classification score is the maximum response from the subtree
- A binary classifier will be trained for each hierarchy level using 90% of data as positive and x images from unrelated categories as negative. The remaining 10% of data is reserved for testing

#### Custom Loss Function:

- The system will employ a custom loss function where classification mistakes closer in the hierarchy incur a smaller penalty than mistakes further away

#### Prediction Averaging for Multiple Images:

- When multiple images are uploaded for a product, the system will predict per image and average the results to increase the certainty of classification

### Non-Functional:

#### Scalability:

- The system must handle large-scale datasets and multiple image uploads efficiently
- System should support hierarchical classifications of deep trees with multiple sublevels and large datasets

#### Performance:

- The model should be optimized for real-time classification
- Prediction for folders with many images should not significantly slow down the system

#### Accuracy:

- The system needs to focus on high classification accuracy, especially for objects at deeper hierarchy levels
- Averaging predictions for multiple images should significantly boost confidence in the results

#### Usability:

- The UI must be intuitive, with options to easily navigate, upload, and (categorize ?) images
- Visual feedback for predictions (e.g., classification accuracy) and penalties for errors should be clear and informative

#### Security:

- The system should ensure secure storage of uploaded images and protect any sensitive data shared by the user

#### The system should allow for modular training of classifiers, so new hierarchies or categories can be added without retraining the entire model (?)

## User cases

1. As a User, I want to be able to upload multiple images of a product or item (via folders or individual images) so that I can categorize the product with better accuracy.
2. As a User, I want to be able to choose between semi-automatic or automatic modes, so I can have an option to manually choose the corect category from 3 most accured ones.
3. As a User, I want to have (an option to see) feedback on classification confidence (e.g., a percentage) for each uploaded image, so that I can assess the certainty of the system’s predictions.
4. As a User, I want to be able to batch upload a large dataset of product images from different categories, so that I can classify multiple products at once efficiently.

#### some other ideas

- As a User, I want to be able to view the classification history and performance over time (accuracy, penalties, confidence scores), so I can track how well the system is performing for my product categorization.
- As a User, I want the system to notify me when a classification result has low confidence, so that I can review and upload more images to improve accuracy.

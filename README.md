# APS-6-2025
a work for the 6th semester of computer science at UNIP (Ribeirão Preto) with the aim of making an application in Python with OpenCV for image processing

# Fruit Quality Inspection (Python & OpenCV)
This project provides a simple computer vision solution for automatic fruit quality inspection using Python and OpenCV. The code segments the fruit in the image and analyzes visual defects to determine if the fruit is in good condition. Five fruit types are supported: banana, apple, orange, tomato, and strawberry.
All logic is easy to adapt for new fruit types or more advanced inspection methods.

# Requirements

 - Python 3.x

 - Libraries: opencv-python, numpy

Install dependencies using:

```bash
pip install opencv-python numpy
```
# Usage Instructions

1. Save your fruit images in the same folder as the script, with the following names:

 - banana.jpg

 - maca.jpg

 - laranja.jpg

 - tomate.jpg

 - morango.jpg

2. Run the script:

python FruitQualityInspection.py

3. For each fruit, the program will show a segmented image and print the quality diagnosis in the terminal.

#Notes

 - Best results are obtained with well-lit, high-quality photos and a clean, contrastive background.

 - The code uses simple rules for defect detection, based on pixel color and texture. For improved performance on varied backgrounds, you may need to adjust the color segmentation ranges or use a more robust image segmentation technique.

- To add new fruits, simply adjust or add segmentation ranges and rules in the script.

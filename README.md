# APS-6-2025
a work for the 6th semester of computer science at UNIP (Ribeirão Preto) with the aim of making an application in Python with OpenCV for image processing

# Fruit Quality Inspection (Python & OpenCV)
This project provides a simple computer vision solution for automatic fruit quality inspection using Python and OpenCV. The code segments the fruit in the image and analyzes visual defects to determine if the fruit is in good condition. Five fruit types are supported: banana, apple, orange, tomato, and strawberry.
All logic is easy to adapt for new fruit types or more advanced inspection methods.

# Requirements

 - Python 3.x

 - Libraries: opencv-python, numpy, colorama

Install dependencies using:

```bash
pip install opencv-python numpy colorama
```
# Usage Instructions

1. Place your fruit images inside the corresponding folders:

 - **banana/**

 - **maca/**

 - **laranja/**

 - **tomate/**

 - **morango/**

You can use any filename and any supported image format (e.g., .jpg, .png).

2. Run the script:

```
python FruitQualityInspection.py
```

3. For each fruit, the program will show a segmented image and print the quality diagnosis in the terminal.

# Interface & Visualization

 - The segmented images (with the correct mask) are displayed on screen using an OpenCV window.

 - After each image, press any key to continue to the next one.

 - If you do not see the windows, ensure you are running outside Jupyter/Colab and using a graphical environment (on Linux WSL, configure an X server as needed).

# Customization and Troubleshooting

 - Adjust the defect tolerance threshold by changing the variable criterio_banana in the code.

 - You can modify the HSV color range intervals in the functions to adapt for new fruits, different lighting, or backgrounds.

 - The “Defect Mask” window shows in white the pixels identified as defective—use this to debug detection accuracy.

 - All results are also printed in the terminal.

# Notes

 - Best results are obtained with well-lit, high-quality photos and a clean, contrastive background.

 - The code uses simple rules for defect detection, based on pixel color and texture. For improved performance on varied backgrounds, you may need to adjust the color segmentation ranges or use a more robust image segmentation technique.

- To add new fruits, simply adjust or add segmentation ranges and rules in the script.

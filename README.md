
# Quick Start

After having followed the [installation](#installation) instructions, Nautilus-OCR can be run by using the included BnL models and example JSON data for the purpose of enhancement

### Copy BnL Models

With `ocr_enhance/` as the current working directory, first copy the BnL models to the `final/` folder.<sup>1</sup>

	cp models/bnl/* models/final/

### Run Enhancement

Next, run [enhance](#enhance) on the `data/examples/` directory, containg a single issue `NZG-1881-10-01-a`

	python3 src/main.py enhance -d data/examples -r 0.02

This command generates a new JSON file for every block with a minimum enhancement prediction of 2%. Finally, the newly generated files can be located in `data/examples/NZG-1881-10-01-a/enhanced`.

<sup>1</sup> As explained in `models/final/README.md`, the models within `models/final/` are automatically applied when executing the **enhance**, **train-epr**, **ocr** and **test-ocr** actions. Models outside of `models/final/` are supposed to be stored for testing and comparison purposes.

### Alternate Way: Using S3

Alternatively, instead of using the examples from data/examples/, you can directly download the issues and pages from the S3 bucket by adding the details in .s3cfg <sup>2</sup> Once the information in the configuration file is complete, execute the following command:

	python3 src/main.py enhance -d .s3cfg -r 0.02

<sup>2</sup> The template for configuratioin file can be found in `.s3cfg`

# Requirements

Nautilus-OCR requires:

* **Linux / macOS**<br>
The software requires dependencies that only work on Linux and macOS.
Windows is not supported at the moment.
* **Python 3.8+**<br>
The software has been developed using Python 3.8.5.
* **Dependencies**<br>
Access to the libraries listed in `requirements.txt`.
* **Impresso Data**<br>
Issues along with Pages and corrsponding images as the data in the JSON format

# Installation

With Python3 (tested on version 3.8.5) installed, clone this repostitory and install the required dependencies:

	git clone git@github.com:kartikeysharma95UZH/ocr_enhance.git
	cd ocr_enhance
	pip3 install -r requirements.txt

Hunspell dependency might require:

	apt-get install libhunspell-dev
	brew install hunspell

OpenCV dependency might require:
	
	apt install libgl1-mesa-glx
	apt install libcudart10.1

You can test that all dependencies have been sucessfully installed by running

	python3 src/main.py -h
	
and looking for the following output:

```
Starting OCR Enhancement

usage: main.py [-h] {enhance} ...

OCR Enhancement Command Line Tool

positional arguments:
  {enhance}   sub-command help

optional arguments:
  -h, --help  show this help message and exit
```

# Modules

### **enhance**

Applies ocr on a set of original Impresso JSONL data, while aiming to enhance ocr accuracy.<sup>1</sup><br>
An optional enhancement prediction model can prevent running ocr for some target blocks.<br> 
Models in `models/final/` are automatically used for this action.<sup>2</sup>

| Option| Default | Explanation |
| :-------------- | :------- | :---------- |
|**-d --directory**||Path to directory containing all orignal Impresso Issues |
|-r --required|0.0|Value for minimum required enhancement prediction <sup>1</sup>|

<sup>1</sup> Enhancement predictions are in range [-1,1], set to -1 to disable epr and automatically reprocess all target blocks.<br>

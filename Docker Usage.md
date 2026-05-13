# Instructions for Using w/ Docker
Some people may want to use our Docker image for easier setup and usage. You can build it locally or download our prebuilt image (browservm/metadata-stripper).

## How to Use Locally
1. **Build the image:**
    
    Open your terminal in the folder containing both files and run: ```docker build -t metadata-stripper .```
2. **Run the Container:**

    Since the script needs to access files on your actual computer, you need to "mount" a folder. Replace ```/path/to/your/photos``` with the actual folder on your computer: ```docker run -it --rm -v "/path/to/your/photos:/data" metadata-stripper```.
3. **Inside the App:**

    When the script asks for a path, simply type ```/data``` to process everything you linked in Step 2.

## How to Use Prebuilt Image
1. **Pull the Image:**

    Simply run ```docker pull browservm/metadata-stripper:main``` to pull our prebuilt Docker image.
2. **Run the Container:**

    The idea is basically the same, except replace ```metadata-stripper``` with ```browservm/metadata-stripper:main``` to run it.
3. **Inside the App:**

    Same as Step 3 with the local image.
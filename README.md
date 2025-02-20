
# MKVEditor

MKVEditor is a web based application that allows the user to view and edit the Video, Audio and Subtitle tracks in `.mkv` media files. I built it after noticing many of the `.mkv` files I kept had incorrect default Audio/ Subtitle tracks. With MKVEditor, I can now quickly search for incorrectly set default tracks, and fix them quickly, all through a simple, easy to use web interface.

## Software Stack

For this project, I used python for the backend along with flask for the web framework. I went with this as I didn't need any fancy features a full web framework would provide, and using python made it very easy to interact with the command-line application `mkvtoolnix` which was used to scan/ edit the `.mkv` files.

## Web Interface

The frontend is very simple, with 4 main windows:
- Home (currently just empty)
- Movies
- TV Shows
- File Window
- Find Incorrect Defaults

### Movies
The Movies window contains a file explorer style window, allowing the user to explore all the movies in their library as shown below:

![image](https://github.com/user-attachments/assets/4cfa82af-433e-441f-8037-be42709cde31)


### TV Shows
The TV Shows window is similar, again containing a file explorer style window to explore all TV shows.

![image](https://github.com/user-attachments/assets/6fa076a9-4204-4416-8888-aa8eac649e55)


### File Window
The File Window provides an interface to view/ edit the tracks in an `.mkv` file. This window is opened whenever the user clicks on a file using the either the Movie file explorer or TV Shows file explorer.

![image](https://github.com/user-attachments/assets/86883bf1-a0d2-4c73-8f52-1d6b6cc09051)


### Find Incorrect Defaults
The Find Incorrect Defaults window is used to search for media where the default tracks do not match a given set of languages. The set of correct languages is set using the search bare shown below:

![image](https://github.com/user-attachments/assets/2d7b542e-102a-445e-b922-ef2a0d81588b)


When the user presses the search button, the backend will start scanning through the whole media library, getting the track information about all the files, and then filtering out the ones with bad default tracks. As this process usually takes quite some time, the backend will also cache the results in `.json` format, only re-scanning if the media library gets changed. The filtered results are then presented as shown below, allowing the user easily to scroll through them and edit the default tracks.

![image](https://github.com/user-attachments/assets/b93950cb-5c3d-48c2-9141-1ed69d26bc51)


### Process Status Readout

As some processes take a while on the backend (e.g. scanning whole media library), it is useful to see what's currently happening on the frontend. Hence, I also added a status bar on the bottom that reads out current processes, as shown below:\

![image](https://github.com/user-attachments/assets/b0ed0e5d-ee29-4d63-a330-ef2bb2e5fba9)


## Docker Deployment

To deploy this project, it made sense to use docker as it made it super easy to deploy the project to my server, which since it used Unraid, was already heavily built around using docker based applications. Variables such as media library directories were set through environment variables, making it super easy to setup.

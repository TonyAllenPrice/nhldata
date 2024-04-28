# NHL Stats

The aim of this project is to build a Python wrapper module for the various public NHL APIs and data sources. 

## NHL APIs

The first module here is *nhl_api* which is a module built to connect to the two public facing NHL APIs. The endpoint documentation is based on [NHL-API-Reference](https://github.com/Zmalski/NHL-API-Reference) by Zmalski.

There are two classes (Web and Stats), each with unique calls inside. It is highly recommended that you reference Zmalski's work to understand what each call is doing, but there are docstrings for each function in the classes.

## MoneyPuck.com

The second module is designed to access the available data from [MoneyPuck.com](https://moneypuck.com/data.htm). This is a series of .csv files that are converted to lists of dictionaries.

Of particular interest here is the shots data that MoneyPuck has going back to 2007/2008. THese are transported as .zip files and unpacked into list/dict structures for consumption. This is from thier documentation:

> All historical shot data is available to download. This includes 1,717,746 shots from the 2007-2008 to 2022-2023 seasons. Data for the 2023-2024 season is also available and updated nightly on this page. Saved shots on goal, missed shots, and goals are included. Blocked shots are not included in these datasets. There are 124 attributes for each shot, including everything from the player and goalie involved in the shot to angles, distances, what happened before the shot, and how long players had been on the ice when the shot was taken. Each shot also has model scores for its probability of being a goal (xGoals) as well as other models such as for the chance there will be a rebound after the shot, the probability the shot will miss the net, and whether the goalie will freeze the puck after the shot. The data has been collected from several sources including the NHL and ESPN. A good amount of data cleaning has also been done on the data. Arena adjusted shot coordinates and distances are also calculated in the dataset using the strategy War-On-Ice used from the method proposed by Schuckers and Curros.

## Additional Sources

If you know of another strong data soucre for NHL stats date, please let me know/submit a push request and we can get it added here. Happy to talk about expected format and such.
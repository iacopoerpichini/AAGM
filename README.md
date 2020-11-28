# Advanced Algorithms and Graph Mining

The project aim is to become comfortable with the Python tools studied in the lectures during the course Advanced Algorithms and Graph Mining and to improve algorithmic skills.

In particular, we use [NetworkX](https://networkx.github.io/) to create and to manage graph algorithm and [Pandas](https://pandas.pydata.org/docs/) to visualize the COVID-19 data.

The data used to test the algorithm are the covid dataset of the Italian Department of Civil Protection. 

Data are available at [https://github.com/pcm-dpc/COVID-19](https://github.com/pcm-dpc/COVID-19).

The project is divided into two parts:
+ The first one uses Python 3.7 for running two algorithms and to analyze some different implementations and to study their complexity.  
+ The second part is an analysis which uses some libraries for data analysis collected in a Jupyter Notebook.

There is also a .pdf document that explains in detail the algorithm implemented in the first part: [Erpichini.pdf](https://github.com/iacopoerpichini/AAGM/tree/main/Erpichini.pdf).

<img src="https://github.com/iacopoerpichini/AAGM/blob/master/img/italia.jpg" height="400" width="600">

## Requirments

+ Python 3.7 and Jupiter Notebook
+ install pandas: `pip install pandas`
+ install geopandas: `pip install geopandas`
+ install networkX: `pip install networkx`
+ install matplotlib: `pip install matplotlib`

## Code structure

The code of the first project is divided into three files but a single file called Erpichini.py will also be provided for the assignment.
The three files .py are stucured as follow:
+ `test.py` file contains all the function calls and their outputs, there is also the calculation of the execution time of each function
+ `function.py` file contains all the implementations of the two algorithm previously mentioned being analyzed and some comments about the complexity
+ `utils.py` file contains some known functions that have been introduced in class and/or taken from the internet

Build the graph of provinces P using NetworkX based on COVID data and a Random graph R, for both creations are tested two algorithms and evaluate the performance (see the .pdf document). 

<img src="https://github.com/iacopoerpichini/AAGM/blob/master/img/graph_P.png" height="400" width="400"> <img src="https://github.com/iacopoerpichini/AAGM/blob/master/img/graph_R.png" height="400" width="400">

The algorithms analyzed are:
+ [Eulerian Path](https://en.wikipedia.org/wiki/Eulerian_path) (path not passing from the same street twice) in particular the Hierholzer's algorithm ([video for explain Eulerian Path (YouTube)](https://www.youtube.com/watch?v=8MpoO2zA2l4) ) and the networkX implementation.
  Here we can see the application of this algorithm on toy example: [Hierholzer](https://www-m9.ma.tum.de/graph-algorithms/hierholzer/index_en.html#:~:text=The%20basic%20idea%20of%20Hierholzer's,first%20circle%20in%20the%20graph)
+ [Clustering coefficient](https://it.wikipedia.org/wiki/Coefficiente_di_clustering) for each node, in three versions: with a naive method, applying fast list intersection algorithm see at lesson and networkX implementation.


  

## Pandas analysis
Is realized with a Jupyter Notebook

<img src="https://github.com/iacopoerpichini/AAGM/blob/master/img/heatmap.png" height="350" width="10000">

## Testing machine spec
All the test are runned on a machine with this specs:
+ CPU: `Intel® Core™ i7-10750H, # of Cores: 6, # of Threads: 12, up to 5.00 GHz`
+ RAM: `2x8 Gb DDR4 2666 MHz`
+ OS: `Ubuntu 20.04.1 LTS`


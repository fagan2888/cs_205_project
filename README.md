## TRACKING GALAXIES OVER TIME

### Introduction

Over the course of time from the Big Bang until present-day, galaxies have been continuously evolving - into the state we all see now and ever-changing. Astronomers have made understanding galaxy formation and evolution possible by building large simulations of sections of the universe: we can “carve out” a part of the universe and record various aspects of the particles of interest within and continue for a period of time. By mapping the properties of these particles to 3-dimensional space, we can visualize the behavior of our galaxies of interest. Some of these complicated features include magnetic fields, gas cooling, black holes, and supernovas. These simulations serve as an important building block to unveil the mysteries of the universe.

At the center of every galaxy is a supermassive black hole which grows through swallowing nearby gas and by merging with other black holes. This black hole can inject energy and momentum back into the gas around it, and is therefore integral to the formation and evolution of galaxies.

For our project, we followed the behavior of gas particles before they fall into black holes using particle data over time snapshots stored as hdf5 files. In order to do this, we utilized the tracer particles present in the simulation. These tracer particles track the transfer of mass between different particle types (e.g. gas converted into stars or gas converted into black holes). Each tracer is associated with a parent cell (either gas, star, or black hole), but the tracer can change which parent it is associated with between each snapshot according to the underlying physics of the simulation.

For each of the sections (referred to as boxes) we are interested in, we made a movie out of the snapshots containing the positions and masses of the associated particles. The boxes are variable in size, with the largest being 300 Mpc in distance. The smaller boxes - or subboxes - are subsections of the large boxes.

<font color='red'>pics for the boxes</font>

The size and number of snapshots also vary across boxes and subboxes, as shown in the table below:

Size | TNG50 | TNG100 | TNG300
:---: | :---: | :---: | :---:
Snapshot size (up to) | 2.7 TB | 1.7 TB | 4.1 TB
Total size | 320 TB | 73 TB | 201.5 TB
Subbox snapshot (up to) | NA | 8.9 GB (~8,000 snapshots) | 20.5 GB (~2,500 snapshots)
Subbox total size (up to) | NA | 41 TB | 19.6 TB

In addition to the three boxes, each box has three resolution levels. We focused on the TNG100 box and the two lowest resolution levels (TNG100-3 and TNG100-2). Because of time constraints we were not able to test our pipeline on the highest resolution (TNG100-1).

The need for efficient big data processing becomes obvious as we aim to analyze the evolution of a small region in the universe over a long period of time. Each box usually consists of thousands to hundreds of thousands of galaxies, and each galaxy is resolved with up to tens of thousands resolution elements. Normally, we are only interested in a small region of the simulation, so we need to locate our particles of interest from a huge list and access and store their properties with ease. Additionally, visualization of the galaxies is compute-intensive.

### Methods

To create the simulations from the snapshot files, we processed the snapshots using the Amazon EMR framework and visualized the results taking advantage of CPU computing on Cannon.

<font color='red'>picture for overall workflow</font>

Specifically, we took the following steps:

1. Upload snapshot files from Cannon to AWS S3 buckets.

2. Generate a list of snapshot files from which to search for particleIDs of interest. In our case, this consists of all of the snapshots with their complete paths.

3. After a galaxy of interest and its corresponding supermassive black hole was identified by hand, we generated particles of interest in two ways:

a. we identified all gas cells that were within a certain radius of that galaxy at each snapshot

b. At the final snapshot we identified all tracer particles associated with the central blackhole. Then, at each previous snapshot we identified the position of those tracer particles whether they are associated black holes, gas, or stars.

4. At each snapshot, the positions, masses, and densities for both 3a and 3b were saved.

5. Post-process for visualization using OpenMP implemented in python through pymp. <font color='red'>Particles mass distribution</font>

6. Create movie for simulation using FuncAnimation from matplotlib.

### Data

We used the Illustris TNG dataset, which is stored on Cannon as /n/hernquistfs3/IllustrisTNG. If you have a Cannon userid, access can be obtained by filling out a request form here.

Below is a simple schematic demonstrating the file and data organization:

<font color='red'>flowchart of data structure</font>

Data for each box is stored under a subdirectory called Runs. The directory name for the boxes is an alphanumeric string that takes the form of L_n_TNG, where

L is box size

N is number of particles/resolution cubed

(so a directory with the name L205n1250TNG means that the box size is 205 Mpc with 1,250 particles3)

Within each box’s directory, the snapshot hdf5 files are stored in their respective snapshot directories starting with snapdir. Each file contains two layers in hierarchical order:

Layer 1: headers specifying particle types

Layer 2: properties of the particles

Note: not every snapshot contains all of the particle types, and not every particle has all of the properties

### Parallel application

Our application uses a single program, multiple data (SPMD) execution model that distributes tasks and simultaneously runs them on multiple processors and nodes. We took advantage of functional parallelism (task parallelism), decomposing the problem into smaller tasks and assigning these to the processors. We executed our model at the loop level, as the majority of our tasks consists of iterating through large lists of files as well as through lines of individual files.

### Programming models

* Our application uses a hybrid programming model consisting of Spark and OpenMP to address the big data and big compute problems, respectively.
Spark: the generation, location, and query of our particleIDs of interest is a repetitive process that searches through the files and outputs each particle’s properties we need to create the simulation. The Spark framework partitions the data into RDDs and operates on them in a parallel fashion, writing outputs only when we need them, which greatly reduces storage and runtime.

* OpenMP: to make a movie using the particle properties obtained using Spark, we need to do a significant amount of post-processing of the results. In addition to the binning, we also found that applying a Gaussian smoothing filter to the particle data was necessary in order to make the visualization look nice. We implemented the binning and smoothing function in C and exposed this procedure to python using the ctypes library. This function was applied to each snapshot, which we also parallelized through OpenMP using the pymp library. This procedure was implemented on Cannon.

### Platform and infrastructure

* AWS S3 buckets for data storage
* EMR for Spark implementation
* Cannon for OpenMP and high-performance computing


```markdown
Syntax highlighted code block

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).

### Jekyll Themes

Your Pages site will use the layout and styles from the Jekyll theme you have selected in your [repository settings](https://github.com/jenliketen/cs_205_project/settings). The name of this theme is saved in the Jekyll `_config.yml` configuration file.

### Support or Contact

Having trouble with Pages? Check out our [documentation](https://help.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.

## TRACKING GALAXIES OVER TIME

### Introduction

Over the course of time from the Big Bang until present-day, galaxies have been continuously evolving - into the state we all see now and ever-changing. Astronomers have made understanding galaxy formation and evolution possible by building large simulations of sections of the universe: we can “carve out” a part of the universe and record various aspects of the particles of interest within and continue for a period of time. By mapping the properties of these particles to 3-dimensional space, we can visualize the behavior of our galaxies of interest. Some of these complicated features include magnetic fields, gas cooling, black holes, and supernovas. These simulations serve as an important building block to unveil the mysteries of the universe.

At the center of every galaxy is a supermassive black hole which grows through swallowing nearby gas and by merging with other black holes. This black hole can inject energy and momentum back into the gas around it, and is therefore integral to the formation and evolution of galaxies.

For our project, we followed the behavior of gas particles before they fall into black holes using particle data over time snapshots stored as hdf5 files. In order to do this, we utilized the tracer particles present in the simulation. These tracer particles track the transfer of mass between different particle types (e.g. gas converted into stars or gas converted into black holes). Each tracer is associated with a parent cell (either gas, star, or black hole), but the tracer can change which parent it is associated with between each snapshot according to the underlying physics of the simulation.

For each of the sections (referred to as boxes) we are interested in, we made a movie out of the snapshots containing the positions and masses of the associated particles. The boxes are variable in size, with the largest being 300 Mpc in distance. The smaller boxes - or subboxes - are subsections of the large boxes. The size and number of snapshots also vary across boxes and subboxes, as shown in the table below:

Size | TNG50 | TNG100 | TNG300
:---: | :---: | :---: | :---:
Snapshot size (up to) | 2.7 TB | 1.7 TB | 4.1 TB
Total size | 320 TB | 73 TB | 201.5 TB
Subbox snapshot (up to) | NA | 8.9 GB (~8,000 snapshots) | 20.5 GB (~2,500 snapshots)
Subbox total size (up to) | NA | 41 TB | 19.6 TB

In addition to the three boxes, each box has three resolution levels. We focused on the TNG100 box and the two lowest resolution levels (TNG100-3 and TNG100-2). Because of time constraints we were not able to test our pipeline on the highest resolution (TNG100-1).

The need for efficient big data processing becomes obvious as we aim to analyze the evolution of a small region in the universe over a long period of time. Each box usually consists of thousands to hundreds of thousands of galaxies, and each galaxy is resolved with up to tens of thousands resolution elements. Normally, we are only interested in a small region of the simulation, so we need to locate our particles of interest from a huge list and access and store their properties with ease. Additionally, visualization of the galaxies is compute-intensive.

### Methods

To create the simulations from the snapshot files, we processed the snapshots using the Amazon EMR framework and visualized the results taking advantage of CPU and GPU computing on Cannon. Specifically, we took the following steps:

1. Upload snapshot files from Cannon to AWS S3 buckets.

2. Generate a list of snapshot files from which to search for particleIDs of interest. In our case, this consists of all of the snapshots with their complete paths.

3. Generate particleIDs of interest by locating particles within a specified radius <font color='red'>(more physics here?)</font>

&nbsp;&nbsp;&nbsp;&nbsp;* Gas particles

&nbsp;&nbsp;&nbsp;&nbsp;* Blackhole particles

&nbsp;&nbsp;&nbsp;&nbsp;* Tracer particles (we cannot directly track the properties of gas particles, so we assign a unique tracer particle to each gas particle and track these instead)

&nbsp;&nbsp;&nbsp;&nbsp;* Blackhole tracer particles


4. Locate the particleIDs generated in Step 3 in the snapshot files generated in Step 1 using Spark.

5. Access and store the coordinates and masses (if applicable) of the particles for post-processing.

6. Post-process for visualization using OpenMP. <font color='red'>Add more info here.</font>

7. Create movie for simulation.



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
